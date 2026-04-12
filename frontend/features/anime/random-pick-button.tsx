'use client';

import { useQuery } from '@tanstack/react-query';
import { Shuffle } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useMutations } from '@/features/anime/hooks';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import type { ScopeKind } from '@/lib/api/types';
import { decodeHtmlEntities } from '@/lib/utils';

export function RandomPickButton({ params }: { params: { scope_kind: ScopeKind; scope_year?: number; season?: string; search?: string } }) {
  const [open, setOpen] = useState(false);
  const { updateStatus } = useMutations();
  const query = useQuery({
    queryKey: queryKeys.randomPick(params),
    queryFn: () => apiClient.getRandomPick(params),
    enabled: open,
  });
  const pickedAnime = query.data?.item ?? null;

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)}><Shuffle className="h-4 w-4" />Random pick</Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Random pick</DialogTitle>
            <DialogDescription>Choose an unwatched anime from the current scope.</DialogDescription>
          </DialogHeader>
          {query.isLoading ? <p>Choosing…</p> : null}
          {query.isError ? <p className="text-sm text-red-600">{query.error.message}</p> : null}
          {pickedAnime ? (
            <div className="space-y-4">
              <div className="space-y-2 rounded-2xl border border-border/70 bg-muted/40 p-5">
                <p className="text-lg font-semibold">{decodeHtmlEntities(pickedAnime.name)}</p>
                <p className="text-sm text-muted-foreground">{pickedAnime.year} · {pickedAnime.season}</p>
              </div>
              <div className="flex justify-end">
                <Button
                  type="button"
                  onClick={() => updateStatus.mutate({ id: pickedAnime.id, status: 'watching' })}
                  disabled={updateStatus.isPending || pickedAnime.status === 'watching'}
                >
                  Set as watching
                </Button>
              </div>
            </div>
          ) : null}
          {query.data && !query.data.item ? <p className="text-sm text-muted-foreground">No unwatched anime found in this scope.</p> : null}
        </DialogContent>
      </Dialog>
    </>
  );
}
