from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, func, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category_type = Column(String(10), nullable=False)  # 'income' or 'expense'
    color = Column(String(7), default="#6B7280")
    is_default = Column(Boolean, default=False)
    archived_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', 'category_type', name='uq_workspace_category'),
        CheckConstraint("category_type IN ('income', 'expense')", name='check_category_type'),
    )
