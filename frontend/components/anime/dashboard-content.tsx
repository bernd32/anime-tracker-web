'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import { percent } from '@/lib/utils';

export function DashboardContent() {
  const yearsQuery = useQuery({ queryKey: queryKeys.years(), queryFn: apiClient.getYears });
  const statsQuery = useQuery({ queryKey: queryKeys.stats(), queryFn: apiClient.getStats });

  if (yearsQuery.isLoading || statsQuery.isLoading) return <Skeleton className="h-72 w-full" />;
  if (yearsQuery.isError) return <p className="text-sm text-red-600">{yearsQuery.error.message}</p>;
  if (statsQuery.isError) return <p className="text-sm text-red-600">{statsQuery.error.message}</p>;
  if (!yearsQuery.data || !statsQuery.data) return <Skeleton className="h-72 w-full" />;

  const years = yearsQuery.data.items;
  const stats = statsQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Quick access to your anime backlog by year and statistics.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader><CardTitle>Total anime</CardTitle></CardHeader><CardContent>{stats.totals.total}</CardContent></Card>
        <Card><CardHeader><CardTitle>Completed</CardTitle></CardHeader><CardContent>{stats.totals.completed}</CardContent></Card>
        <Card><CardHeader><CardTitle>Completion</CardTitle></CardHeader><CardContent>{stats.totals.completion_percent}%</CardContent></Card>
      </div>
      <Card>
        <CardHeader><CardTitle>Years</CardTitle></CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {years.map((item) => (
            <Link key={item.year} href={`/library/${item.year}`} className="rounded-lg border p-4 transition hover:bg-accent">
              <div className="flex items-center justify-between">
                <h2 className="font-medium">{item.year}</h2>
                <span className="text-sm text-muted-foreground">{percent(item.counts.completed, item.counts.total)}%</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{item.counts.completed} completed of {item.counts.total}</p>
            </Link>
          ))}
          {!years.length ? <p className="text-sm text-muted-foreground">No year pages yet. Create a year scaffold after adding your first anime.</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}
