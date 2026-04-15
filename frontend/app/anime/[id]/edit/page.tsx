'use client';

import { useParams } from 'next/navigation';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AnimeForm } from '@/features/anime/anime-form';
import { OwnerGate } from '@/features/auth/owner-gate';
import { useAnime } from '@/features/anime/hooks';

export default function EditAnimePage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const query = useAnime(id);

  return (
    <OwnerGate>
      <Card>
        <CardHeader><CardTitle>Edit anime</CardTitle></CardHeader>
        <CardContent>
          {!Number.isFinite(id) ? <p className="text-sm text-red-600">Invalid anime id.</p> : null}
          {query.isLoading ? <Skeleton className="h-72 w-full" /> : null}
          {query.isError ? <p className="text-sm text-red-600">{query.error.message}</p> : null}
          {Number.isFinite(id) && query.data ? <AnimeForm mode="edit" initial={query.data.item} /> : null}
        </CardContent>
      </Card>
    </OwnerGate>
  );
}
