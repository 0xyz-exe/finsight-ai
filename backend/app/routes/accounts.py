from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.account import Account
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])

# ponytail: No auth yet; add current_user dependency post-MVP
TEMP_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

@router.post("", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = Account(
        workspace_id=TEMP_WORKSPACE_ID,
        name=account.name,
        account_type=account.account_type,
        currency=account.currency,
        initial_balance=account.initial_balance,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).filter(
        Account.workspace_id == TEMP_WORKSPACE_ID,
        Account.archived_at == None
    ).all()

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db)):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.workspace_id == TEMP_WORKSPACE_ID
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: UUID, updates: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.workspace_id == TEMP_WORKSPACE_ID
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if updates.name is not None:
        account.name = updates.name
    if updates.account_type is not None:
        account.account_type = updates.account_type
    
    db.commit()
    db.refresh(account)
    return account

@router.delete("/{account_id}", status_code=204)
def archive_account(account_id: UUID, db: Session = Depends(get_db)):
    from datetime import datetime
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.workspace_id == TEMP_WORKSPACE_ID
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.archived_at = datetime.now()
    db.commit()
    return None
