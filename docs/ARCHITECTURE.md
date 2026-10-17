# Architecture — FinSight AI

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Forms:** React Hook Form + Zod
- **Tables:** TanStack Table
- **Charts:** Recharts
- **Dates:** date-fns-tz
- **Decimals:** decimal.js (display only)
- **State:** React Context for global state, React Query for server state

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Language:** Python with type hints
- **Validation:** Pydantic v2
- **Database:** PostgreSQL 15+ (prod), SQLite (local dev option)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Decimals:** Python `decimal.Decimal`
- **Auth:** FastAPI security utilities + passlib

### Infrastructure
- **Development:** Docker Compose (optional, not required)
- **CI:** GitHub Actions
- **Testing:** pytest (backend), Vitest + React Testing Library (frontend), Playwright (E2E)

### Rationale
- Free and open-source
- Strong typing (TypeScript, Python type hints)
- Decimal-safe arithmetic (Decimal type)
- Proven for financial applications
- Active maintenance

## 2. System Architecture

### High-Level Design

```
┌─────────────────────────────────────────┐
│         Next.js Frontend (SSR)          │
│  - UI Components                        │
│  - Client-side validation               │
│  - Charts and visualization             │
│  - Form handling                        │
└──────────────┬──────────────────────────┘
               │ REST API (JSON)
               │
┌──────────────▼──────────────────────────┐
│         FastAPI Backend                 │
│  - Request validation (Pydantic)        │
│  - Business logic                       │
│  - Authorization                        │
│  - Financial calculations               │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy ORM
               │
┌──────────────▼──────────────────────────┐
│         PostgreSQL Database             │
│  - ACID transactions                    │
│  - NUMERIC types for money              │
│  - Row-level constraints                │
│  - Indexes for performance              │
└─────────────────────────────────────────┘

External (Optional):
┌─────────────────────────────────────────┐
│      AI Insights Service                │
│  - Local or API-based                   │
│  - Timeout handling                     │
│  - Fallback to rules                    │
└─────────────────────────────────────────┘
```

## 3. Module Boundaries

### Backend Modules

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, startup
│   ├── config.py            # Settings (Pydantic BaseSettings)
│   ├── database.py          # DB session, engine
│   ├── dependencies.py      # Auth, get_db, get_current_user
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── budget.py
│   │   └── audit_log.py
│   ├── schemas/             # Pydantic schemas (API contracts)
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   └── ...
│   ├── routes/              # API endpoints
│   │   ├── accounts.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   ├── budgets.py
│   │   ├── reports.py
│   │   ├── imports.py
│   │   └── auth.py
│   ├── services/            # Business logic
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   ├── import_service.py
│   │   ├── report_service.py
│   │   ├── forecast_service.py  # P2
│   │   └── insight_service.py   # P2
│   └── utils/
│       ├── decimal_utils.py     # Safe arithmetic
│       ├── csv_utils.py
│       ├── auth.py
│       └── validators.py
├── tests/
├── alembic/                 # Migrations
└── requirements.txt
```

### Frontend Modules

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Dashboard
│   │   ├── accounts/
│   │   ├── transactions/
│   │   ├── categories/
│   │   ├── budgets/
│   │   ├── reports/
│   │   └── settings/
│   ├── components/          # Reusable UI
│   │   ├── ui/              # shadcn components
│   │   ├── forms/
│   │   ├── tables/
│   │   ├── charts/
│   │   └── layout/
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # API client
│   │   ├── currency.ts      # Formatting
│   │   ├── dates.ts
│   │   ├── decimal.ts       # decimal.js wrapper
│   │   └── validators.ts    # Zod schemas
│   ├── hooks/               # Custom React hooks
│   ├── contexts/            # React contexts
│   └── types/               # TypeScript types
├── public/
├── tests/
└── package.json
```

## 4. Data Flow

### Example: Create Transaction

1. **User submits form** (frontend)
2. **Client validation** (Zod schema)
3. **API request** `POST /api/transactions` with JSON body
4. **Backend receives**, validates (Pydantic)
5. **Authorization check** (user owns workspace → account)
6. **Business logic** (transaction_service.py):
   - Validate amount > 0
   - Validate account exists and not archived
   - If transfer, validate destination account
   - Start DB transaction
   - Insert transaction record
   - Update account balance (computed, not stored redundantly unless needed for perf)
   - Log audit event
   - Commit DB transaction
7. **Response** with created transaction (201)
8. **Frontend updates** UI, shows toast

### Example: CSV Import

1. **User uploads CSV** (multipart form)
2. **Backend** `/api/imports/upload` stores temp file, returns import_id
3. **User maps columns** (frontend)
4. **POST** `/api/imports/{import_id}/preview` with mapping
5. **Backend validates** all rows, detects duplicates, returns preview
6. **User reviews**, selects rows to import
7. **POST** `/api/imports/{import_id}/confirm` with selected rows
8. **Backend** inserts valid transactions in DB transaction, returns summary
9. **Frontend** shows result, links to imported transactions

## 5. Security Architecture

### Authentication
- Password hashing: bcrypt or argon2
- Session: JWT or secure HTTP-only cookies
- Token expiry: 1 hour (refresh tokens: 7 days)

### Authorization
- Every API endpoint checks `current_user`
- Workspace membership enforced in DB queries
- Pattern:
  ```python
  def get_account(account_id, user):
      account = db.query(Account).filter(
          Account.id == account_id,
          Account.workspace_id.in_(user.workspace_ids)
      ).first()
      if not account:
          raise HTTPException(404)
      return account
  ```

