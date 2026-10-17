from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, NUMERIC, Date, Text, func, CheckConstraint
import uuid
from datetime import datetime, timezone
from ..database import Base, GUID

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(GUID(), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = Column(GUID(), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    transaction_type = Column(String(10), nullable=False)  # 'income', 'expense', 'transfer'
    amount = Column(NUMERIC(19, 2), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    description = Column(Text)
    notes = Column(Text)
    transfer_to_account_id = Column(GUID(), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    transfer_pair_id = Column(GUID(), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=True)
    import_job_id = Column(GUID(), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("transaction_type IN ('income', 'expense', 'transfer')", name='check_transaction_type'),
        CheckConstraint("amount > 0", name='check_positive_amount'),
    )
