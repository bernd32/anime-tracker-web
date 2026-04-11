import { Badge } from '@/components/ui/badge';
import type { AnimeStatus } from '@/lib/api/types';

export function StatusBadge({ status }: { status: AnimeStatus }) {
  if (status === 'completed') return <Badge variant="success">Completed</Badge>;
  if (status === 'watching') return <Badge variant="warning">Watching</Badge>;
  return <Badge variant="secondary">Unwatched</Badge>;
}
