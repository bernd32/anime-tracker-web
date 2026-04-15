'use client';

import Link from 'next/link';
import type { Route } from 'next';
import { Plus } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useAuthSession } from '@/features/auth/hooks';

export function AddAnimeButton({ year }: { year?: number }) {
  const authQuery = useAuthSession();
  const href = (year ? `/anime/new?year=${year}` : '/anime/new') as Route;

  if (!authQuery.data?.can_write) {
    return null;
  }

  return (
    <Button asChild>
      <Link href={href}><Plus className="h-4 w-4" />Add anime</Link>
    </Button>
  );
}
