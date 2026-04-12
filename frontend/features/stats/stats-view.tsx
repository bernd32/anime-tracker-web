'use client';

import { useQuery } from '@tanstack/react-query';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import { percent } from '@/lib/utils';

const STATUS_COLORS = ['#94a3b8', '#facc15', '#4ade80'];
const BAR_COLOR = '#60a5fa';

export function StatsView() {
  const query = useQuery({ queryKey: queryKeys.stats(), queryFn: apiClient.getStats });

  if (query.isLoading) return <Skeleton className="h-72 w-full" />;
  if (query.isError) return <p className="text-sm text-red-600">{query.error.message}</p>;
  if (!query.data) return <Skeleton className="h-72 w-full" />;

  const data = query.data;
  const statusData = [
    { name: 'Unwatched', value: data.by_status.unwatched },
    { name: 'Watching', value: data.by_status.watching },
    { name: 'Completed', value: data.by_status.completed },
  ].filter((entry) => entry.value > 0);
  const yearData = data.by_scope.years.map((entry) => ({
    year: String(entry.year),
    total: entry.total,
    completed: entry.completed,
    completion: percent(entry.completed, entry.total),
  }));
  const topTypes = data.by_type.slice(0, 6);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total anime" value={String(data.totals.total)} note="All entries in the library" />
        <StatCard label="Completed" value={String(data.totals.completed)} note="Finished anime count" />
        <StatCard label="Completion" value={`${data.totals.completion_percent}%`} note="Across the whole library" />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.05fr_1.45fr]">
        <Card className="overflow-hidden">
          <CardHeader className="pb-2">
            <CardTitle>Status Distribution</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-5">
            <div className="h-72 w-full max-w-sm">
              {statusData.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={70}
                      outerRadius={100}
                      paddingAngle={3}
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`${entry.name}-${entry.value}`} fill={STATUS_COLORS[index % STATUS_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<StatsTooltip suffix=" anime" />} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChartState />
              )}
            </div>
            <div className="flex w-full max-w-md flex-wrap items-center justify-center gap-3">
              {statusData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-3 rounded-full border border-border/70 bg-muted/35 px-4 py-2">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: STATUS_COLORS[index % STATUS_COLORS.length] }}
                    aria-hidden="true"
                  />
                  <span className="text-sm font-medium">{entry.name}</span>
                  <span className="text-sm text-muted-foreground">{entry.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden">
          <CardHeader className="pb-2">
            <CardTitle>Completed By Year</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="h-80">
              {yearData.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={yearData} margin={{ top: 8, right: 8, left: -18, bottom: 8 }}>
                    <CartesianGrid vertical={false} strokeDasharray="3 3" />
                    <XAxis dataKey="year" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip content={<StatsTooltip suffix=" completed" />} />
                    <Bar dataKey="completed" radius={[8, 8, 0, 0]} fill={BAR_COLOR} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChartState />
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {yearData.slice(0, 6).map((entry) => (
                <div key={entry.year} className="rounded-xl border border-border/70 bg-muted/35 px-4 py-3">
                  <p className="text-sm font-medium">{entry.year}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{entry.completed} completed of {entry.total}</p>
                  <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">{entry.completion}% complete</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>By Type</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {topTypes.length ? topTypes.map((entry) => {
              const width = percent(entry.count, data.totals.total);
              return (
                <div key={`${entry.type}-${entry.count}`} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{entry.type || 'Other'}</span>
                    <span className="text-muted-foreground">{entry.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-sky-400 to-blue-500"
                      style={{ width: `${width}%` }}
                      aria-hidden="true"
                    />
                  </div>
                </div>
              );
            }) : <EmptyInlineState label="No type data yet." />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Pre-2010</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-3xl font-semibold tracking-tight">{percent(data.by_scope.pre2010.completed, data.by_scope.pre2010.total)}%</p>
              <p className="text-sm text-muted-foreground">{data.by_scope.pre2010.completed} completed of {data.by_scope.pre2010.total}</p>
            </div>
            <div className="h-4 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-amber-300 to-orange-400"
                style={{ width: `${percent(data.by_scope.pre2010.completed, data.by_scope.pre2010.total)}%` }}
                aria-hidden="true"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ label, note, value }: { label: string; note: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tracking-tight">{value}</p>
        <p className="mt-1 text-sm text-muted-foreground">{note}</p>
      </CardContent>
    </Card>
  );
}

function EmptyChartState() {
  return (
    <div className="flex h-full items-center justify-center rounded-2xl border border-dashed text-sm text-muted-foreground">
      No data yet.
    </div>
  );
}

function EmptyInlineState({ label }: { label: string }) {
  return <p className="text-sm text-muted-foreground">{label}</p>;
}

function StatsTooltip({ active, payload, label, suffix = '' }: { active?: boolean; payload?: Array<{ value?: number | string }>; label?: string; suffix?: string }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border bg-background px-3 py-2 text-sm shadow-md">
      {label ? <p className="font-medium">{label}</p> : null}
      <p className="text-muted-foreground">{payload[0]?.value}{suffix}</p>
    </div>
  );
}
