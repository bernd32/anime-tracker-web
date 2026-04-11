'use client';
import type React from 'react';
import { Menu } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Suspense, useState } from 'react';

import { GlobalSearch } from '@/components/layout/global-search';
import { SidebarNav } from '@/components/layout/sidebar-nav';
import { ImportExportMenu } from '@/features/import-export/import-export-menu';
import { AddAnimeButton } from '@/features/anime/add-anime-button';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setMobileOpen((v) => !v)} aria-label="Open navigation">
            <Menu className="h-5 w-5" />
          </Button>
          <Link href="/years" className="text-lg font-semibold tracking-tight">Anime Backlog</Link>
          <div className="min-w-0 flex-1">
            <Suspense fallback={<SearchFallback />}>
              <GlobalSearch />
            </Suspense>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <ImportExportMenu />
            <AddAnimeButton />
            <Link href="/settings" className="text-sm text-muted-foreground hover:text-foreground">Settings</Link>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 lg:px-6">
        <aside className={cn('fixed inset-y-0 left-0 z-20 w-72 border-r bg-background p-4 transition-transform lg:static lg:translate-x-0 lg:border-r-0 lg:p-0', mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
          <div className="lg:hidden">
            <div className="flex items-center justify-between pb-4">
              <span className="font-semibold">Navigation</span>
              <Button variant="ghost" size="sm" onClick={() => setMobileOpen(false)}>Close</Button>
            </div>
            <Separator className="mb-4" />
          </div>
          <SidebarNav pathname={pathname} onNavigate={() => setMobileOpen(false)} />
        </aside>
        {mobileOpen ? <div className="fixed inset-0 z-10 bg-black/30 lg:hidden" onClick={() => setMobileOpen(false)} aria-hidden="true" /> : null}
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}

function SearchFallback() {
  return <div className="h-9 w-full max-w-xl rounded-md border bg-transparent" aria-hidden="true" />;
}
