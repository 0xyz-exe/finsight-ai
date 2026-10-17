from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, func
import uuid
from ..database import Base, GUID

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    mode = Column(String(20), nullable=False, default="personal")
    currency = Column(String(3), nullable=False, default="IDR")
    timezone = Column(String(50), nullable=False, default="Asia/Jakarta")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
