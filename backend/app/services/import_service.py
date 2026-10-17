from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List, Dict
from ..models.import_job import ImportJob
from ..models.transaction import Transaction
from ..models.account import Account
from ..utils.csv_utils import (
    parse_csv_file, parse_date, parse_amount, detect_duplicate, escape_csv_formula
)
from ..schemas.import_job import (
    ColumnMapping, ImportPreviewResponse, TransactionPreview, ImportConfirmResponse
)

def create_import_job(
    db: Session,
    job_id: UUID,
    workspace_id: UUID,
    account_id: UUID,
    filename: str,
    filepath: str,
) -> ImportJob:
    """Create new import job."""
    
    job = ImportJob(
        id=job_id,
        workspace_id=workspace_id,
        account_id=account_id,
        filename=filename,
        filepath=filepath,
        status="uploaded",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def process_csv_preview(
    db: Session,
    job_id: UUID,
    workspace_id: UUID,
    column_mapping: ColumnMapping,
    date_format: str,
    decimal_separator: str,
) -> ImportPreviewResponse:
    """Parse and validate CSV, return preview."""
    
    job = db.query(ImportJob).filter(ImportJob.id == job_id, ImportJob.workspace_id == workspace_id).first()
    if not job:
        raise ValueError("Import job not found")
    
    # Read CSV
    with open(job.filepath, 'rb') as f:
        content = f.read()
    
    rows = parse_csv_file(content)
    
    # Get existing transactions for duplicate detection
    existing_txns = db.query(Transaction).filter(
        Transaction.workspace_id == workspace_id,
        Transaction.account_id == job.account_id
    ).order_by(Transaction.transaction_date.desc()).limit(1000).all()
    
    existing_data = [
        {
            'id': t.id,
            'transaction_date': t.transaction_date,
            'amount': t.amount,
            'description': t.description or '',
        }
        for t in existing_txns
    ]
    
    # Validate each row
    previews = []
    valid_count = 0
    warning_count = 0
    error_count = 0
    
    for idx, row in enumerate(rows, start=1):
        preview = validate_row(
            row=row,
            row_number=idx,
            column_mapping=column_mapping,
            date_format=date_format,
            decimal_separator=decimal_separator,
            existing_transactions=existing_data,
        )
        
        if preview.status == 'valid':
            valid_count += 1
        elif preview.status == 'warning':
            warning_count += 1
        elif preview.status == 'error':
            error_count += 1
        
        previews.append(preview)
    
    # Update job
    job.status = "previewed"
    job.total_rows = len(rows)
    job.column_mapping = column_mapping.dict()
    job.preview_data = [p.dict() for p in previews]
    db.commit()
    
    return ImportPreviewResponse(
        job_id=job.id,
        total_rows=len(rows),
        valid_rows=valid_count,
        warning_rows=warning_count,
        error_rows=error_count,
        previews=previews,
    )

def validate_row(
    row: Dict[str, str],
    row_number: int,
    column_mapping: ColumnMapping,
    date_format: str,
    decimal_separator: str,
    existing_transactions: List[Dict],
) -> TransactionPreview:
    """Validate single CSV row."""
    
    errors = []
    status = 'valid'
    
    # Parse date
    date_str = row.get(column_mapping.date_column, '')
    txn_date = parse_date(date_str, date_format)
    if not txn_date:
        errors.append(f"Invalid date: {date_str}")
        status = 'error'
    
    # Parse amount
    amount = None
    if column_mapping.amount_column:
        amount_str = row.get(column_mapping.amount_column, '')
        amount = parse_amount(amount_str, decimal_separator)
    elif column_mapping.debit_column or column_mapping.credit_column:
        debit_str = row.get(column_mapping.debit_column or '', '')
        credit_str = row.get(column_mapping.credit_column or '', '')
        
        debit = parse_amount(debit_str, decimal_separator) if debit_str else None
        credit = parse_amount(credit_str, decimal_separator) if credit_str else None
        
        if debit:
            amount = debit
        elif credit:
            amount = credit
    
    if amount is None or amount <= 0:
        errors.append("Invalid or missing amount")
        status = 'error'
    
    # Description
    description = row.get(column_mapping.description_column, '').strip()
    if not description:
        errors.append("Missing description")
        if status != 'error':
            status = 'warning'
    
    # Category (optional)
    category = row.get(column_mapping.category_column, '') if column_mapping.category_column else None
    
    # Duplicate detection
    is_duplicate = False
    duplicate_id = None
    if txn_date and amount and description:
        is_duplicate, duplicate_id = detect_duplicate(description, amount, txn_date, existing_transactions)
        if is_duplicate and status == 'valid':
            status = 'warning'
    
    return TransactionPreview(
        row_number=row_number,
        date=txn_date,
        description=description,
        amount=str(amount) if amount else None,
        category=category,
        status=status,
        errors=errors,
        is_duplicate_candidate=is_duplicate,
        duplicate_match_id=duplicate_id,
    )

def confirm_import(
    db: Session,
    job_id: UUID,
    workspace_id: UUID,
    row_numbers: List[int],
) -> ImportConfirmResponse:
    """Import selected rows as transactions."""
    
    job = db.query(ImportJob).filter(ImportJob.id == job_id, ImportJob.workspace_id == workspace_id).first()
    if not job:
        raise ValueError("Import job not found")
    
    if not job.preview_data:
        raise ValueError("No preview data. Run preview first.")
    
    # Filter to selected rows
    selected = [p for p in job.preview_data if p['row_number'] in row_numbers]
    
    imported = 0
    skipped = 0
    errors = 0
    
    for preview in selected:
        if preview['status'] == 'error':
            errors += 1
            continue
        
        if not preview['date'] or not preview['amount']:
            errors += 1
            continue
        
        # Create transaction
        txn = Transaction(
            workspace_id=workspace_id,
            account_id=job.account_id,
            transaction_type='expense',  # Default; could infer from debit/credit
            amount=preview['amount'],
            transaction_date=preview['date'],
            description=preview['description'],
            import_job_id=job.id,
        )
        db.add(txn)
        imported += 1
    
    try:
        db.commit()
        
        # Update job
        job.status = "confirmed"
        job.imported_rows = imported
        job.skipped_rows = skipped
        job.error_rows = errors
        job.completed_at = datetime.now()
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Import failed: {str(e)}")
    
    return ImportConfirmResponse(
        imported_count=imported,
        skipped_count=skipped,
        error_count=errors,
    )
