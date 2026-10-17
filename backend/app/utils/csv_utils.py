import csv
import io
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from uuid import UUID

def parse_csv_file(file_content: bytes, encoding: str = 'utf-8') -> List[Dict[str, str]]:
    """Parse CSV file content into list of dicts."""
    try:
        text = file_content.decode(encoding)
    except UnicodeDecodeError:
        # Try common encodings
        for enc in ['utf-8-sig', 'latin-1', 'cp1252']:
            try:
                text = file_content.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Unable to decode file. Please ensure it's UTF-8 encoded.")
    
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        rows.append(row)
    
    return rows

def parse_date(date_str: str, date_format: str) -> Optional[date]:
    """Parse date string according to format."""
    formats = {
        'YYYY-MM-DD': '%Y-%m-%d',
        'DD/MM/YYYY': '%d/%m/%Y',
        'MM/DD/YYYY': '%m/%d/%Y',
    }
    
    fmt = formats.get(date_format)
    if not fmt:
        return None
    
    try:
        return datetime.strptime(date_str.strip(), fmt).date()
    except (ValueError, AttributeError):
        return None

def parse_amount(amount_str: str, decimal_separator: str = '.') -> Optional[Decimal]:
    """Parse amount string to Decimal."""
    if not amount_str:
        return None
    
    # Clean common formatting
    cleaned = amount_str.strip().replace(' ', '').replace(',', '')
    
    # Handle different decimal separators
    if decimal_separator == ',':
        cleaned = cleaned.replace('.', '').replace(',', '.')
    
    # Remove currency symbols
    cleaned = ''.join(c for c in cleaned if c.isdigit() or c in '.-')
    
    try:
        amount = Decimal(cleaned)
        return abs(amount)  # Always positive
    except (InvalidOperation, ValueError):
        return None

def detect_duplicate(
    description: str,
    amount: Decimal,
    transaction_date: date,
    existing_transactions: List[Dict],
) -> Tuple[bool, Optional[UUID]]:
    """Detect if transaction is likely a duplicate."""
    for txn in existing_transactions:
        # Match on same date + amount + similar description
        if (txn['transaction_date'] == transaction_date and 
            txn['amount'] == amount and
            similarity_score(description, txn['description']) > 0.8):
            return True, txn['id']
    
    return False, None

def similarity_score(s1: str, s2: str) -> float:
    """Simple string similarity (case-insensitive)."""
    if not s1 or not s2:
        return 0.0
    
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    
    if s1 == s2:
        return 1.0
    
    # Simple containment check
    if s1 in s2 or s2 in s1:
        return 0.9
    
    # Word overlap
    words1 = set(s1.split())
    words2 = set(s2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0

def escape_csv_formula(value: str) -> str:
    """Escape potential formula injection in CSV exports."""
    if not value:
        return value
    
    if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + value
    
    return value
