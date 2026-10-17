# Financial Calculations — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Core Principle

**All monetary calculations use decimal-safe arithmetic.** Never binary floating-point for authoritative amounts.

## 2. Data Types

### Backend (Python)
```python
from decimal import Decimal, ROUND_HALF_EVEN

amount = Decimal("1000.50")  # Always string input to avoid float
result = amount + Decimal("2000.75")  # Decimal("3001.25")
```

### Database (PostgreSQL)
```sql
amount NUMERIC(19, 2)  -- 19 digits total, 2 after decimal
-- Max: 999,999,999,999,999.99
```

### Frontend (TypeScript)
```typescript
import Decimal from 'decimal.js';

const amount = new Decimal('1000.50');
const result = amount.plus('2000.75');  // Decimal(3001.25)
```

**Note:** Frontend decimals for display only. Backend is authoritative.

## 3. Rounding Rules

- **Method:** Banker's rounding (ROUND_HALF_EVEN)
- **Display:** Always 2 decimal places for currency
- **Storage:** 2 decimal places in DB
- **Calculation:** Full precision during intermediate steps, round only at display/storage

```python
from decimal import Decimal, ROUND_HALF_EVEN

def round_currency(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
```

## 4. Transaction Types and Balance Impact

### Income
- **Effect:** Increases account balance
- **Amount:** Stored as positive
- **Balance calculation:** `balance + amount`

### Expense
- **Effect:** Decreases account balance
- **Amount:** Stored as positive
- **Balance calculation:** `balance - amount`

### Transfer
- **Effect:** Moves money between accounts
- **Implementation:** Two linked transactions
  - Source account: amount stored positive, subtracted from balance
  - Destination account: amount stored positive, added to balance
- **Link:** `transfer_pair_id` references the paired transaction
- **Category:** NULL (transfers are not income or expense)

## 5. Account Balance Calculation

```python
def calculate_account_balance(
    account_id: UUID,
    initial_balance: Decimal,
    transactions: List[Transaction],
) -> Decimal:
    balance = initial_balance
    
    for t in transactions:
        if t.transaction_type == "income":
            balance += t.amount
        elif t.transaction_type == "expense":
            balance -= t.amount
        elif t.transaction_type == "transfer":
            if t.account_id == account_id:
                # Outgoing transfer
                balance -= t.amount
            elif t.transfer_to_account_id == account_id:
                # Incoming transfer
                balance += t.amount
    
    return round_currency(balance)
```

### SQL Version
```sql
SELECT 
    a.initial_balance +
    COALESCE(SUM(
        CASE 
            WHEN t.transaction_type = 'income' THEN t.amount
            WHEN t.transaction_type = 'expense' THEN -t.amount
            WHEN t.transaction_type = 'transfer' AND t.account_id = a.id THEN -t.amount
            WHEN t.transaction_type = 'transfer' AND t.transfer_to_account_id = a.id THEN t.amount
            ELSE 0
        END
    ), 0) AS current_balance
FROM accounts a
LEFT JOIN transactions t 
    ON t.account_id = a.id OR t.transfer_to_account_id = a.id
WHERE a.id = ?
GROUP BY a.id, a.initial_balance;
```

## 6. Period Summaries

### Total Income (Period)
```python
def calculate_total_income(
    workspace_id: UUID,
    start_date: date,
    end_date: date,
    account_ids: Optional[List[UUID]] = None,
) -> Decimal:
    query = transactions.filter(
        workspace_id=workspace_id,
        transaction_type="income",
        transaction_date >= start_date,
        transaction_date < end_date,  # Exclusive end
    )
    if account_ids:
        query = query.filter(account_id.in_(account_ids))
    
    total = sum(t.amount for t in query) or Decimal("0")
    return round_currency(total)
```

