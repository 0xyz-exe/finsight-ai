from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import date

class ImportJobCreate(BaseModel):
    account_id: UUID
    filename: str

class ColumnMapping(BaseModel):
    date_column: str
    description_column: str
    amount_column: Optional[str] = None
    debit_column: Optional[str] = None
    credit_column: Optional[str] = None
    category_column: Optional[str] = None
    
class ImportPreviewRequest(BaseModel):
    column_mapping: ColumnMapping
    date_format: str = Field(default="YYYY-MM-DD", pattern="^(YYYY-MM-DD|DD/MM/YYYY|MM/DD/YYYY)$")
    decimal_separator: str = Field(default=".", pattern="^[.,]$")

class TransactionPreview(BaseModel):
    row_number: int
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[str] = None
    category: Optional[str] = None
    status: str  # 'valid', 'warning', 'error'
    errors: List[str] = []
    is_duplicate_candidate: bool = False
    duplicate_match_id: Optional[UUID] = None

class ImportPreviewResponse(BaseModel):
    job_id: UUID
    total_rows: int
    valid_rows: int
    warning_rows: int
    error_rows: int
    previews: List[TransactionPreview]

class ImportConfirmRequest(BaseModel):
    row_numbers: List[int]  # Which rows to import

class ImportConfirmResponse(BaseModel):
    imported_count: int
    skipped_count: int
    error_count: int
