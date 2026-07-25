'use client';

import type React from 'react';
import Link from 'next/link';
import type { Route } from 'next';
import { usePathname } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuthSession } from '@/features/auth/hooks';

export function OwnerGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const authQuery = useAuthSession();

  if (authQuery.isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (authQuery.isError) {
    return <p className="text-sm text-red-600">{authQuery.error.message}</p>;
  }

  if (authQuery.data?.can_write) {
    return <>{children}</>;
  }

  return (
    <div className="rounded-xl border p-6">
      <h1 className="text-xl font-semibold tracking-tight">Owner access required</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Please log in to perform actions.
      </p>
      <div className="mt-4">
        <Button asChild>
          <Link href={`/login?next=${encodeURIComponent(pathname)}` as Route}>Sign in</Link>
        </Button>
      </div>
    </div>
  );
}
