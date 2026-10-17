import uuid
from sqlalchemy import CHAR, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator

class GUID(TypeDecorator):
    """Store UUIDs natively in PostgreSQL and as portable strings elsewhere."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        value = value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return value if dialect.name == "postgresql" else str(value)

    def process_result_value(self, value, dialect):
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

Base = declarative_base()

# Lazy initialization to avoid importing config at module level
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        from .config import settings
        _engine = create_engine(settings.database_url)
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
