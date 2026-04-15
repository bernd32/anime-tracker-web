'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { Route } from 'next';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthSession } from '@/features/auth/hooks';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function LoginForm({ nextPath }: { nextPath?: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const authQuery = useAuthSession();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const safeNextPath = normalizeNextPath(nextPath);

  const login = useMutation({
    mutationFn: () => apiClient.login(username, password),
    onSuccess: async (session) => {
      queryClient.setQueryData(queryKeys.authSession(), session);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.authSession() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.preferences() }),
      ]);
      router.replace(safeNextPath);
      router.refresh();
    },
  });

  useEffect(() => {
    if (authQuery.data?.can_write) {
      router.replace(safeNextPath);
    }
  }, [authQuery.data?.can_write, router, safeNextPath]);

  return (
    <form
      className="space-y-4"
      onSubmit={async (event) => {
        event.preventDefault();
        await login.mutateAsync();
      }}
    >
      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input id="username" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
        />
      </div>
      {login.error ? <p className="text-sm text-red-600">{login.error.message}</p> : null}
      <Button type="submit" disabled={login.isPending || authQuery.isLoading}>
        {login.isPending ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}

function normalizeNextPath(nextPath?: string) {
  if (!nextPath || !nextPath.startsWith('/') || nextPath.startsWith('//')) {
    return '/years' as Route;
  }
  return nextPath as Route;
}
