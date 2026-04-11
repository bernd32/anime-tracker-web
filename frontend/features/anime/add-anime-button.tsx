import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function AddAnimeButton() {
  return (
    <Button asChild>
      <Link href="/anime/new"><Plus className="h-4 w-4" />Add anime</Link>
    </Button>
  );
}
