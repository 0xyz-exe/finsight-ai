import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Account, Transaction, Workspace, Category
from app.services.report_service import calculate_account_balance, calculate_period_summary

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    workspace = Workspace(
        id="00000000-0000-0000-0000-000000000001",
        name="Test",
        mode="personal",
    )
    db.add(workspace)
    db.commit()
    
    yield db
    db.close()

def test_calculate_balance_with_income_and_expense(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc = Account(workspace_id=workspace_id, name="Cash", account_type="cash", initial_balance=Decimal("1000.00"))
    cat = Category(workspace_id=workspace_id, name="Salary", category_type="income")
    db.add(acc)
    db.add(cat)
    db.commit()
    
    # Income
    t1 = Transaction(
        workspace_id=workspace_id,
        account_id=acc.id,
        category_id=cat.id,
        transaction_type="income",
        amount=Decimal("500.00"),
        transaction_date=date(2026, 10, 1)
    )
    # Expense
    t2 = Transaction(
        workspace_id=workspace_id,
        account_id=acc.id,
        category_id=cat.id,
        transaction_type="expense",
        amount=Decimal("200.00"),
        transaction_date=date(2026, 10, 2)
    )
    db.add(t1)
    db.add(t2)
    db.commit()
    
    balance = calculate_account_balance(db, acc.id, workspace_id)
    assert balance == Decimal("1300.00")  # 1000 + 500 - 200

def test_calculate_balance_with_transfer(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc1 = Account(workspace_id=workspace_id, name="Cash", account_type="cash", initial_balance=Decimal("1000.00"))
    acc2 = Account(workspace_id=workspace_id, name="Bank", account_type="bank", initial_balance=Decimal("0.00"))
    db.add(acc1)
    db.add(acc2)
    db.commit()
    
    # Transfer from acc1 to acc2
    t_out = Transaction(
        workspace_id=workspace_id,
        account_id=acc1.id,
        transaction_type="transfer",
        amount=Decimal("300.00"),
        transaction_date=date(2026, 10, 1),
        transfer_to_account_id=acc2.id,
    )
    db.add(t_out)
    db.flush()
    
    t_in = Transaction(
        workspace_id=workspace_id,
        account_id=acc2.id,
        transaction_type="transfer",
        amount=Decimal("300.00"),
        transaction_date=date(2026, 10, 1),
        transfer_to_account_id=acc1.id,
        transfer_pair_id=t_out.id,
    )
    db.add(t_in)
    t_out.transfer_pair_id = t_in.id
    db.commit()
    
    balance1 = calculate_account_balance(db, acc1.id, workspace_id)
    balance2 = calculate_account_balance(db, acc2.id, workspace_id)
    
    assert balance1 == Decimal("700.00")   # 1000 - 300
    assert balance2 == Decimal("300.00")   # 0 + 300

def test_period_summary_excludes_transfers(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc = Account(workspace_id=workspace_id, name="Cash", account_type="cash")
    cat = Category(workspace_id=workspace_id, name="Salary", category_type="income")
    db.add(acc)
    db.add(cat)
    db.commit()
    
    # Income
    t1 = Transaction(
        workspace_id=workspace_id,
        account_id=acc.id,
        category_id=cat.id,
        transaction_type="income",
        amount=Decimal("1000.00"),
        transaction_date=date(2026, 10, 1)
    )
    # Transfer (should NOT count as income)
    t2 = Transaction(
        workspace_id=workspace_id,
        account_id=acc.id,
        transaction_type="transfer",
        amount=Decimal("500.00"),
        transaction_date=date(2026, 10, 2),
        transfer_to_account_id=acc.id,
    )
    db.add(t1)
    db.add(t2)
    db.commit()
    
    summary = calculate_period_summary(
        db=db,
        workspace_id=workspace_id,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 11, 1),
    )
    
    assert summary["income"] == Decimal("1000.00")  # Only real income
    assert summary["expense"] == Decimal("0.00")
    assert summary["net"] == Decimal("1000.00")
