import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Account, Transaction, Workspace
from app.services.transaction_service import create_transfer

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    # Create test workspace
    workspace = Workspace(
        id="00000000-0000-0000-0000-000000000001",
        name="Test Workspace",
        mode="personal",
    )
    db.add(workspace)
    db.commit()
    
    yield db
    db.close()

def test_create_transfer_success(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    # Create accounts
    acc1 = Account(workspace_id=workspace_id, name="Cash", account_type="cash", initial_balance=Decimal("1000.00"))
    acc2 = Account(workspace_id=workspace_id, name="Bank", account_type="bank", initial_balance=Decimal("0.00"))
    db.add(acc1)
    db.add(acc2)
    db.commit()
    
    # Create transfer
    source_txn, dest_txn = create_transfer(
        db=db,
        workspace_id=workspace_id,
        source_account_id=acc1.id,
        destination_account_id=acc2.id,
        amount=Decimal("100.00"),
        transaction_date=date(2026, 10, 17),
        description="Test transfer"
    )
    db.commit()
    
    assert source_txn.transaction_type == "transfer"
    assert source_txn.amount == Decimal("100.00")
    assert source_txn.account_id == acc1.id
    assert source_txn.transfer_to_account_id == acc2.id
    assert source_txn.transfer_pair_id == dest_txn.id
    
    assert dest_txn.transaction_type == "transfer"
    assert dest_txn.amount == Decimal("100.00")
    assert dest_txn.account_id == acc2.id
    assert dest_txn.transfer_to_account_id == acc1.id
    assert dest_txn.transfer_pair_id == source_txn.id

def test_create_transfer_same_account(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc = Account(workspace_id=workspace_id, name="Cash", account_type="cash")
    db.add(acc)
    db.commit()
    
    with pytest.raises(ValueError, match="Cannot transfer to same account"):
        create_transfer(
            db=db,
            workspace_id=workspace_id,
            source_account_id=acc.id,
            destination_account_id=acc.id,
            amount=Decimal("100.00"),
            transaction_date=date(2026, 10, 17),
        )

def test_create_transfer_negative_amount(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc1 = Account(workspace_id=workspace_id, name="Cash", account_type="cash")
    acc2 = Account(workspace_id=workspace_id, name="Bank", account_type="bank")
    db.add(acc1)
    db.add(acc2)
    db.commit()
    
    with pytest.raises(ValueError, match="Amount must be positive"):
        create_transfer(
            db=db,
            workspace_id=workspace_id,
            source_account_id=acc1.id,
            destination_account_id=acc2.id,
            amount=Decimal("-100.00"),
            transaction_date=date(2026, 10, 17),
        )

def test_create_transfer_nonexistent_account(db):
    workspace_id = "00000000-0000-0000-0000-000000000001"
    
    acc = Account(workspace_id=workspace_id, name="Cash", account_type="cash")
    db.add(acc)
    db.commit()
    
    fake_id = "99999999-9999-9999-9999-999999999999"
    
    with pytest.raises(ValueError, match="account not found"):
        create_transfer(
            db=db,
            workspace_id=workspace_id,
            source_account_id=acc.id,
            destination_account_id=fake_id,
            amount=Decimal("100.00"),
            transaction_date=date(2026, 10, 17),
        )
