# UI/UX Design Brief — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Design Principles

- **Trust:** Financial data presentation must be accurate, clear, unambiguous
- **Clarity:** Every number shows its context (period, filters, calculation basis)
- **Safety:** Confirm destructive actions; distinguish actuals from projections
- **Efficiency:** Common tasks in ≤3 clicks
- **Accessibility:** Keyboard navigation, ARIA, contrast, semantic HTML

## 2. Visual System

### Theme
- Dark and light modes
- System preference detection with manual toggle

### Colors
- Primary: financial green for positive, red for negative
- Neutral grays for backgrounds
- Accent for CTAs
- Semantic: success, warning, error, info

### Typography
- Sans-serif system font stack
- Headers: 600-700 weight
- Body: 400 weight
- Numbers: tabular figures, monospace for alignment

### Layout
- Responsive: mobile 320px+, tablet 768px+, desktop 1024px+
- Sidebar navigation (desktop), bottom nav (mobile)
- Content max-width: 1200px
- Consistent spacing: 4px base unit (8, 16, 24, 32, 48, 64)

## 3. Component Patterns

### Currency Display
- Format: Rp 1.000.000,00 (IDR default)
- Configurable locale
- Tabular alignment in tables
- Color: green for positive, red for negative, neutral for zero

### Date Display
- Relative: "Today", "Yesterday", "3 days ago" (last 7 days)
- Absolute: "17 Oct 2026" for older dates
- Full timestamp on hover
- Timezone indicator where ambiguous

### Empty States
- Icon + message + primary action
- Example: "No transactions yet. Add your first transaction or import a CSV."

### Loading States
- Skeleton screens for tables
- Spinners for actions
- Disable buttons during submission

### Error States
- Inline validation errors below fields
- Banner for page-level errors
- Actionable message: "Invalid date format. Use YYYY-MM-DD."

### Filters
- Persistent filter bar above lists
- Chips for active filters (closeable)
- Clear all button when >1 filter
- Filter count badge on filter button

## 4. Core Screens

### 4.1 Dashboard (Home)

**Layout:**
- Top: period selector (This Month, Last Month, Last 3 Months, Custom Range)
- Row 1: 4 summary cards (Income, Expenses, Net Cash Flow, Total Balance)
- Row 2: Income vs Expenses chart (line, 6-12 months)
- Row 3: Spending by Category chart (pie or bar)
- Row 4: Recent Transactions (last 10, link to full list)
- Row 5: Budget Status (top 5 categories with progress bars)

**States:**
- Empty: "No transactions yet. Get started by adding accounts and transactions."
- Loading: skeleton cards and chart placeholders
- Error: "Failed to load dashboard. [Retry]"

### 4.2 Accounts

**List View:**
- Cards or table rows
- Columns: Name, Type, Balance, Last Activity
- Actions: Edit, Archive, View Transactions
- Footer: Total Balance across all accounts
- Add Account button (primary, top-right)

**Create/Edit Form:**
- Fields: Name (required), Type (select), Currency (default IDR), Initial Balance (optional, default 0)
- Validate: name not empty, balance is decimal
- Cancel and Save buttons

**Empty State:**
- "No accounts yet. Create your first account to start tracking."

### 4.3 Transactions

**List View:**
- Filters: Date Range, Account(s), Category(ies), Type (Income/Expense/Transfer)
- Search: by description
- Sort: Date (default desc), Amount, Category
- Table columns: Date, Description, Category, Account, Amount, Type
- Color-code type: green (income), red (expense), blue (transfer)
- Pagination: 50 per page
- Actions per row: Edit, Delete (confirm modal)
- Bulk actions: Export CSV
- Add Transaction button (primary, top-right)

**Create/Edit Form:**
- Type selector: Income / Expense / Transfer
- Fields:
  - Date (date picker, default today)
  - Amount (decimal input, required)
  - Account (select, required)
  - Category (select, required for income/expense; N/A for transfer)
  - To Account (select, required for transfer)
  - Description (textarea, optional)
