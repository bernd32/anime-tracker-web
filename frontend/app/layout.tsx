import type React from 'react';
import './globals.css';

import type { Metadata } from 'next';

import { AppShell } from '@/components/layout/app-shell';
import { AppProviders } from '@/components/providers/app-providers';

export const metadata: Metadata = {
  title: 'Anime Backlog Tracker',
  description: 'Self-hosted anime backlog tracker',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppProviders>
          <AppShell>{children}</AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
