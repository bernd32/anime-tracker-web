'use client';

import { MoreHorizontal } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

import { ShikimoriSheet } from '@/features/anime/shikimori-sheet';
import { useMutations } from '@/features/anime/hooks';
import type { AnimeItem } from '@/lib/api/types';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

export function AnimeRowActions({ anime }: { anime: AnimeItem }) {
  const { updateStatus, updateDownloaded, deleteAnime } = useMutations();
  const [openInfo, setOpenInfo] = useState(false);

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" aria-label={`Actions for ${anime.name}`}>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <Link href={`/anime/${anime.id}/edit`}>Edit</Link>
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => setOpenInfo(true)}>Shikimori info</DropdownMenuItem>
          <DropdownMenuItem onSelect={() => updateDownloaded.mutate({ id: anime.id, downloaded: !anime.downloaded })}>
            {anime.downloaded ? 'Mark not downloaded' : 'Mark downloaded'}
          </DropdownMenuItem>
          {anime.status !== 'watching' ? <DropdownMenuItem onSelect={() => updateStatus.mutate({ id: anime.id, status: 'watching' })}>Set watching</DropdownMenuItem> : null}
          {anime.status !== 'completed' ? <DropdownMenuItem onSelect={() => updateStatus.mutate({ id: anime.id, status: 'completed' })}>Set completed</DropdownMenuItem> : null}
          {anime.status !== 'unwatched' ? <DropdownMenuItem onSelect={() => updateStatus.mutate({ id: anime.id, status: 'unwatched' })}>Set unwatched</DropdownMenuItem> : null}
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-red-600" onSelect={() => deleteAnime.mutate(anime.id)}>Delete</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <ShikimoriSheet anime={anime} open={openInfo} onOpenChange={setOpenInfo} />
    </>
  );
}
