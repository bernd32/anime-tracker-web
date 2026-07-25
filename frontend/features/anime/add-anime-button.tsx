'use client';

import Link from 'next/link';
import type { Route } from 'next';
import { Plus } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useRequireOwnerAction } from '@/features/auth/require-owner-action';

export function AddAnimeButton({ year }: { year?: number }) {
  const { requireOwnerAction } = useRequireOwnerAction();
  const href = (year ? `/anime/new?year=${year}` : '/anime/new') as Route;

  return (
    <Button asChild>
      <Link
        href={href}
        onClick={(event) => {
          if (!requireOwnerAction()) event.preventDefault();
        }}
      >
        <Plus className="h-4 w-4" />Add anime
      </Link>
    </Button>
  );
}
