from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.transaction import Transaction
from ..schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])

TEMP_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    from ..services.transaction_service import create_transfer
    
    if txn.transaction_type == "transfer":
        if not txn.transfer_to_account_id:
            raise HTTPException(status_code=400, detail="transfer_to_account_id required for transfers")
        
        try:
            source_txn, dest_txn = create_transfer(
                db=db,
                workspace_id=TEMP_WORKSPACE_ID,
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
    
    if txn.transaction_type in ("income", "expense") and not txn.category_id:
        raise HTTPException(status_code=400, detail="Category required for income/expense")
    
    db_txn = Transaction(
        workspace_id=TEMP_WORKSPACE_ID,
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
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        Transaction.workspace_id == TEMP_WORKSPACE_ID
    ).order_by(Transaction.transaction_date.desc()).limit(50).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.workspace_id == TEMP_WORKSPACE_ID
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: UUID, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.workspace_id == TEMP_WORKSPACE_ID
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(txn)
    db.commit()
    return None
