from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date
from uuid import UUID
from typing import Optional

class TransactionBase(BaseModel):
    transaction_type: str = Field(..., pattern="^(income|expense|transfer)$")
    amount: Decimal = Field(..., gt=0)
    transaction_date: date
    description: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransactionCreate(TransactionBase):
    account_id: UUID
    category_id: Optional[UUID] = None
    transfer_to_account_id: Optional[UUID] = None

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    transaction_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = None
    category_id: Optional[UUID] = None

class TransactionResponse(TransactionBase):
    id: UUID
    workspace_id: UUID
    account_id: UUID
    category_id: Optional[UUID] = None
    transfer_to_account_id: Optional[UUID] = None
    transfer_pair_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True
