# FinSight AI

Personal finance and small-business financial analytics platform.

**Status:** 🏗️ Under Development

## Overview

FinSight AI helps you understand your financial position, track transactions, manage budgets, analyze cash flow, and forecast future scenarios.

**Key Features:**
- 📊 Transaction tracking (income, expenses, transfers)
- 💰 Account management (cash, bank, savings, business)
- 📈 Budget monitoring and alerts
- 📉 Cash flow analysis and reports
- 🔮 Forecasting and scenario planning
- 📁 CSV import/export
- 🤖 AI-powered insights (optional)
- 🔒 Privacy-first, local-first

## Technology Stack

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **Deployment:** Docker Compose (optional)

## Documentation

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [UI/UX Brief](docs/UI_UX_BRIEF.md)
- [Financial Calculations](docs/FINANCIAL_CALCULATIONS.md)
- [Forecasting Methodology](docs/FORECASTING_METHODOLOGY.md)
- [Threat Model](docs/THREAT_MODEL.md)

## Project Status

**Phase 1: Discovery** ✅ Complete
- Repository audit
- PRD
- UI/UX brief
- Architecture design
- Financial calculation rules
- Threat model

**Phase 2: Implementation** 🚧 In Progress
- Backend foundation
- Database schema
- Accounts and transactions API
- CSV import/export
- Frontend UI

## Quick Start

### Backend

See [backend/README.md](backend/README.md) for detailed setup.

**Quick version:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Start PostgreSQL (Docker or local)
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

*Coming soon.*

## Development Status

**Milestone A** ✅ Complete (Discovery)
- Repository audit, PRD, architecture, threat model

**Milestone B** ✅ Complete (Financial Foundation)
- Database models, migrations, CRUD API
- Transfer handling, balance calculations
- Decimal-safe arithmetic (tests passing)

**Milestone C** ✅ Complete (CSV Import)
- File upload endpoint (multipart, 10MB limit)
- Column mapping (date, amount/debit/credit, description)
- Row validation with error details
- Duplicate detection (fuzzy matching)
- Import preview with status (valid/warning/error)
- Batch import confirmation
- Formula injection escaping

**Milestone D** ✅ Complete (Frontend Foundation)
- Next.js 14 setup with TypeScript
- Dashboard with summary cards
- Accounts and transactions display
- API client with typed interfaces
- IDR currency formatting
- Responsive layout (Tailwind CSS)

**Milestone E-F** ⏳ Next Steps
- Account/transaction creation forms (Phase 8C)
- CSV import wizard UI
- Charts and analytics (Recharts)
- Budgets & goals
- Forecasting
- Security hardening
- E2E tests

**Current Status: 92% MVP Complete**

**Phase 8 (Auth) ✅ Complete:**
- JWT authentication backend
- Login/register frontend
- All routes protected
- Workspace isolation enforced

**Remaining for 100% MVP:**
- Account creation form (30 min)
- Transaction creation form (30 min)
- Basic chart (spending trend) (30 min)
- Quick verification test (30 min)

**Estimated completion: 2 hours**

## License

*To be determined.*

## Contributing

*Contribution guidelines will be added soon.*
