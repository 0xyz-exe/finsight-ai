from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID
from datetime import date
from ..models.transaction import Transaction
from ..models.account import Account
from ..utils.decimal_utils import round_currency

def calculate_account_balance(db: Session, account_id: UUID, workspace_id: UUID) -> Decimal:
    """Calculate current balance for an account."""
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.workspace_id == workspace_id
    ).first()
    
    if not account:
        raise ValueError("Account not found")
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).all()
    transaction_sum = Decimal("0")
    for transaction in transactions:
        if transaction.transaction_type == "income":
            transaction_sum += transaction.amount
        elif transaction.transaction_type == "expense":
            transaction_sum -= transaction.amount
        elif transaction.transfer_pair_id:
            pair = db.query(Transaction).filter(
                Transaction.id == transaction.transfer_pair_id
            ).first()
            if pair and transaction.created_at and pair.created_at:
                transaction_sum += transaction.amount if transaction.created_at > pair.created_at else -transaction.amount
        elif transaction.transfer_to_account_id:
            transaction_sum -= transaction.amount

    balance = account.initial_balance + transaction_sum
    
    return round_currency(balance)

def calculate_period_summary(
    db: Session,
    workspace_id: UUID,
    start_date: date,
    end_date: date,
    account_ids: list[UUID] | None = None,
) -> dict:
    """Calculate income, expense, net for period."""
    
    query = db.query(Transaction).filter(
        Transaction.workspace_id == workspace_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date < end_date,
    )
    
    if account_ids:
        query = query.filter(Transaction.account_id.in_(account_ids))
    
    transactions = query.all()
    
    income = sum(
        t.amount for t in transactions if t.transaction_type == "income"
    ) or Decimal("0")
    
    expense = sum(
        t.amount for t in transactions if t.transaction_type == "expense"
    ) or Decimal("0")
    
    net = round_currency(income - expense)
    
    return {
        "income": round_currency(income),
        "expense": round_currency(expense),
        "net": net,
        "start_date": start_date,
        "end_date": end_date,
    }
