'use client';

import type React from 'react';
import Link from 'next/link';
import { useState } from 'react';

import { ShikimoriSheet } from '@/features/anime/shikimori-sheet';
import { useMutations } from '@/features/anime/hooks';
import type { AnimeItem } from '@/lib/api/types';
import { Button } from '@/components/ui/button';
import { cn, decodeHtmlEntities } from '@/lib/utils';

export function AnimeRowActions({ anime }: { anime: AnimeItem }) {
  const { updateStatus, updateDownloaded, deleteAnime } = useMutations();
  const [openInfo, setOpenInfo] = useState(false);
  const animeName = decodeHtmlEntities(anime.name);
  const watchingLabel = anime.status === 'watching' ? 'Unset watching' : 'Set watching';
  const watchingStatus = anime.status === 'watching' ? 'unwatched' : 'watching';
  const completedLabel = anime.status === 'completed' ? 'Set unwatched' : 'Set completed';
  const completedStatus = anime.status === 'completed' ? 'unwatched' : 'completed';

  return (
    <>
      <div className="flex flex-nowrap items-center justify-end gap-2">
        <ActionButton
          asChild
          emoji="✏️"
          label={`Edit ${animeName}`}
        >
          <Link href={`/anime/${anime.id}/edit`}>
            <span aria-hidden="true">✏️</span>
          </Link>
        </ActionButton>
        <ActionButton
          emoji="ℹ️"
          label={`Open Shikimori info for ${animeName}`}
          onClick={() => setOpenInfo(true)}
        />
        <ActionButton
          emoji="⬇️"
          label={anime.downloaded ? `Mark ${animeName} as not downloaded` : `Mark ${animeName} as downloaded`}
          onClick={() => updateDownloaded.mutate({ id: anime.id, downloaded: !anime.downloaded })}
          disabled={updateDownloaded.isPending}
        />
        <ActionButton
          emoji="👀"
          label={`${watchingLabel} for ${animeName}`}
          onClick={() => updateStatus.mutate({ id: anime.id, status: watchingStatus })}
          disabled={updateStatus.isPending}
        />
        <ActionButton
          emoji="✅"
          label={`${completedLabel} for ${animeName}`}
          onClick={() => updateStatus.mutate({ id: anime.id, status: completedStatus })}
          disabled={updateStatus.isPending}
        />
        <ActionButton
          emoji="🗑️"
          label={`Delete ${animeName}`}
          onClick={() => deleteAnime.mutate(anime.id)}
          disabled={deleteAnime.isPending}
          destructive
        />
      </div>
      <ShikimoriSheet anime={anime} open={openInfo} onOpenChange={setOpenInfo} />
    </>
  );
}

function ActionButton({
  asChild = false,
  children,
  destructive = false,
  emoji,
  label,
  ...props
}: React.ComponentProps<typeof Button> & {
  children?: React.ReactNode;
  emoji: string;
  label: string;
  destructive?: boolean;
}) {
  return (
    <Button
      asChild={asChild}
      type={asChild ? undefined : 'button'}
      variant="ghost"
      size="icon"
      className={cn(
        'h-10 w-10 rounded-xl border border-border/70 bg-background/80 text-lg shadow-sm backdrop-blur-sm hover:bg-background',
        destructive && 'border-red-200 bg-red-50 hover:bg-red-100',
      )}
      title={label}
      aria-label={label}
      {...props}
    >
      {children ?? <span aria-hidden="true">{emoji}</span>}
    </Button>
  );
}
