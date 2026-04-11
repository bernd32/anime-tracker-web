'use client';

import { Search } from 'lucide-react';
import type { Route } from 'next';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { Input } from '@/components/ui/input';

export function GlobalSearch() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [value, setValue] = useState(searchParams.get('search') ?? '');

  useEffect(() => {
    setValue(searchParams.get('search') ?? '');
  }, [searchParams]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString());
      if (value.trim()) {
        params.set('search', value.trim());
      } else {
        params.delete('search');
      }
      const query = params.toString();
      const nextUrl = query ? `${pathname}?${query}` : pathname;
      const currentUrl = searchParams.toString() ? `${pathname}?${searchParams.toString()}` : pathname;
      if (nextUrl !== currentUrl) {
        router.replace(nextUrl as Route, { scroll: false });
      }
    }, 250);
    return () => window.clearTimeout(handle);
  }, [pathname, router, searchParams, value]);

  return (
    <div className="relative max-w-xl" role="search">
      <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input value={value} onChange={(event) => setValue(event.target.value)} placeholder="Search by anime name" className="pl-9" aria-label="Search by anime name" />
    </div>
  );
}
