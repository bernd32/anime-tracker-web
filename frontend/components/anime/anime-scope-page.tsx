'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { Route } from 'next';
import { useRouter } from 'next/navigation';

import { AnimeListView } from '@/features/anime/anime-list-view';
import { AddAnimeButton } from '@/features/anime/add-anime-button';
import { useAuthSession } from '@/features/auth/hooks';
import { RandomPickButton } from '@/features/anime/random-pick-button';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/lib/api/client';
import type { ScopeKind } from '@/lib/api/types';
import { queryKeys } from '@/lib/query/keys';
import { cn, percent } from '@/lib/utils';

export function AnimeScopePage({ title, description, scopeKind, scopeYear, search = '' }: { title: string; description: string; scopeKind: ScopeKind; scopeYear?: number; search?: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const authQuery = useAuthSession();
  const canWrite = authQuery.data?.can_write ?? false;
  const deleteYear = useMutation({
    mutationFn: (year: number) => apiClient.deleteYear(year),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.years() }),
        queryClient.invalidateQueries({ queryKey: ['anime'] }),
        queryClient.invalidateQueries({ queryKey: queryKeys.stats() }),
      ]);
      const years = await queryClient.fetchQuery({
        queryKey: queryKeys.years(),
        queryFn: apiClient.getYears,
      });
      const latestYear = years.items[0]?.year;
      router.push((latestYear ? `/library/${latestYear}` : '/years') as Route);
    },
  });
  const confirmDeleteYear = (year: number) => {
    if (!window.confirm(`Delete the year ${year} and all anime entries in it? This cannot be undone.`)) {
      return;
    }
    deleteYear.mutate(year);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-xl border p-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {canWrite && scopeKind === 'year' && scopeYear ? <Button variant="destructive" onClick={() => confirmDeleteYear(scopeYear)}>Delete year</Button> : null}
          <RandomPickButton params={{ scope_kind: scopeKind, scope_year: scopeYear, search }} />
          <AddAnimeButton year={scopeYear} />
        </div>
      </div>
      {scopeKind === 'year' && scopeYear ? <ScopeCompletionChart scopeKind={scopeKind} scopeYear={scopeYear} search={search} /> : null}
      {scopeKind === 'pre2010' ? <ScopeCompletionChart scopeKind={scopeKind} search={search} /> : null}
      <AnimeListView scopeKind={scopeKind} scopeYear={scopeYear} search={search} />
    </div>
  );
}

function ScopeCompletionChart({ scopeKind, scopeYear, search }: { scopeKind: ScopeKind; scopeYear?: number; search: string }) {
  const query = useQuery({
    queryKey: queryKeys.animeList({ scope_kind: scopeKind, scope_year: scopeYear, search }),
    queryFn: () => apiClient.listAnime({ scope_kind: scopeKind, scope_year: scopeYear, search }),
  });

  if (query.isLoading) {
    return <Skeleton className="h-32 w-full" />;
  }
  if (query.isError || !query.data) {
    return null;
  }

  const total = query.data.items.length;
  const completed = query.data.items.filter((item) => item.status === 'completed').length;
  const completion = percent(completed, total);
  const progressLabel = scopeKind === 'year' && scopeYear ? `${scopeYear}` : 'Pre-2010';

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-3xl font-semibold tracking-tight">{completion}%</p>
            <p className="text-sm text-muted-foreground">{completed} completed of {total} anime</p>
          </div>
          <div className="text-sm text-muted-foreground">
            {total ? `Progress for ${progressLabel}` : `No anime added for ${progressLabel} yet`}
          </div>
        </div>
        <div className="h-4 overflow-hidden rounded-full bg-slate-100">
          <div
            className={cn(
              'h-full rounded-full bg-gradient-to-r from-green-400 via-green-500 to-emerald-500 transition-[width] duration-300',
              !total && 'w-0',
            )}
            style={{ width: `${completion}%` }}
            aria-hidden="true"
          />
        </div>
      </CardContent>
    </Card>
  );
}
