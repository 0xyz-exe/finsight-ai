# Frontend Setup

## Prerequisites

- Node.js 18+
- Backend running on `http://localhost:8000`

## Installation

```bash
cd frontend
npm install
```

## Configuration

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Development

```bash
npm run dev
```

Open http://localhost:3000

## Features

**Dashboard (/):**
- Summary cards (income, expense, net)
- Accounts list
- Recent transactions

**Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Axios for API
- React Query (ready)
- Recharts (ready for charts)

## API Integration

All API calls in `src/lib/api.ts`:
- Accounts CRUD
- Transactions CRUD
- Reports (balance, summary)

## Format Utilities

`src/lib/format.ts`:
- `formatCurrency()` - IDR default (Rp 1.000.000)
- `formatDate()` - Indonesian format
- `formatDateShort()` - Abbreviated

## Next Steps

1. Add account creation form
2. Add transaction creation form
3. Add CSV import wizard
4. Add charts (Recharts)
5. Add navigation
6. Add error boundaries
7. Add loading states
