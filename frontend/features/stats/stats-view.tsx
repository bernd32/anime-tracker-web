'use client';

import { useQuery } from '@tanstack/react-query';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function StatsView() {
  const query = useQuery({ queryKey: queryKeys.stats(), queryFn: apiClient.getStats });

  if (query.isLoading) return <Skeleton className="h-40 w-full" />;
  if (query.isError) return <p className="text-sm text-red-600">{query.error.message}</p>;
  if (!query.data) return <Skeleton className="h-40 w-full" />;

  const data = query.data;
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader><CardTitle>Overview</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Total anime: {data.totals.total}</p>
          <p>Completed: {data.totals.completed}</p>
          <p>Completion: {data.totals.completion_percent}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>By status</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          {Object.entries(data.by_status).map(([key, value]) => <p key={key}>{key}: {value}</p>)}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>By type</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          {data.by_type.map((entry) => <p key={`${entry.type}-${entry.count}`}>{entry.type || 'None'}: {entry.count}</p>)}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Year breakdown</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Pre-2010: {data.by_scope.pre2010.completed} / {data.by_scope.pre2010.total}</p>
          {data.by_scope.years.map((entry) => <p key={entry.year}>{entry.year}: {entry.completed} / {entry.total}</p>)}
        </CardContent>
      </Card>
    </div>
  );
}
