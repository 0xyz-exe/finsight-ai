# Backend Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)

## Installation

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

3. **Set up database:**

Using Docker:
```bash
docker run --name finsight-db -e POSTGRES_USER=finsight -e POSTGRES_PASSWORD=finsight -e POSTGRES_DB=finsight -p 5432:5432 -d postgres:15
```

Or install PostgreSQL locally and create database:
```sql
CREATE DATABASE finsight;
CREATE USER finsight WITH PASSWORD 'finsight';
GRANT ALL PRIVILEGES ON DATABASE finsight TO finsight;
```

4. **Configure environment:**
```bash
cp ../.env.example .env
# Edit .env if needed (default works for Docker setup above)
```

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start server:**
```bash
uvicorn app.main:app --reload
```

API available at: http://localhost:8000  
API docs: http://localhost:8000/docs

## Testing

```bash
pytest
```

## API Endpoints

### Accounts
- `POST /api/accounts` - Create account
- `GET /api/accounts` - List accounts
- `GET /api/accounts/{id}` - Get account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Archive account

### Transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions` - List transactions
- `GET /api/transactions/{id}` - Get transaction
- `DELETE /api/transactions/{id}` - Delete transaction

## Notes

- MVP uses temporary hardcoded workspace ID
- Auth will be added in next phase
- Transfers not yet implemented