### Input Validation
- Pydantic schemas on backend (all endpoints)
- Zod schemas on frontend (early feedback)
- SQL injection prevention: parameterized queries (SQLAlchemy)
- CSV injection prevention: escape formulas in exports
- File upload: size limit, extension whitelist, content validation

### Secrets Management
- `.env` for local dev (gitignored)
- Environment variables for prod
- Never log sensitive data

## 6. Database Design Principles

- **ACID transactions** for multi-record operations
- **Decimal precision:** NUMERIC(19,2) for amounts (or integer cents)
- **Soft deletes:** `archived_at` timestamp for accounts, categories
- **Audit trail:** separate audit_logs table
- **Workspace isolation:** every entity has workspace_id FK
- **Indexes:** on foreign keys, search fields, date ranges
- **Constraints:** NOT NULL, CHECK (amount > 0), UNIQUE where needed

## 7. Financial Calculation Layer

**Location:** `backend/app/services/report_service.py` and `transaction_service.py`

**Rules:**
- All calculations use `Decimal` type
- Rounding: half-even (banker's rounding), 2 decimal places for display
- Transfer handling: exclude from income/expense totals
- Balance: compute from transactions (not stored redundantly unless cached with invalidation)
- Date boundaries: inclusive start, exclusive end (period filtering)
- Timezone: convert all dates to workspace timezone before calculations

**Never:**
- Float arithmetic for money
- Direct DB aggregates on non-decimal columns
- Unvalidated user input in calculations

## 8. API Design

### REST Principles
- Resources: accounts, transactions, categories, budgets, reports
- HTTP verbs: GET (read), POST (create), PUT/PATCH (update), DELETE
- Status codes: 200 (OK), 201 (created), 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (server error)
- JSON request/response bodies
- Pagination: `?page=1&limit=50`, response includes total_count

### Endpoint Patterns
- List: `GET /api/transactions?page=1&limit=50&date_from=2026-01-01`
- Get: `GET /api/transactions/{id}`
- Create: `POST /api/transactions` (body: JSON)
- Update: `PUT /api/transactions/{id}` (body: JSON)
- Delete: `DELETE /api/transactions/{id}`

### Response Format
```json
{
  "data": {...},
  "meta": {"page": 1, "total": 100}
}
```

### Error Format
```json
{
  "error": {
    "code": "INVALID_AMOUNT",
    "message": "Amount must be greater than zero",
    "field": "amount"
  }
}
```

## 9. Performance Considerations

### Backend
- DB connection pooling
- Indexes on frequently queried columns
- Pagination for large lists
- Lazy loading for relationships (avoid N+1)
- Caching for read-heavy data (future: Redis)

### Frontend
- Code splitting (Next.js automatic)
- Lazy load charts and large components
- Debounce search inputs
- React Query caching
- Pagination for transaction tables

### Database
- Index on (workspace_id, date) for transactions
- Index on (workspace_id, account_id) for transactions
- Partial index for non-archived accounts
- VACUUM and ANALYZE regularly (PostgreSQL)

## 10. Testing Strategy

### Unit Tests (Backend)
- Test financial calculations with fixtures
- Test decimal arithmetic
- Test validators
- Test services in isolation (mock DB)
- Coverage target: >80% for services

### Integration Tests (Backend)
- Test API endpoints with test DB
- Test DB transactions (rollback on error)
- Test authorization (cross-workspace access denied)
- Test CSV import pipeline

### Unit Tests (Frontend)
- Test components with React Testing Library
- Test custom hooks
- Test utility functions (currency formatting, decimal math)

### E2E Tests (Playwright)
- Critical user journeys (see PRD)
- Run against local backend + test DB
- Fixtures for deterministic data

## 11. Development Workflow

### Local Setup
1. Clone repo
2. Backend: `cd backend && python -m venv venv && pip install -r requirements.txt`
3. Database: `docker compose up -d postgres` (or local PostgreSQL)
4. Migrations: `alembic upgrade head`
5. Backend: `uvicorn app.main:app --reload`
6. Frontend: `cd frontend && npm install && npm run dev`
7. Open `http://localhost:3000`

### Database Migrations
- Create: `alembic revision --autogenerate -m "description"`
- Apply: `alembic upgrade head`
- Rollback: `alembic downgrade -1`
- Review generated SQL before applying

### Git Workflow
- Branch per feature: `feature/transaction-import`
- Commit frequently, squash before merge
- Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- PR required for main branch

## 12. Deployment (Future)

### Production Stack (Example)
- **Frontend:** Vercel or self-hosted with PM2
- **Backend:** Docker container on VPS or cloud
- **Database:** Managed PostgreSQL (AWS RDS, DigitalOcean)
- **Secrets:** Environment variables
- **Backups:** Daily automated DB backups
- **Monitoring:** Application logs, error tracking (Sentry)

### Environment Variables
```
# Backend
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=...
ALLOWED_ORIGINS=https://finsight.example.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.finsight.example.com
```

## 13. Known Constraints

- **No microservices:** Monolithic backend for MVP (simpler)
- **No real-time sync:** Polling or manual refresh
- **No multi-tenancy isolation:** Workspace-level only (same DB)
- **No horizontal scaling needed:** Single instance sufficient for MVP
- **CSV only:** No direct bank API integration

## Next Steps

Create database design document with schema and relationships.
