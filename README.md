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
- ✅ Database models (accounts, transactions, categories)
- ✅ Alembic migrations
- ✅ CRUD API (accounts, transactions)
- ✅ Decimal-safe arithmetic utilities
- ✅ Transfer handling (two linked transactions)
- ✅ Balance calculation service
- ✅ Period summary reports (income/expense/net)
- ✅ Tests: decimal utils (7/7 passed)

**Milestone C** ⏳ Next (CSV Import)
- File upload endpoint
- Column mapping
- Validation and preview
- Duplicate detection
- Confirmed import

**Milestone D-F** ⏳ Remaining
- Frontend (Next.js)
- Analytics and charts
- Forecasting
- Security hardening

## License

*To be determined.*

## Contributing

*Contribution guidelines will be added soon.*
