'use client';
import type React from 'react';


import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';

import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function ThemeController({ children }: { children: React.ReactNode }) {
  const query = useQuery({ queryKey: queryKeys.preferences(), queryFn: apiClient.getPreferences, retry: false });

  useEffect(() => {
    const theme = query.data?.theme ?? 'system';
    const root = document.documentElement;
    const resolved = theme === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme;
    root.classList.toggle('dark', resolved === 'dark');
  }, [query.data?.theme]);

  useEffect(() => {
    const density = query.data?.density ?? 'comfortable';
    document.documentElement.dataset.density = density;
  }, [query.data?.density]);

  return <>{children}</>;
}
