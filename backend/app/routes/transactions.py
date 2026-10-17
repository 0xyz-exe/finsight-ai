from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.transaction import Transaction
from ..models.account import Account
from ..models.workspace import Workspace
from ..models.user import User
from ..schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    txn: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == txn.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    from ..services.transaction_service import create_transfer
    
    if txn.transaction_type == "transfer":
        if not txn.transfer_to_account_id:
            raise HTTPException(status_code=400, detail="transfer_to_account_id required")
        
        try:
            source_txn, dest_txn = create_transfer(
                db=db,
                workspace_id=account.workspace_id,
                source_account_id=txn.account_id,
                destination_account_id=txn.transfer_to_account_id,
                amount=txn.amount,
                transaction_date=txn.transaction_date,
                description=txn.description or "",
            )
            db.commit()
            return source_txn
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    db_txn = Transaction(
        workspace_id=account.workspace_id,
        account_id=txn.account_id,
        category_id=txn.category_id,
        transaction_type=txn.transaction_type,
        amount=txn.amount,
        transaction_date=txn.transaction_date,
        description=txn.description,
        notes=txn.notes,
    )
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace_ids = [w.id for w in db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()]
    return db.query(Transaction).filter(
        Transaction.workspace_id.in_(workspace_ids)
    ).order_by(Transaction.transaction_date.desc()).limit(50).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == txn.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return txn

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == txn.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(txn)
    db.commit()
    return None
