from decimal import Decimal, ROUND_HALF_EVEN

def round_currency(amount: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

def to_decimal(value: str | int | float) -> Decimal:
    """Convert to Decimal safely."""
    return Decimal(str(value))
