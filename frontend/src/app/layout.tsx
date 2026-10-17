import './globals.css';
import type { Metadata } from 'next';

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
      <body>{children}</body>
    </html>
  );
}
