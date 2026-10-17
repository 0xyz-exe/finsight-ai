# Product Requirements Document — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17  
**Status:** Initial

## 1. Product Vision

Personal finance and small-business financial analytics platform. Track transactions, understand cash flow, budget, forecast. Privacy-first, local-first, open-source.

## 2. Problem Statement

Users need to:
- Understand their financial position
- Track income/expenses without complex accounting software
- Analyze spending patterns
- Plan budgets and savings
- Forecast future scenarios
- Import bank/bookkeeping data safely

Constraints:
- No bank credentials
- No real payment execution
- No regulated financial advice
- Free and open-source tools only

## 3. User Personas

**Personal User (Primary)**
- Tracks personal income/expenses
- Wants to save money
- Needs budget visibility
- Imports bank CSV exports
- Uses mobile and desktop

**Small Business Owner (Secondary)**
- Tracks business revenue/expenses
- Needs cash-flow monitoring
- Wants P&L summaries
- Imports bookkeeping exports
- Desktop-focused

## 4. Core Workflows

### Personal Finance
1. Create account (cash, bank, savings)
2. Record income/expense transactions
3. Transfer between accounts
4. Import CSV from bank
5. Categorize transactions
6. Set monthly budgets
7. Track savings goals
8. View spending trends
9. Forecast future balance
10. Export filtered records

### Small Business
1. Create business accounts
2. Record revenue/expenses
3. Categorize by business type (sales, operations, etc.)
4. Track cash flow
5. Compare budget vs actual
6. Generate P&L reports
7. Forecast revenue/expenses
8. Export for accountant

## 5. Functional Requirements

### P0 (MVP Must-Have)

**Accounts**
- Create/edit/archive accounts
- Types: cash, bank, savings, business
- Store name, currency (default IDR), initial balance
- List all accounts with current balances

**Transactions**
- Manual income/expense entry
- Fields: date, amount, category, description, account
- Transfer between accounts (not double-counted)
- Edit/delete with safeguards
- List with search/filter/sort
- Pagination

**Categories**
- Custom income/expense categories
- Default set provided
- Edit/delete (with transaction reassignment prompt)

**CSV Import**
- Upload CSV
- Map columns (date, description, amount/debit/credit)
- Preview before import
- Validate rows, show errors
- Detect duplicate candidates
- Confirm import
- Record import history

**Financial Summaries**
- Total income (period)
- Total expenses (period)
- Net cash flow
- Spending by category
- Account balances
- Month-over-month comparison

**Decimal-Safe Arithmetic**
- Use Decimal type or integer minor units
- Never float for authoritative calculations
- Document rounding rules

### P1 (High Priority)

**Budgets**
- Monthly budgets per category
- Budget utilization percentage
- Over-budget alerts
- Budget vs actual report

**Recurring Transactions**
- Define templates (monthly rent, salary, etc.)
- Do not auto-post; keep as templates

**CSV Export**
- Export filtered transactions
- Export reports
- Prevent formula injection

**Charts**
- Spending by category (pie/bar)
- Income vs expenses over time (line)
- Cash flow trends
- Budget utilization

**Audit History**
- Log transaction create/edit/delete
- Log import operations
- Timestamp and user association

**Workspace Isolation**
- Multi-user support
- Each workspace has own accounts/transactions
- Enforce authorization on all operations

### P2 (Nice to Have)

**Savings Goals**
- Set target amount and date
- Track progress from actual data

**Forecasting**
- Historical average method
- Trend-based projection
- User-adjustable scenarios
- Clearly labeled as projection

**AI Insights (Optional)**
- Spending anomalies
- Budget overruns
- Recurring expense changes
- Deterministic fallback if no AI
- Never auto-modify transactions

**Business Mode**
- Toggle personal/business view
- Business-specific categories
- P&L report structure
- Revenue/expense classification

## 6. Non-Functional Requirements

### Security (P0)
- No plaintext secrets in repo
- Input validation on all endpoints
- Parameterized queries (no SQL injection)
- Workspace authorization checks
- CSV injection prevention in exports
- Redact sensitive data from logs

### Privacy (P0)
- No external transmission of financial data (except optional AI, with consent)
- Local storage default
- Clear data retention policy

### Performance (P1)
- Transaction list loads <1s for 10k records
- CSV import validates 1k rows <5s
- Dashboard renders <2s

### Usability (P0)
- Responsive mobile/desktop
- IDR default, configurable currency
- Asia/Jakarta timezone default
- Clear empty states
- Loading indicators
- Error messages with recovery actions

### Accessibility (P1)
- Keyboard navigation
- ARIA labels
- Sufficient contrast
- Semantic HTML

## 7. Acceptance Criteria

**AC1: Account Management**
- User creates account with name, type, currency, initial balance
- Balance updates after transactions
- Archived accounts hidden from active views

**AC2: Transaction Entry**
- User records income/expense with date, amount, category, description
- Amount validated as positive decimal
- Date validated
- Account balance updates immediately

**AC3: Transfer Handling**
- User transfers between accounts
- Both accounts update correctly
- Transfer not counted as income or expense in summaries

**AC4: CSV Import**
- User uploads CSV
- System previews all rows
- User maps columns
- System validates amounts, dates
- Invalid rows shown with error messages
- User confirms import
- Only valid rows imported
- Import summary displayed

**AC5: Financial Summary**
- Dashboard shows total income, total expenses, net cash flow for selected period
- Transfers excluded from income/expense totals
- Empty state if no transactions

**AC6: Budget Tracking**
- User creates monthly budget for category
- System calculates utilization percentage
- Alert shown if exceeded