### Total Expenses (Period)
```python
def calculate_total_expenses(
    workspace_id: UUID,
    start_date: date,
    end_date: date,
    account_ids: Optional[List[UUID]] = None,
) -> Decimal:
    query = transactions.filter(
        workspace_id=workspace_id,
        transaction_type="expense",
        transaction_date >= start_date,
        transaction_date < end_date,
    )
    if account_ids:
        query = query.filter(account_id.in_(account_ids))
    
    total = sum(t.amount for t in query) or Decimal("0")
    return round_currency(total)
```

### Net Cash Flow
```python
def calculate_net_cash_flow(
    total_income: Decimal,
    total_expenses: Decimal,
) -> Decimal:
    """Net cash flow = Income - Expenses.
    
    Transfers are excluded (not income or expense).
    """
    return round_currency(total_income - total_expenses)
```

**Critical:** Transfers NOT included in income or expense totals.

## 7. Category Summaries

### Spending by Category
```python
def calculate_category_spending(
    workspace_id: UUID,
    start_date: date,
    end_date: date,
) -> Dict[str, Decimal]:
    """Returns {category_name: total_amount}."""
    
    results = db.query(
        Category.name,
        func.sum(Transaction.amount).label("total")
    ).join(Transaction).filter(
        Transaction.workspace_id == workspace_id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date < end_date,
    ).group_by(Category.name).all()
    
    return {
        name: round_currency(Decimal(str(total)))
        for name, total in results
    }
```

## 8. Budget Calculations

### Budget Utilization
```python
def calculate_budget_utilization(
    budget_amount: Decimal,
    actual_spending: Decimal,
) -> Decimal:
    """Returns percentage: (actual / budget) * 100."""
    
    if budget_amount == 0:
        return Decimal("0")
    
    utilization = (actual_spending / budget_amount) * Decimal("100")
    return utilization.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
```

### Budget Remaining
```python
def calculate_budget_remaining(
    budget_amount: Decimal,
    actual_spending: Decimal,
) -> Decimal:
    return round_currency(budget_amount - actual_spending)
```

## 9. Savings Rate

```python
def calculate_savings_rate(
    total_income: Decimal,
    total_expenses: Decimal,
) -> Decimal:
    """Savings rate = (Income - Expenses) / Income * 100.
    
    Returns percentage. Returns 0 if income is 0.
    """
    if total_income == 0:
        return Decimal("0")
    
    rate = ((total_income - total_expenses) / total_income) * Decimal("100")
    return rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
```

## 10. Date Boundaries

### Period Filtering
- **Start date:** Inclusive (`>=`)
- **End date:** Exclusive (`<`)
- **Example:** "October 2026" = `2026-10-01` to `2026-11-01` (end exclusive)

### Timezone Handling
```python
from zoneinfo import ZoneInfo

def get_period_boundaries(
    year: int,
    month: int,
    timezone: str = "Asia/Jakarta",
) -> Tuple[date, date]:
    """Returns (start_date, end_date) for a month period."""
    tz = ZoneInfo(timezone)
    start = date(year, month, 1)
    
    # End: first day of next month
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    
    return start, end
```

## 11. Transfer Handling

### Creating a Transfer
```python
def create_transfer(
    source_account_id: UUID,
    destination_account_id: UUID,
    amount: Decimal,
    transaction_date: date,
    description: str,
) -> Tuple[Transaction, Transaction]:
    """Creates two linked transactions for a transfer."""
    
    if source_account_id == destination_account_id:
        raise ValueError("Cannot transfer to same account")
    
    if amount <= 0:
        raise ValueError("Transfer amount must be positive")
    
    # Source transaction (outgoing)
    source_txn = Transaction(
        account_id=source_account_id,
        transaction_type="transfer",
        amount=amount,
        transaction_date=transaction_date,
        description=description,
        transfer_to_account_id=destination_account_id,
        category_id=None,
    )
    db.add(source_txn)
    db.flush()  # Get ID
    
    # Destination transaction (incoming)
    dest_txn = Transaction(
        account_id=destination_account_id,
        transaction_type="transfer",
        amount=amount,
        transaction_date=transaction_date,
        description=description,
        transfer_to_account_id=source_account_id,
        transfer_pair_id=source_txn.id,
        category_id=None,
    )
    db.add(dest_txn)
    db.flush()
    
    # Link back
    source_txn.transfer_pair_id = dest_txn.id
    
    db.commit()
    return source_txn, dest_txn
```

