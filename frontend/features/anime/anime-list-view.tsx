'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';

import { AnimeRowActions } from '@/features/anime/anime-row-actions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api/client';
import type { AnimeItem, AnimeSeason, ScopeKind } from '@/lib/api/types';
import { queryKeys } from '@/lib/query/keys';
import { cn, decodeHtmlEntities, titleCaseSeason } from '@/lib/utils';

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
        {seasons.map((season) => (
          <Section
            key={season}
            title={`${titleCaseSeason(season)} (${(grouped.get(season) ?? []).length})`}
            items={grouped.get(season) ?? []}
            emptyHint={`No anime in ${titleCaseSeason(season)}.`}
            addAnimeYear={scopeYear}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Section title={scopeKind === 'pre2010' ? 'Pre-2010 anime' : 'Anime'} items={items} emptyHint="No anime found in this scope." />
    </div>
  );
}

function Section({ title, items, emptyHint, addAnimeYear }: { title: string; items: AnimeItem[]; emptyHint: string; addAnimeYear?: number }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {!items.length ? <EmptySection hint={emptyHint} year={addAnimeYear} /> : <AnimeCollection items={items} />}
      </CardContent>
    </Card>
  );
}

function EmptySection({ hint, year }: { hint: string; year?: number }) {
  return (
    <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
      <p>{hint}</p>
      <Button asChild variant="outline" className="mt-4">
        <Link href={year ? `/anime/new?year=${year}` : '/anime/new'}>Add anime</Link>
      </Button>
    </div>
  );
}

function AnimeCollection({ items }: { items: AnimeItem[] }) {
  return (
    <>
      <div className="hidden overflow-x-auto lg:block">
        <table className="w-full table-fixed border-separate [border-spacing:0_0.5rem] text-left text-sm">
          <colgroup>
            <col className="w-[52%]" />
            <col className="w-[16%]" />
            <col className="w-[32%]" />
          </colgroup>
          <thead>
            <tr className="text-muted-foreground">
              <th className="px-4 py-1.5">Name</th>
              <th className="px-4 py-1.5">Type</th>
              <th className="px-4 py-1.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((anime) => (
              <tr key={anime.id} className="align-top">
                <td className={cn(animeCellClassName(anime), 'rounded-l-xl border-r-0 px-4 py-2.5 font-medium')}>
                  {anime.url ? (
                    <a
                      href={anime.url}
                      target="_blank"
                      rel="noopener noreferrer nofollow"
                      className="block truncate underline underline-offset-2"
                      title={decodeHtmlEntities(anime.name)}
                    >
                      {decodeHtmlEntities(anime.name)}
                    </a>
                  ) : (
                    <span className="block truncate" title={decodeHtmlEntities(anime.name)}>
                      {decodeHtmlEntities(anime.name)}
                    </span>
                  )}
                </td>
                <td className={cn(animeCellClassName(anime), 'border-l-0 border-r-0 px-4 py-2.5')}>{anime.type || '—'}</td>
                <td className={cn(animeCellClassName(anime), 'rounded-r-xl border-l-0 px-4 py-2 text-right')}><AnimeRowActions anime={anime} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="space-y-3 lg:hidden">
        {items.map((anime) => (
          <div key={anime.id} className={cn('rounded-xl border p-4 shadow-sm', animeCardClassName(anime))}>
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1.5">
                <p className="font-medium">{anime.url ? <a href={anime.url} target="_blank" rel="noopener noreferrer nofollow" className="underline underline-offset-2">{decodeHtmlEntities(anime.name)}</a> : decodeHtmlEntities(anime.name)}</p>
                <div className="flex flex-wrap gap-2"><span className="text-sm text-muted-foreground">{anime.type || 'No type'}</span></div>
              </div>
              <AnimeRowActions anime={anime} />
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

function animeToneClassName(anime: AnimeItem): string {
  if (anime.status === 'completed') {
    return 'border-green-200 bg-green-100/85';
  }
  if (anime.status === 'watching') {
    return 'border-yellow-200 bg-yellow-100/90';
  }
  if (!anime.downloaded) {
    return 'border-slate-200 bg-slate-100/90';
  }
  return 'border-border bg-background';
}

function animeCellClassName(anime: AnimeItem): string {
  return cn('border-y text-foreground', animeToneClassName(anime));
}

function animeCardClassName(anime: AnimeItem): string {
  return animeToneClassName(anime);
}
