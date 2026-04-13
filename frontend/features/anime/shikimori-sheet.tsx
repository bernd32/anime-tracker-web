'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import type { AnimeItem } from '@/lib/api/types';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function ShikimoriSheet({ anime, open, onOpenChange }: { anime: AnimeItem; open: boolean; onOpenChange: (value: boolean) => void }) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: queryKeys.shikimori(anime.id),
    queryFn: () => apiClient.getShikimori(anime.id),
    enabled: open,
  });
  const resetCache = useMutation({
    mutationFn: () => apiClient.resetShikimori(anime.id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.shikimori(anime.id) });
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>{anime.name}</DialogTitle>
          <DialogDescription>Cached Shikimori information</DialogDescription>
        </DialogHeader>
        <div className="flex justify-end">
          <Button type="button" variant="outline" size="sm" onClick={() => resetCache.mutate()} disabled={resetCache.isPending}>
            {resetCache.isPending ? 'Resetting...' : 'Reset cache'}
          </Button>
        </div>
        {query.isLoading ? <Skeleton className="h-48 w-full" /> : null}
        {query.isError ? <p className="text-sm text-red-600">{query.error.message}</p> : null}
        {resetCache.isError ? <p className="text-sm text-red-600">{resetCache.error.message}</p> : null}
        {query.data ? (
          <div className="space-y-4 text-sm">
            <div className="grid gap-4 sm:grid-cols-2">
              <Info label="Russian title" value={query.data.result.russian} />
              <Info label="Japanese title" value={query.data.result.japanese} />
              <Info label="Score" value={query.data.result.score} />
              <Info label="Episodes" value={String(query.data.result.episodes ?? '—')} />
              <Info label="Aired on" value={query.data.result.aired_on ?? '—'} />
              <Info label="Cache source" value={query.data.cache.source} />
            </div>
            <Info label="Studios" value={query.data.result.studios.join(', ') || '—'} />
            <Info label="Genres" value={query.data.result.genres.join(', ') || '—'} />
            <Info label="Description" value={query.data.result.description ?? '—'} />
            {anime.url ? <a href={anime.url} target="_blank" rel="noopener noreferrer nofollow" className="text-sm underline">Open external anime URL</a> : null}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function Info({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="whitespace-pre-wrap break-words">{value || '—'}</p>
    </div>
  );
}
