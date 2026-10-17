'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, TokenStorage, type User } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    const token = TokenStorage.get();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const res = await authApi.me(token);
      setUser(res.data);
    } catch (error) {
      TokenStorage.remove();
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const res = await authApi.login({ email, password });
    TokenStorage.set(res.data.access_token);
    await loadUser();
  }

  async function register(email: string, password: string, fullName?: string) {
    await authApi.register({ email, password, full_name: fullName });
    await login(email, password);
  }

  function logout() {
    TokenStorage.remove();
    setUser(null);
    window.location.href = '/login';
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
