from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from ..database import Base

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(Text)  # Temp storage path
    status = Column(String(20), nullable=False, default="uploaded")  # uploaded, previewed, confirmed, failed
    column_mapping = Column(JSONB)
    total_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    skipped_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    preview_data = Column(JSONB)  # Cached preview results
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
