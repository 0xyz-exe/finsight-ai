from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer, Text, JSON, func
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base, GUID

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(GUID(), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(Text)  # Temp storage path
    status = Column(String(20), nullable=False, default="uploaded")  # uploaded, previewed, confirmed, failed
    column_mapping = Column(JSON().with_variant(JSONB(), "postgresql"))
    total_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    skipped_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    preview_data = Column(JSON().with_variant(JSONB(), "postgresql"))  # Cached preview results
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
