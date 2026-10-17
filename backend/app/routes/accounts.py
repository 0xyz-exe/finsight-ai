from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.account import Account
from ..models.user import User
from ..models.workspace import Workspace
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = db.query(Workspace).filter(Workspace.owner_id == current_user.id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="No workspace found")
    
    db_account = Account(
        workspace_id=workspace.id,
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
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace_ids = [w.id for w in db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()]
    return db.query(Account).filter(
        Account.workspace_id.in_(workspace_ids),
        Account.archived_at == None
    ).all()

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return account

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: UUID,
    updates: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if updates.name is not None:
        account.name = updates.name
    if updates.account_type is not None:
        account.account_type = updates.account_type
    
    db.commit()
    db.refresh(account)
    return account

@router.delete("/{account_id}", status_code=204)
def archive_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    account.archived_at = datetime.now()
    db.commit()
    return None
