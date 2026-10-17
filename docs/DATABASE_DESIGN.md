# Database Design — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Database Choice

**PostgreSQL 15+** for production (ACID, NUMERIC type, mature)  
**SQLite** for local dev (optional, same schema via SQLAlchemy)

## 2. Schema Overview

```
users
  ↓ (many-to-many via workspace_members)
workspaces
  ↓ (one-to-many)
accounts, categories, budgets, recurring_templates, import_jobs
  ↓
transactions ← links to categories, accounts
  ↓
audit_logs
```

## 3. Core Tables

### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Notes:**
- UUID for IDs (harder to enumerate)
- Email unique, case-insensitive
- Password hashed with bcrypt/argon2

### workspaces

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('personal', 'business')),
    currency VARCHAR(3) DEFAULT 'IDR',
    timezone VARCHAR(50) DEFAULT 'Asia/Jakarta',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Notes:**
- Mode: personal or business (affects UI, categories)
- Currency: ISO 4217 code (IDR default)
- Timezone: IANA timezone (Asia/Jakarta default)

### workspace_members

```sql
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'owner' CHECK (role IN ('owner', 'editor', 'viewer')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
```

**Notes:**
- Many-to-many: user can belong to multiple workspaces
- Role for future permissions (MVP: owner only)

### accounts

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('cash', 'bank', 'savings', 'business')),
    currency VARCHAR(3) DEFAULT 'IDR',
    initial_balance NUMERIC(19, 2) DEFAULT 0.00,
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, name)
);

CREATE INDEX idx_accounts_workspace ON accounts(workspace_id);
CREATE INDEX idx_accounts_workspace_active ON accounts(workspace_id) WHERE archived_at IS NULL;
```

**Notes:**
- NUMERIC(19,2): up to 999,999,999,999,999.99
- Soft delete: archived_at (NULL = active)
- Initial balance: opening balance at account creation
- Current balance: computed from transactions

### categories

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category_type VARCHAR(10) NOT NULL CHECK (category_type IN ('income', 'expense')),
    color VARCHAR(7) DEFAULT '#6B7280',
    is_default BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, name, category_type)
);

CREATE INDEX idx_categories_workspace ON categories(workspace_id);
```

**Notes:**
- Separate income and expense categories
- Color: hex code for UI
- is_default: system-provided categories (can't delete)

### transactions

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense', 'transfer')),
    amount NUMERIC(19, 2) NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL,
    description TEXT,
    notes TEXT,
    transfer_to_account_id UUID REFERENCES accounts(id) ON DELETE RESTRICT,
    transfer_pair_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    import_job_id UUID REFERENCES import_jobs(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (
        (transaction_type = 'transfer' AND transfer_to_account_id IS NOT NULL AND category_id IS NULL)
        OR (transaction_type IN ('income', 'expense') AND transfer_to_account_id IS NULL AND category_id IS NOT NULL)
    )
);

CREATE INDEX idx_transactions_workspace ON transactions(workspace_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_workspace_date ON transactions(workspace_id, transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
```

**Notes:**
- Transfer creates TWO transactions (one debit, one credit) linked by transfer_pair_id
- CHECK: transfer requires transfer_to_account_id, no category; income/expense requires category, no transfer
- amount always positive (type determines sign)
- RESTRICT on account: can't delete account with transactions (must reassign or archive)
- import_job_id: track which import created this transaction

### budgets

```sql
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    period_year INT NOT NULL,
    period_month INT NOT NULL CHECK (period_month BETWEEN 1 AND 12),
    amount NUMERIC(19, 2) NOT NULL CHECK (amount > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, category_id, period_year, period_month)
);

CREATE INDEX idx_budgets_workspace ON budgets(workspace_id);
CREATE INDEX idx_budgets_period ON budgets(period_year, period_month);
```

**Notes:**
- One budget per category per month
- amount: budget limit

### recurring_templates (P1)

```sql
CREATE TABLE recurring_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    amount NUMERIC(19, 2) NOT NULL CHECK (amount > 0),
    description TEXT,
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_recurring_workspace ON recurring_templates(workspace_id);
```

**Notes:**
- Template only (no auto-posting in MVP)
- Used for forecasting

### import_jobs

```sql
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('uploaded', 'previewed', 'confirmed', 'failed')),
    column_mapping JSONB,
    total_rows INT DEFAULT 0,
    imported_rows INT DEFAULT 0,
    skipped_rows INT DEFAULT 0,
    error_rows INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_import_jobs_workspace ON import_jobs(workspace_id);
```

**Notes:**
- column_mapping: JSON with user's column selections
- Counts for summary display

### audit_logs

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'archive')),
    changes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_workspace ON audit_logs(workspace_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

**Notes:**
- changes: JSON with before/after values
- Immutable log (no updates/deletes)

## 4. Default Data (Seed)

### Default Categories (on workspace creation)

**Income:**
- Salary
- Freelance
- Investment
- Other Income

**Expense:**
- Food & Dining
- Transportation
- Utilities
- Rent
- Healthcare
- Entertainment
- Shopping
- Other Expense

**Business (if mode=business):**
- Revenue - Sales
- Revenue - Services
- Expense - Operations
- Expense - Marketing
- Expense - Salaries

## 5. Constraints and Invariants

### Constraints
- All amounts > 0 (stored as positive; type determines direction)
- Transfer has two linked transactions (transfer_pair_id)
- Transfer transactions have no category
- Income/expense transactions have category
- Account names unique per workspace
- Budget unique per workspace/category/month

### Invariants (enforced by application)
- Transfer pair: source account ≠ destination account
- Transaction date not in distant future (warning only)
- Archived account: no new transactions
- Deleted category: reassign transactions first

## 6. Calculated Fields (Not Stored)

### Account Balance
```sql
SELECT 
    a.initial_balance +
    COALESCE(SUM(CASE 
        WHEN t.transaction_type = 'income' THEN t.amount
        WHEN t.transaction_type = 'expense' THEN -t.amount
        WHEN t.transaction_type = 'transfer' AND t.account_id = a.id THEN -t.amount
        WHEN t.transaction_type = 'transfer' AND t.transfer_to_account_id = a.id THEN t.amount
    END), 0) AS current_balance
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id OR t.transfer_to_account_id = a.id
WHERE a.id = ?
```

**Rationale:** Computed to ensure consistency; no risk of stale cached balance.

**Optimization (if needed):** Materialized view or cached column with trigger.

## 7. Migrations

### Initial Migration (alembic)
- Create all tables
- Seed default categories on workspace creation (application logic, not SQL)

### Future Migrations
- Add forecast_scenarios table (P2)
- Add insights table (P2)
- Add attachments table (future: receipt uploads)

## 8. Performance Indexes

**Critical:**
- `transactions(workspace_id, transaction_date)`: for period queries
- `transactions(account_id)`: for account balance
- `transactions(category_id)`: for category summaries

**Future (if needed):**
- Partial index on archived_at IS NULL for active-only queries
- GiST index on date ranges if using range queries

## 9. Backup and Recovery

- Automated daily backups (pg_dump)
- Retention: 30 days
- Test restore monthly
- Workspace export: CSV dump of all transactions

## 10. Security

- No sensitive data in plain text
- User passwords hashed
- Workspace isolation via foreign keys + application checks
- Audit log immutable
- Connection via SSL in production

## Next Steps

Create API documentation and financial calculations document.