## 12. Refunds and Reversals

### Option A: Reverse Transaction
```python
def create_refund(
    original_transaction: Transaction,
    refund_date: date,
) -> Transaction:
    """Creates opposite transaction (income ↔ expense)."""
    
    if original_transaction.transaction_type == "income":
        refund_type = "expense"
    elif original_transaction.transaction_type == "expense":
        refund_type = "income"
    else:
        raise ValueError("Cannot refund a transfer")
    
    refund = Transaction(
        workspace_id=original_transaction.workspace_id,
        account_id=original_transaction.account_id,
        category_id=original_transaction.category_id,
        transaction_type=refund_type,
        amount=original_transaction.amount,
        transaction_date=refund_date,
        description=f"Refund: {original_transaction.description}",
        notes=f"Refund of transaction {original_transaction.id}",
    )
    return refund
```

### Option B: Edit Original Amount
- User edits original transaction to reduce amount
- Simpler if full refund: delete original (with confirmation)

## 13. Common Pitfalls

### ❌ Wrong: Float Arithmetic
```python
amount = 1000.50 + 2000.75  # 3001.25 (may be 3001.2500000001)
```

### ✅ Right: Decimal Arithmetic
```python
amount = Decimal("1000.50") + Decimal("2000.75")  # Exact
```

### ❌ Wrong: Including Transfers in Income
```python
total_income = sum(t.amount for t in transactions)  # Includes transfers!
```

### ✅ Right: Exclude Transfers
```python
total_income = sum(
    t.amount for t in transactions 
    if t.transaction_type == "income"
)
```

### ❌ Wrong: Direct Balance Storage (Stale Risk)
```sql
CREATE TABLE accounts (
    balance NUMERIC(19, 2)  -- Can become stale
);
```

### ✅ Right: Computed Balance
```python
balance = initial_balance + sum_of_transactions
```

### ❌ Wrong: Rounding Too Early
```python
subtotal = round(amount * 0.9, 2)
tax = round(subtotal * 0.1, 2)
total = round(subtotal + tax, 2)  # Multiple rounding = error accumulation
```

### ✅ Right: Round Once at End
```python
subtotal = amount * Decimal("0.9")
tax = subtotal * Decimal("0.1")
total = round_currency(subtotal + tax)
```

## 14. Validation Rules

- **Amount:** Must be positive Decimal
- **Date:** Not more than 365 days in future (warning, not error)
- **Transfer:** Source ≠ destination account
- **Category:** Required for income/expense, NULL for transfer
- **Currency:** Must match account currency (or configurable conversion in future)

## 15. Testing Fixtures

```python
# Test: Simple balance calculation
account = Account(initial_balance=Decimal("1000.00"))
transactions = [
    Transaction(type="income", amount=Decimal("500.00")),
    Transaction(type="expense", amount=Decimal("200.00")),
]
assert calculate_balance(account, transactions) == Decimal("1300.00")

# Test: Transfer not counted as income
transactions = [
    Transaction(type="income", amount=Decimal("500.00")),
    Transaction(type="transfer", amount=Decimal("100.00")),
]
assert calculate_total_income(transactions) == Decimal("500.00")

# Test: Decimal precision
a = Decimal("0.1")
b = Decimal("0.2")
assert a + b == Decimal("0.3")  # Exact (not 0.30000000000000004)

# Test: Budget utilization
budget = Decimal("1000.00")
spent = Decimal("850.00")
assert calculate_budget_utilization(budget, spent) == Decimal("85.00")
```

## Next Steps

Create forecasting methodology and threat model documents.
