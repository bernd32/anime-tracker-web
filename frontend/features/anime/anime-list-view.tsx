'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';

import { AnimeRowActions } from '@/features/anime/anime-row-actions';
import { CommentText } from '@/features/anime/comment-text';
import { RandomPickButton } from '@/features/anime/random-pick-button';
import { StatusBadge } from '@/features/anime/status-badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';
import type { AnimeItem, AnimeSeason, ScopeKind } from '@/lib/api/types';
import { queryKeys } from '@/lib/query/keys';
import { percent, titleCaseSeason } from '@/lib/utils';

const seasons: AnimeSeason[] = ['winter', 'spring', 'summer', 'fall', 'other'];

export function AnimeListView({ scopeKind, scopeYear, search = '' }: { scopeKind: ScopeKind; scopeYear?: number; search?: string }) {
  const query = useQuery({
    queryKey: queryKeys.animeList({ scope_kind: scopeKind, scope_year: scopeYear, search }),
    queryFn: () => apiClient.listAnime({ scope_kind: scopeKind, scope_year: scopeYear, search }),
  });

  if (query.isLoading) return <Skeleton className="h-64 w-full" />;
  if (query.isError) return <p className="text-sm text-red-600">{query.error.message}</p>;
  if (!query.data) return <Skeleton className="h-64 w-full" />;

  const items = query.data.items;
  if (scopeKind === 'year') {
    const grouped = new Map<AnimeSeason, AnimeItem[]>();
    seasons.forEach((season) => grouped.set(season, items.filter((item) => item.season === season)));
    return (
      <div className="space-y-6">
        <Toolbar total={items.length} completed={items.filter((item) => item.status === 'completed').length} randomParams={{ scope_kind: 'year', scope_year: scopeYear, search }} />
        {seasons.map((season) => (
          <Section key={season} title={titleCaseSeason(season)} items={grouped.get(season) ?? []} emptyHint={`No anime in ${titleCaseSeason(season)}.`} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Toolbar total={items.length} completed={items.filter((item) => item.status === 'completed').length} randomParams={{ scope_kind: scopeKind, search }} />
      <Section title={scopeKind === 'pre2010' ? 'Pre-2010 anime' : 'Anime'} items={items} emptyHint="No anime found in this scope." />
    </div>
  );
}

function Toolbar({ total, completed, randomParams }: { total: number; completed: number; randomParams: { scope_kind: ScopeKind; scope_year?: number; search?: string } }) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm text-muted-foreground">Total: {total} · Completed: {completed} · {percent(completed, total)}%</p>
      </div>
      <RandomPickButton params={randomParams} />
    </div>
  );
}

function Section({ title, items, emptyHint }: { title: string; items: AnimeItem[]; emptyHint: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {!items.length ? <EmptySection hint={emptyHint} /> : <AnimeCollection items={items} />}
      </CardContent>
    </Card>
  );
}

function EmptySection({ hint }: { hint: string }) {
  return (
    <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
      <p>{hint}</p>
      <Button asChild variant="outline" className="mt-4">
        <Link href="/anime/new">Add anime</Link>
      </Button>
    </div>
  );
}

function AnimeCollection({ items }: { items: AnimeItem[] }) {
  return (
    <>
      <div className="hidden overflow-x-auto lg:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b text-muted-foreground">
              <th className="py-3 pr-4">Name</th>
              <th className="py-3 pr-4">Type</th>
              <th className="py-3 pr-4">Status</th>
              <th className="py-3 pr-4">Downloaded</th>
              <th className="py-3 pr-4">Comment</th>
              <th className="py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((anime) => (
              <tr key={anime.id} className="border-b align-top last:border-b-0">
                <td className="py-3 pr-4 font-medium">{anime.url ? <a href={anime.url} target="_blank" rel="noopener noreferrer nofollow" className="underline underline-offset-2">{anime.name}</a> : anime.name}</td>
                <td className="py-3 pr-4">{anime.type || '—'}</td>
                <td className="py-3 pr-4"><StatusBadge status={anime.status} /></td>
                <td className="py-3 pr-4">{anime.downloaded ? 'Yes' : 'No'}</td>
                <td className="max-w-md py-3 pr-4"><CommentText text={anime.comment} /></td>
                <td className="py-3 text-right"><AnimeRowActions anime={anime} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="space-y-3 lg:hidden">
        {items.map((anime) => (
          <div key={anime.id} className="rounded-lg border p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-2">
                <p className="font-medium">{anime.url ? <a href={anime.url} target="_blank" rel="noopener noreferrer nofollow" className="underline underline-offset-2">{anime.name}</a> : anime.name}</p>
                <div className="flex flex-wrap gap-2"><StatusBadge status={anime.status} /><span className="text-sm text-muted-foreground">{anime.type || 'No type'}</span></div>
                <p className="text-sm text-muted-foreground">Downloaded: {anime.downloaded ? 'Yes' : 'No'}</p>
              </div>
              <AnimeRowActions anime={anime} />
            </div>
            <div className="mt-3"><CommentText text={anime.comment} /></div>
          </div>
        ))}
      </div>
    </>
  );
}