**AC7: Decimal Safety**
- All monetary calculations use Decimal or integer minor units
- Addition: 1000.50 + 2000.75 = 3001.25 (exact)
- No floating-point errors

**AC8: Authorization**
- User A cannot access User B's workspace
- API returns 403 for unauthorized access
- Verified by test

## 8. Financial Calculation Rules

### Monetary Storage
- PostgreSQL: NUMERIC(19,2) or integer cents
- Python: decimal.Decimal
- JavaScript: decimal.js or integer cents
- Never: binary float for authoritative amounts

### Transaction Types
- **Income:** increases account balance
- **Expense:** decreases account balance
- **Transfer:** decreases source, increases destination; not income/expense

### Balance Calculation
```
Account Balance = Initial Balance 
                  + Sum(Income transactions) 
                  - Sum(Expense transactions) 
                  + Sum(Transfers In) 
                  - Sum(Transfers Out)
```

### Cash Flow
```
Net Cash Flow = Total Income - Total Expenses
```
*Transfers excluded.*

### Budget Utilization
```
Utilization % = (Actual Expenses / Budget Amount) × 100
```

### Refunds/Reversals
- Treat as opposite transaction type with reference to original
- Or: edit original transaction amount

### Date Boundaries
- Use transaction date for period filtering
- Timezone: Asia/Jakarta default
- End-of-day: 23:59:59 in configured timezone

## 9. Security Requirements

### Authentication (P1)
- Password hashing (bcrypt/argon2)
- Session management
- CSRF protection (if cookie-based)

### Authorization (P0)
- Every endpoint checks workspace membership
- No shared data between workspaces

### Input Validation (P0)
- Amount: positive decimal, max precision
- Date: valid ISO format
- Description: max length, no script tags
- CSV: file size limit, validate encoding

### CSV Export (P1)
- Escape formulas (prefix =, +, -, @ with ')
- Validate no script injection

### Secrets (P0)
- .env for local secrets
- Never commit real credentials
- Environment variables for production

## 10. Data Import/Export

### CSV Import Requirements
- Max file size: 10 MB
- Encoding: UTF-8
- Formats supported:
  - Date: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
  - Amount: single column or debit/credit columns
  - Decimal: . or ,
- Validation:
  - Row number for errors
  - Missing required fields
  - Invalid amount/date format
  - Account not found
- Duplicate detection:
  - Match on date + amount + description (fuzzy)
  - User reviews candidates
  - User decides: skip or import as new
- Import summary:
  - Rows inserted
  - Rows skipped (duplicates)
  - Rows rejected (errors)

### CSV Export Requirements
- Filtered transactions to CSV
- Columns: date, description, category, amount, account, type
- Headers in first row
- UTF-8 with BOM for Excel
- Formula injection prevention

## 11. Reporting Requirements

### Personal Finance Reports
1. **Income/Expense Summary:** period, totals, net cash flow
2. **Category Breakdown:** spending by category with percentages
3. **Monthly Trends:** income/expenses by month, line chart
4. **Budget vs Actual:** categories with budget, actual, variance
5. **Account Balances:** all accounts with current balance

### Business Reports (P2)
1. **Profit & Loss:** revenue, expenses, net for period
2. **Cash Flow Statement:** inflows, outflows, net change
3. **Expense by Type:** operational categories
4. **Revenue Trends:** monthly/quarterly

### Report Filters
- Date range
- Account(s)
- Category(ies)
- Transaction type

## 12. Forecasting Requirements

### Methods (P2)
1. **Simple Average:** average last 3/6/12 months
2. **Trend-Based:** linear regression if sufficient data (>12 months)
3. **Recurring Assumptions:** use defined recurring transactions

### Forecast Outputs
- Projected balance by month
- Confidence: "based on 6-month average"
- Scenario name and assumptions displayed

### Scenarios
- Baseline: current spending continues
- Optimistic: expenses reduce 10%
- Pessimistic: expenses increase 10%
- Custom: user-defined adjustments

### Requirements
- Separate actuals from projections visually
- Document methodology in UI
- Do not claim guarantees
- Minimum 3 months data for meaningful forecast

## 13. AI Integration (P2, Optional)

### Insights
- Unusual spending (>2σ from mean)
- Budget overruns
- Recurring expense changes
- Potential duplicates
- Forecast assumptions with high impact

### Requirements
- Optional; works without AI
- Deterministic fallback (threshold rules)
- User consent before sending data
- No auto-modify transactions
- Timeout: 10s
- Validate output structure

### Providers
- Support local/free-tier only for MVP
- Environment variable for API key
- Handle failures gracefully

## 14. Known Limitations

**Out of Scope for MVP:**
- Investment tracking
- Multi-currency conversion
- Tax calculation
- Double-entry accounting
- Payroll
- Invoicing
- Real-time bank sync
- Mobile native app (web-responsive only)
- Multi-user collaboration within workspace
- Recurring transaction auto-posting

**Future Enhancements:**
- Scheduled recurring transaction posting
- Receipt attachment
- Mobile native apps
- Advanced forecasting (ARIMA, ML)
- Investment portfolio tracking
- Tax export formats

## 15. Success Metrics

**MVP Success:**
- User can import 1k-row CSV in <10s
- Financial summaries accurate (test with fixtures)
- Zero data leakage between workspaces
- Zero floating-point errors in calculations
- Security audit passed
- E2E tests cover critical paths

**User Success:**
- Understand spending patterns
- Stay within budgets
- Import bank data safely
- Export for accountant/records

## Next Steps

1. Create UI/UX brief
2. Design database schema
3. Document financial calculations
4. Implement accounts and transactions (P0)
5. Implement CSV import (P0)
6. Implement financial summaries (P0)
