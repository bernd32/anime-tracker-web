import { StatsView } from '@/features/stats/stats-view';

export default function StatsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Statistics</h1>
        <p className="text-sm text-muted-foreground">Overview of totals, completion, and type breakdowns.</p>
      </div>
      <StatsView />
    </div>
  );
}
