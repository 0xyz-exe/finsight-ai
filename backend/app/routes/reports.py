from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from ..database import get_db
from ..services.report_service import calculate_account_balance, calculate_period_summary
from ..models.account import Account
from ..models.user import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/balance/{account_id}")
def get_balance(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current balance for account."""
    
    # Verify account ownership
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    from ..models.workspace import Workspace
    workspace = db.query(Workspace).filter(
        Workspace.id == account.workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=403, detail="Access denied")
    
    balance = calculate_account_balance(db, account_id)
    return {"account_id": str(account_id), "balance": str(balance)}

@router.get("/summary")
def get_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get period summary for current user's workspaces."""
    
    # Get user's workspaces
    from ..models.workspace import Workspace
    workspace_ids = [w.id for w in db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()]
    
    if not workspace_ids:
        return {
            "income": "0",
            "expense": "0",
            "net": "0",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
    
    summary = calculate_period_summary(db, workspace_ids[0], start_date, end_date)
    return {
        "income": str(summary["income"]),
        "expense": str(summary["expense"]),
        "net": str(summary["net"]),
        "start_date": summary["start_date"].isoformat(),
        "end_date": summary["end_date"].isoformat(),
    }
