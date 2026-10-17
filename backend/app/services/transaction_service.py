from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from ..models.transaction import Transaction
from ..models.account import Account

def create_transfer(
    db: Session,
    workspace_id: UUID,
    source_account_id: UUID,
    destination_account_id: UUID,
    amount: Decimal,
    transaction_date,
    description: str = "",
) -> tuple[Transaction, Transaction]:
    """Create two linked transactions for a transfer."""
    
    if source_account_id == destination_account_id:
        raise ValueError("Cannot transfer to same account")
    
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    # Verify both accounts exist and belong to workspace
    source = db.query(Account).filter(
        Account.id == source_account_id,
        Account.workspace_id == workspace_id,
        Account.archived_at == None
    ).first()
    
    dest = db.query(Account).filter(
        Account.id == destination_account_id,
        Account.workspace_id == workspace_id,
        Account.archived_at == None
    ).first()
    
    if not source:
        raise ValueError("Source account not found")
    if not dest:
        raise ValueError("Destination account not found")
    
    # Source transaction (outgoing)
    source_txn = Transaction(
        workspace_id=workspace_id,
        account_id=source_account_id,
        transaction_type="transfer",
        amount=amount,
        transaction_date=transaction_date,
        description=description or f"Transfer to {dest.name}",
        transfer_to_account_id=destination_account_id,
        category_id=None,
    )
    db.add(source_txn)
    db.flush()
    
    # Destination transaction (incoming)
    dest_txn = Transaction(
        workspace_id=workspace_id,
        account_id=destination_account_id,
        transaction_type="transfer",
        amount=amount,
        transaction_date=transaction_date,
        description=description or f"Transfer from {source.name}",
        transfer_to_account_id=source_account_id,
        transfer_pair_id=source_txn.id,
        category_id=None,
    )
    db.add(dest_txn)
    db.flush()
    
    # Link back
    source_txn.transfer_pair_id = dest_txn.id
    
    return source_txn, dest_txn
