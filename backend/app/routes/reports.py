from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from ..database import get_db
from ..services.report_service import calculate_account_balance, calculate_period_summary

router = APIRouter(prefix="/reports", tags=["reports"])

TEMP_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"

@router.get("/balance/{account_id}")
def get_account_balance(account_id: UUID, db: Session = Depends(get_db)):
    balance = calculate_account_balance(db, account_id, TEMP_WORKSPACE_ID)
    return {"account_id": str(account_id), "balance": str(balance)}

@router.get("/summary")
def get_period_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    summary = calculate_period_summary(db, TEMP_WORKSPACE_ID, start_date, end_date)
    return {
        "income": str(summary["income"]),
        "expense": str(summary["expense"]),
        "net": str(summary["net"]),
        "start_date": summary["start_date"].isoformat(),
        "end_date": summary["end_date"].isoformat(),
    }
