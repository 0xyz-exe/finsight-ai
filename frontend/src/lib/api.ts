import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Account types
export interface Account {
  id: string;
  workspace_id: string;
  name: string;
  account_type: 'cash' | 'bank' | 'savings' | 'business';
  currency: string;
  initial_balance: string;
  archived_at: string | null;
}

export interface AccountCreate {
  name: string;
  account_type: 'cash' | 'bank' | 'savings' | 'business';
  currency?: string;
  initial_balance?: string;
}

// Transaction types
export interface Transaction {
  id: string;
  workspace_id: string;
  account_id: string;
  category_id: string | null;
  transaction_type: 'income' | 'expense' | 'transfer';
  amount: string;
  transaction_date: string;
  description: string | null;
  notes: string | null;
  transfer_to_account_id: string | null;
  transfer_pair_id: string | null;
}

export interface TransactionCreate {
  transaction_type: 'income' | 'expense' | 'transfer';
  amount: string;
  transaction_date: string;
  description?: string;
  notes?: string;
  account_id: string;
  category_id?: string;
  transfer_to_account_id?: string;
}

// API functions
export const accountsApi = {
  list: () => api.get<Account[]>('/accounts'),
  get: (id: string) => api.get<Account>(`/accounts/${id}`),
  create: (data: AccountCreate) => api.post<Account>('/accounts', data),
  update: (id: string, data: Partial<AccountCreate>) => api.put<Account>(`/accounts/${id}`, data),
  delete: (id: string) => api.delete(`/accounts/${id}`),
};

export const transactionsApi = {
  list: () => api.get<Transaction[]>('/transactions'),
  get: (id: string) => api.get<Transaction>(`/transactions/${id}`),
  create: (data: TransactionCreate) => api.post<Transaction>('/transactions', data),
  delete: (id: string) => api.delete(`/transactions/${id}`),
};

export const reportsApi = {
  balance: (accountId: string) => api.get<{ account_id: string; balance: string }>(`/reports/balance/${accountId}`),
  summary: (startDate: string, endDate: string) =>
    api.get<{ income: string; expense: string; net: string; start_date: string; end_date: string }>(
      `/reports/summary?start_date=${startDate}&end_date=${endDate}`
    ),
};
