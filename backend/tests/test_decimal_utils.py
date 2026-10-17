from decimal import Decimal
import pytest
from app.utils.decimal_utils import round_currency, to_decimal

def test_round_currency_half_even():
    assert round_currency(Decimal("1.234")) == Decimal("1.23")
    assert round_currency(Decimal("1.235")) == Decimal("1.24")  # Round up
    assert round_currency(Decimal("1.245")) == Decimal("1.24")  # Banker's rounding (even)
    assert round_currency(Decimal("1.255")) == Decimal("1.26")  # Banker's rounding (even)

def test_round_currency_negative():
    assert round_currency(Decimal("-1.234")) == Decimal("-1.23")
    assert round_currency(Decimal("-1.235")) == Decimal("-1.24")

def test_to_decimal_from_string():
    assert to_decimal("100.50") == Decimal("100.50")
    assert to_decimal("0.1") == Decimal("0.1")

def test_to_decimal_from_int():
    assert to_decimal(100) == Decimal("100")

def test_to_decimal_from_float():
    # Float converted via string to avoid precision issues
    assert to_decimal(100.5) == Decimal("100.5")

def test_decimal_addition_precision():
    a = Decimal("0.1")
    b = Decimal("0.2")
    assert a + b == Decimal("0.3")  # Exact, unlike float

def test_decimal_no_float_error():
    # Verify Decimal avoids float issues
    result = Decimal("1000.50") + Decimal("2000.75")
    assert result == Decimal("3001.25")
    assert str(result) == "3001.25"