- Validate: amount > 0, date not future (warning only), accounts different for transfer
- Cancel and Save buttons

**Delete Confirmation:**
- Modal: "Delete this transaction? This cannot be undone."
- Show transaction details
- Cancel and Delete buttons

**Empty State:**
- "No transactions found. Adjust filters or add a new transaction."

### 4.4 CSV Import Wizard

**Step 1: Upload**
- Drag-drop zone or file picker
- Accept: .csv, max 10 MB
- Progress bar during upload
- Error: file too large, invalid format

**Step 2: Map Columns**
- Preview: first 5 rows
- Dropdown per column: Date, Description, Amount, Debit, Credit, Category (optional)
- Mark required mappings
- Detect common patterns automatically
- Format settings: Date format (select), Decimal separator (. or ,)
- Back and Next buttons

**Step 3: Preview & Validate**
- Table: all rows with validation status
- Color-code: green (valid), yellow (warning), red (error)
- Error details per row
- Duplicate candidates: "Possible duplicate: [existing transaction]. Import anyway?"
- Checkbox per row: include in import (default: valid=checked, error=unchecked)
- Summary: X valid, Y warnings, Z errors
- Back, Cancel, Confirm Import buttons

**Step 4: Result**
- Summary: X inserted, Y skipped (duplicates), Z rejected (errors)
- Link to imported transactions (filtered)
- Close button

### 4.5 Categories

**List View:**
- Two sections: Income Categories, Expense Categories
- Columns: Name, Color (dot), Transaction Count, Last Used
- Actions: Edit, Delete (if count=0), Merge (if count>0)
- Add Category button per section

**Create/Edit Form:**
- Fields: Name (required), Type (Income/Expense), Color (picker)
- Cancel and Save buttons

**Delete with Transactions:**
- Modal: "This category has X transactions. Reassign them first or merge into another category."
- Reassign dropdown
- Cancel and Proceed buttons

### 4.6 Budgets

**List View:**
- Period selector: This Month, Next Month, Custom Month
- Table: Category, Budget Amount, Actual, Remaining, Utilization %
- Progress bar per row (color: green <80%, yellow 80-100%, red >100%)
- Add Budget button

**Create/Edit Form:**
- Fields: Category (select), Month (month picker), Amount (decimal, required)
- Cancel and Save buttons

**Empty State:**
- "No budgets set for this month. Create your first budget."

### 4.7 Savings Goals (P2)

**List View:**
- Cards: Goal Name, Target Amount, Current Progress, Target Date, Days Remaining
- Progress bar
- Actions: Edit, Complete, Delete
- Add Goal button

**Create/Edit Form:**
- Fields: Name (required), Target Amount (required), Target Date (required), Linked Account (optional)
- Cancel and Save buttons

### 4.8 Reports

**Report Center:**
- Tiles: Income/Expense Summary, Category Breakdown, Monthly Trends, Budget vs Actual, P&L (business mode), Cash Flow Analysis
- Click tile → open report

**Report View:**
- Top: Report name, period selector, filters (accounts, categories)
- Export button (CSV, PDF in future)
- Main content: table and/or chart
- Methodology note: "Calculated as [formula]. Period: [dates]. Filters: [active filters]."

### 4.9 Forecasting (P2)

**Scenario Builder:**
- Base scenario: current data
- Adjustments: increase/decrease income %, increase/decrease expenses %, add/remove recurring transaction
- Horizon: 3, 6, 12 months
- Generate Forecast button

**Forecast View:**
- Chart: projected balance by month
- Table: month, income, expenses, net, balance
- Methodology: "Based on 6-month historical average with [adjustments]."
- Warning: "This is a projection, not a guarantee."
- Compare Scenarios (side-by-side)

### 4.10 AI Insights (P2, Optional)

**Insights Panel (Dashboard sidebar or dedicated page):**
- Cards per insight:
  - Icon + category (Anomaly, Budget, Recurring)
  - Title: "Unusual spending in Dining"
  - Details: "Spent Rp 2.5M this month, 85% above 3-month average of Rp 1.35M."
  - Linked transactions
  - Dismiss button
