from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date
from uuid import UUID
from typing import Optional

class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    account_type: str = Field(..., pattern="^(cash|bank|savings|business)$")
    currency: str = Field(default="IDR", pattern="^[A-Z]{3}$")
    initial_balance: Decimal = Field(default=Decimal("0.00"))

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_type: Optional[str] = Field(None, pattern="^(cash|bank|savings|business)$")

class AccountResponse(AccountBase):
    id: UUID
    workspace_id: UUID
    archived_at: Optional[date] = None
    
    class Config:
        from_attributes = True
