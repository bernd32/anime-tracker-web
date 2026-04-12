'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { Route } from 'next';
import { useRouter } from 'next/navigation';

import { AnimeListView } from '@/features/anime/anime-list-view';
import { AddAnimeButton } from '@/features/anime/add-anime-button';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';
import type { ScopeKind } from '@/lib/api/types';
import { queryKeys } from '@/lib/query/keys';

export function AnimeScopePage({ title, description, scopeKind, scopeYear, search = '' }: { title: string; description: string; scopeKind: ScopeKind; scopeYear?: number; search?: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const scaffold = useMutation({ mutationFn: (year: number) => apiClient.createYearScaffold(year), onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: queryKeys.years() }); } });
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
          {scopeKind === 'year' && scopeYear ? <Button variant="outline" onClick={() => scaffold.mutate(scopeYear)}>Create scaffold</Button> : null}
          {scopeKind === 'year' && scopeYear ? <Button variant="destructive" onClick={() => confirmDeleteYear(scopeYear)}>Delete year</Button> : null}
          <AddAnimeButton />
        </div>
      </div>
      <AnimeListView scopeKind={scopeKind} scopeYear={scopeYear} search={search} />
    </div>
  );
}