- Empty: "No insights right now. Check back later."
- Fallback mode indicator: "AI insights unavailable. Showing rule-based alerts only."

### 4.11 Settings

**Sections:**
- **Workspace:** Name, Mode (Personal/Business), Currency (default IDR), Timezone (default Asia/Jakarta), Date Format, Number Format
- **Security:** Change Password, Audit Log (view-only)
- **Data:** Export All Data (CSV), Import Data, Backup/Restore (future), Delete Workspace (confirm)
- **Appearance:** Theme (Light/Dark/System)

## 5. Navigation

**Desktop (Sidebar):**
- Logo + Workspace Name
- Dashboard
- Accounts
- Transactions
- Categories
- Budgets
- Reports
- Forecasts (P2)
- Insights (P2)
- Settings
- Bottom: User menu (logout, profile)

**Mobile (Bottom Nav + Hamburger):**
- Bottom: Dashboard, Transactions, Add (center, prominent), Accounts, Menu
- Menu drawer: full nav list

## 6. Interaction Patterns

### Confirmation Modals
- Destructive actions: Delete transaction, delete account (with transactions), delete workspace
- Financial actions: Import CSV (after preview)
- Pattern: Title, explanation, details, Cancel (secondary) + Confirm (danger)

### Toasts
- Success: "Transaction added", "Budget saved"
- Error: "Failed to save. [Retry]"
- Position: top-right (desktop), top (mobile)
- Duration: 3-5s, dismissible

### Inline Edit
- Where practical: account name, transaction description
- Pattern: click to edit, blur or Enter to save, Esc to cancel

### Keyboard Shortcuts (Desktop)
- `/` focus search
- `n` new transaction
- `Esc` close modal
- Arrow keys navigate lists

## 7. Responsive Breakpoints

- **Mobile:** 320-767px (single column, bottom nav, simplified tables)
- **Tablet:** 768-1023px (2-column where useful, sidebar collapses to icons)
- **Desktop:** 1024px+ (full sidebar, multi-column layouts)

## 8. Data Visualization

### Charts (use Recharts or similar)
- **Line:** Income vs Expenses over time
- **Bar:** Spending by category
- **Pie:** Category proportions (if ≤8 categories, else bar)
- **Progress:** Budget utilization
- **Area:** Forecast balance projection (shaded for uncertainty)

**Requirements:**
- Responsive
- Accessible (keyboard, ARIA labels)
- Color-blind friendly
- Legend
- Tooltips with exact values
- Currency formatting

## 9. Accessibility

- Semantic HTML5 elements
- ARIA labels for icons and interactive elements
- Focus indicators (outline)
- Contrast ratio: 4.5:1 for text, 3:1 for large text
- Form labels associated with inputs
- Error messages linked via aria-describedby
- Keyboard navigation for all interactive elements
- Screen-reader announcements for dynamic content (toasts, updates)

## 10.Localization (IDR/Asia Jakarta Default)

- Currency: Rp 1.000.000,00 (period for thousands, comma for decimals)
- Date: DD/MM/YYYY or DD Mon YYYY
- Time: 24-hour format
- Timezone: Asia/Jakarta (GMT+7)
- Number format: 1.000,50

**Configurable in settings for other locales.**

## 11. Performance

- First paint: <1s
- Interaction to paint: <100ms
- Dashboard load: <2s
- Transaction list (1k rows): <1s with pagination
- CSV import preview: <5s for 1k rows

## 12. Implementation Notes

- Use Next.js 14+ with App Router
- Tailwind CSS for styling
- shadcn/ui for components
- Recharts for charts
- date-fns for date handling with tz support
- decimal.js for client-side decimal math (display only; backend is authoritative)
- React Hook Form + Zod for forms
- TanStack Table for complex tables

## Next Steps

Create architecture and database design documents.
