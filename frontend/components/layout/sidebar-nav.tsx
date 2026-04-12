'use client';
import type React from 'react';

import { useQuery } from '@tanstack/react-query';
import type { Route } from 'next';
import Link from 'next/link';

import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import { cn, percent } from '@/lib/utils';

export function SidebarNav({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  const yearsQuery = useQuery({ queryKey: queryKeys.years(), queryFn: apiClient.getYears });

  return (
    <nav className="space-y-6" aria-label="Primary">
      <div className="space-y-1">
        <NavLink href="/years" active={pathname === '/years'} onNavigate={onNavigate}>Dashboard</NavLink>
        <NavLink href="/library/pre-2010" active={pathname === '/library/pre-2010'} onNavigate={onNavigate}>Pre-2010</NavLink>
        <NavLink href="/stats" active={pathname === '/stats'} onNavigate={onNavigate}>Statistics</NavLink>
      </div>
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Years</p>
        <div className="space-y-1">
          {yearsQuery.isLoading ? <div className="text-sm text-muted-foreground">Loading years…</div> : null}
          {yearsQuery.data?.items.map((item) => {
            const completion = percent(item.counts.completed, item.counts.total);
            return (
            <NavLink key={item.year} href={`/library/${item.year}` as Route} active={pathname === `/library/${item.year}`} onNavigate={onNavigate}>
              <span className={cn(completion < 100 && 'font-semibold text-foreground')}>{item.year}</span>
              <span className={cn('text-xs text-muted-foreground', completion < 100 && 'font-semibold text-foreground')}>{completion}%</span>
            </NavLink>
          )})}
          {!yearsQuery.isLoading && !yearsQuery.data?.items.length ? <div className="text-sm text-muted-foreground">No years yet.</div> : null}
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, active, children, onNavigate }: { href: Route; active: boolean; children: React.ReactNode; onNavigate?: () => void }) {
  return (
    <Link href={href} onClick={onNavigate} className={cn('flex items-center justify-between rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent', active && 'bg-accent font-medium')}>
      {children}
    </Link>
  );
}
