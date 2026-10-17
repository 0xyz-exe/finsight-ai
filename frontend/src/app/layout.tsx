import './globals.css';
import type { Metadata } from 'next';
import { AuthProvider } from '@/contexts/AuthContext';

export const metadata: Metadata = {
  title: 'FinSight AI - Personal Finance',
  description: 'Track your finances with ease',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
