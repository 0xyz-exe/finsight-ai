import { api } from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export const authApi = {
  register: (data: RegisterRequest) => api.post<User>('/auth/register', data),
  login: (data: LoginRequest) => api.post<AuthResponse>('/auth/login', data),
  me: (token: string) => 
    api.get<User>('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    }),
};

// Token storage
export const TokenStorage = {
  get: () => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('finsight_token');
  },
  
  set: (token: string) => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('finsight_token', token);
  },
  
  remove: () => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('finsight_token');
  },
};

// Add token to all API requests
api.interceptors.request.use((config) => {
  const token = TokenStorage.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      TokenStorage.remove();
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
