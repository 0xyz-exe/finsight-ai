from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, NUMERIC, func, CheckConstraint, UniqueConstraint
import uuid
from ..database import Base, GUID

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_type = Column(String(20), nullable=False)  # 'cash', 'bank', 'savings', 'business'
    currency = Column(String(3), default="IDR")
    initial_balance = Column(NUMERIC(19, 2), default=0.00)
    archived_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_workspace_account_name'),
        CheckConstraint("account_type IN ('cash', 'bank', 'savings', 'business')", name='check_account_type'),
    )
