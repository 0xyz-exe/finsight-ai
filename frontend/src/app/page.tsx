'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { accountsApi, transactionsApi, reportsApi, type Account, type Transaction } from '@/lib/api';
import { formatCurrency, formatDateShort } from '@/lib/format';
import AccountForm from '@/components/AccountForm';
import TransactionForm from '@/components/TransactionForm';

export default function Home() {
  const { user, loading: authLoading, logout } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<{ income: string; expense: string; net: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (user) {
      loadDashboard();
    } else {
      setLoading(false);
    }
  }, [authLoading, user]);

  async function loadDashboard() {
    try {
      const [accountsRes, transactionsRes] = await Promise.all([
        accountsApi.list(),
        transactionsApi.list(),
      ]);

      setAccounts(accountsRes.data);
      setTransactions(transactionsRes.data);

      // Load current month summary
      const now = new Date();
      const startDate = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
      const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 1).toISOString().split('T')[0];

      const summaryRes = await reportsApi.summary(startDate, endDate);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">FinSight AI</h1>
            <p className="text-gray-600">Welcome, {user.email}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowAccountForm(true)}
              className="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded"
            >
              + Account
            </button>
            <button
              onClick={() => setShowTransactionForm(true)}
              className="px-4 py-2 text-sm bg-green-600 text-white hover:bg-green-700 rounded"
            >
              + Transaction
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 rounded"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Income</div>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(summary.income)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Expenses</div>
              <div className="text-2xl font-bold text-red-600">{formatCurrency(summary.expense)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Net Cash Flow</div>
              <div className={`text-2xl font-bold ${parseFloat(summary.net) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(summary.net)}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Accounts */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Accounts</h2>
            </div>
            <div className="p-6">
              {accounts.length === 0 ? (
                <p className="text-gray-500">No accounts yet. Create your first account.</p>
              ) : (
                <div className="space-y-4">
                  {accounts.map((account) => (
                    <div key={account.id} className="flex justify-between items-center p-4 border border-gray-200 rounded">
                      <div>
                        <div className="font-medium">{account.name}</div>
                        <div className="text-sm text-gray-500 capitalize">{account.account_type}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatCurrency(account.initial_balance)}</div>
                        <div className="text-sm text-gray-500">{account.currency}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Recent Transactions</h2>
            </div>
            <div className="p-6">
              {transactions.length === 0 ? (
                <p className="text-gray-500">No transactions yet.</p>
              ) : (
                <div className="space-y-3">
                  {transactions.slice(0, 10).map((txn) => (
                    <div key={txn.id} className="flex justify-between items-center p-3 border-b border-gray-100">
                      <div>
                        <div className="font-medium text-sm">{txn.description || 'No description'}</div>
                        <div className="text-xs text-gray-500">{formatDateShort(txn.transaction_date)}</div>
                      </div>
                      <div
                        className={`font-semibold ${
                          txn.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {txn.transaction_type === 'expense' && '-'}
                        {formatCurrency(txn.amount)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showAccountForm && (
        <AccountForm
          onClose={() => setShowAccountForm(false)}
          onSuccess={loadDashboard}
        />
      )}

      {showTransactionForm && (
        <TransactionForm
          onClose={() => setShowTransactionForm(false)}
          onSuccess={loadDashboard}
        />
      )}
    </div>
  );
}
