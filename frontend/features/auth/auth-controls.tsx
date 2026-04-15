'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import type { Route } from 'next';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { useAuthSession } from '@/features/auth/hooks';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function AuthControls() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const authQuery = useAuthSession();
  const logout = useMutation({
    mutationFn: apiClient.logout,
    onSuccess: async (session) => {
      queryClient.setQueryData(queryKeys.authSession(), session);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.authSession() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.preferences() }),
      ]);
      router.push('/years');
      router.refresh();
    },
  });

  if (authQuery.isError) {
    return <span className="text-sm text-red-600">{authQuery.error.message}</span>;
  }

  if (authQuery.isLoading || !authQuery.data) {
    return <span className="text-sm text-muted-foreground">Checking access...</span>;
  }

  if (!authQuery.data.authenticated) {
    return (
      <>
        <span className="hidden text-sm text-muted-foreground sm:inline">Read only</span>
        <Button asChild variant="outline" size="sm">
          <Link href={'/login' as Route}>Sign in</Link>
        </Button>
      </>
    );
  }

  return (
    <>
      <span className="hidden text-sm text-muted-foreground sm:inline">{authQuery.data.username}</span>
      <Button type="button" variant="outline" size="sm" onClick={() => logout.mutate()} disabled={logout.isPending}>
        {logout.isPending ? 'Signing out...' : 'Sign out'}
      </Button>
    </>
  );
}
