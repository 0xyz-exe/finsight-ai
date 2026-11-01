# FinSight AI

Personal finance and small-business financial analytics built with Next.js and
FastAPI.

Repository: https://github.com/0xyz-exe/finsight-ai

## Screenshots

### 1. Financial Overview & Cash Flow Dashboard
Dasbor utama FinSight AI untuk pemantauan kesehatan finansial dan arus kas secara real-time dengan kartu metrik ringkasan (Total Pemasukan, Total Pengeluaran, dan Arus Kas Bersih berformat mata uang IDR), panel ringkasan saldo per akun keuangan (Bank, Kas Tunai, Bisnis, Tabungan), serta daftar transaksi terkini dengan indikator visual berkode warna hijau dan merah yang memudahkan identifikasi mutasi kas:
![Financial Overview & Cash Flow Dashboard](docs/screenshots/01_dashboard.png)

### 2. Transaction History & Categorization
Antarmuka pencatatan dan kategorisasi transaksi keuangan yang fleksibel dengan dialog modal penambahan transaksi multi-tipe (Pemasukan, Pengeluaran, dan Transfer Antar Rekening), pemilihan akun sumber dan tujuan, input nominal desimal presisi, penentuan tanggal mutasi, serta penulisan deskripsi alur kas yang terhubung langsung ke buku kas workspace:
![Transaction History & Categorization](docs/screenshots/02_transactions.png)

### 3. Account Management & Net Worth
Pusat pengelolaan akun keuangan dan aset multi-kategori yang mendukung rekening giro operasional bank, rekening bisnis, kas kecil (petty cash), dan deposito tabungan jangka panjang dengan konfigurasi saldo awal, kode mata uang global (IDR), dan isolasi data berbasis workspace terenkripsi untuk mengkalkulasi kekayaan bersih secara akurat:
![Account Management & Net Worth](docs/screenshots/03_accounts.png)

### 4. Financial Analytics & Summary Reports
Panel pelaporan analitik keuangan yang menghitung agregasi total pemasukan, total pengeluaran operasional, dan arus kas bersih pada periode berjalan menggunakan kalkulasi desimal berbasis server yang aman dari floating-point rounding error, menyajikan wawasan likuiditas finansial untuk bisnis maupun personal:
![Financial Analytics & Summary Reports](docs/screenshots/04_reports.png)

### 5. Secure JWT Authentication
Gerbang autentikasi mandiri berbasis JSON Web Token (JWT) dengan alur login dan registrasi aman, proteksi kredensial menggunakan hashing password berbasis bcrypt, isolasi session pengguna, serta integrasi otomatis ke workspace finansial pribadi pengguna:
![Secure JWT Authentication](docs/screenshots/05_login.png)

> **Status:** MVP complete and ready for beta testing.

FinSight AI helps users track accounts and transactions, understand cash flow,
and view financial summaries in a workspace-isolated dashboard.

## Features

- JWT authentication with login and registration
- Workspace-isolated user data
- Account management for cash, bank, savings, and business accounts
- Income, expense, and transfer transactions
- Decimal-safe balance and cash-flow calculations
- Current-period financial summaries
- CSV import and export support in the backend
- Responsive dashboard with IDR currency formatting

## Tech stack

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.11+
- **Database:** PostgreSQL 15+
- **ORM and migrations:** SQLAlchemy, Alembic

## Repository structure

```text
.
├── backend/       FastAPI application, models, migrations, and tests
├── frontend/      Next.js application
├── docs/          Product, architecture, database, and security documentation
└── .env.example   Backend environment template
```

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- PostgreSQL 15 or newer
- Git

Docker can be used to run PostgreSQL locally.

## Quick start

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd finsight-ai
```

Replace `<your-repository-url>` with the URL of your GitHub repository.

### 2. Start PostgreSQL

Using Docker:

```bash
docker run --name finsight-db \
  -e POSTGRES_USER=finsight \
  -e POSTGRES_PASSWORD=finsight \
  -e POSTGRES_DB=finsight \
  -p 5432:5432 \
  -d postgres:15
```

If the container already exists, start it with:

```bash
docker start finsight-db
```

### 3. Configure the backend

From the repository root, copy the environment template:

```powershell
Copy-Item .env.example backend\.env
```

For macOS/Linux:

```bash
cp .env.example backend/.env
```

Review `backend/.env` and change `SECRET_KEY` before using the application
outside local development. Never commit `.env` or real credentials.

The default database configuration expects:

```text
DATABASE_URL=postgresql://finsight:finsight@localhost:5432/finsight
```

### 4. Install and run the backend

#### Windows PowerShell

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks activation scripts, run this once for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS/Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

The backend is available at:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Expected health response:

```json
{"status":"ok"}
```

### 5. Install and run the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The dashboard is available at <http://localhost:3000>.

The frontend uses `http://localhost:8000/api` by default. To use another API
URL, create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Restart the frontend after changing environment variables.

## Testing and builds

Run backend tests:

```bash
cd backend
venv\Scripts\python.exe -m pytest -q       # Windows
./venv/bin/python -m pytest -q             # macOS/Linux
```

Build the frontend:

```bash
cd frontend
npm run build
```

The current verified baseline is 14 passing backend tests and a successful
frontend production build.

## Documentation

- [Backend setup and API endpoints](backend/README.md)
- [Frontend setup](frontend/README.md)
- [Product requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database design](docs/DATABASE_DESIGN.md)
- [Financial calculations](docs/FINANCIAL_CALCULATIONS.md)
- [Forecasting methodology](docs/FORECASTING_METHODOLOGY.md)
- [Threat model](docs/THREAT_MODEL.md)

## Roadmap

- CSV import wizard in the frontend
- Charts and analytics
- Budgets and goals
- Forecasting workflows
- End-to-end testing
- Production security hardening
- Containerized application deployment

## Security

This project is intended for local development and beta testing. Before
production use:

- Set a strong, unique `SECRET_KEY`.
- Use a managed PostgreSQL instance with secure credentials.
- Configure `ALLOWED_ORIGINS` for the deployed frontend only.
- Store secrets in the deployment platform's secret manager.
- Review the [threat model](docs/THREAT_MODEL.md).

Please do not commit passwords, API keys, `.env` files, uploaded financial
data, or database backups.

## License

This project is not currently licensed for redistribution. Add a license
before publishing it for reuse.

## Contributing

Issues and pull requests are welcome. Please include reproduction steps,
tests for behavioral changes, and documentation updates where appropriate.
