from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import os
from ..database import get_db
from ..schemas.import_job import (
    ImportJobCreate, ImportPreviewRequest, ImportPreviewResponse,
    ImportConfirmRequest, ImportConfirmResponse, TransactionPreview
)
from ..services.import_service import (
    create_import_job, process_csv_preview, confirm_import
)

router = APIRouter(prefix="/imports", tags=["imports"])

TEMP_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=201)
async def upload_csv(
    account_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload CSV file and create import job."""
    
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE/1024/1024}MB)")
    
    # Create import job
    job_id = uuid4()
    filepath = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    
    with open(filepath, 'wb') as f:
        f.write(content)
    
    job = create_import_job(
        db=db,
        job_id=job_id,
        workspace_id=TEMP_WORKSPACE_ID,
        account_id=account_id,
        filename=file.filename,
        filepath=filepath,
    )
    
    return {
        "job_id": str(job.id),
        "filename": job.filename,
        "status": job.status,
    }

@router.post("/preview/{job_id}", response_model=ImportPreviewResponse)
def preview_import(
    job_id: UUID,
    request: ImportPreviewRequest,
    db: Session = Depends(get_db)
):
    """Preview CSV import with validation."""
    
    result = process_csv_preview(
        db=db,
        job_id=job_id,
        workspace_id=TEMP_WORKSPACE_ID,
        column_mapping=request.column_mapping,
        date_format=request.date_format,
        decimal_separator=request.decimal_separator,
    )
    
    return result

@router.post("/confirm/{job_id}", response_model=ImportConfirmResponse)
def confirm_csv_import(
    job_id: UUID,
    request: ImportConfirmRequest,
    db: Session = Depends(get_db)
):
    """Confirm import of selected rows."""
    
    result = confirm_import(
        db=db,
        job_id=job_id,
        workspace_id=TEMP_WORKSPACE_ID,
        row_numbers=request.row_numbers,
    )
    
    return result

@router.get("/jobs")
def list_import_jobs(db: Session = Depends(get_db)):
    """List recent import jobs."""
    from ..models.import_job import ImportJob
    
    jobs = db.query(ImportJob).filter(
        ImportJob.workspace_id == TEMP_WORKSPACE_ID
    ).order_by(ImportJob.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": str(job.id),
            "filename": job.filename,
            "status": job.status,
            "total_rows": job.total_rows,
            "imported_rows": job.imported_rows,
            "created_at": job.created_at.isoformat(),
        }
        for job in jobs
    ]
