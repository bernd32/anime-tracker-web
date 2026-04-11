'use client';

import { useQuery } from '@tanstack/react-query';
import { Shuffle } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import type { ScopeKind } from '@/lib/api/types';

export function RandomPickButton({ params }: { params: { scope_kind: ScopeKind; scope_year?: number; season?: string; search?: string } }) {
  const [open, setOpen] = useState(false);
  const query = useQuery({
    queryKey: queryKeys.randomPick(params),
    queryFn: () => apiClient.getRandomPick(params),
    enabled: open,
  });

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
          {query.data?.item ? (
            <div className="space-y-2">
              <p className="text-lg font-semibold">{query.data.item.name}</p>
              <p className="text-sm text-muted-foreground">{query.data.item.year} · {query.data.item.season}</p>
            </div>
          ) : null}
          {query.data && !query.data.item ? <p className="text-sm text-muted-foreground">No unwatched anime found in this scope.</p> : null}
        </DialogContent>
      </Dialog>
    </>
  );
}
