'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export function Switch({ checked, onCheckedChange, className }: { checked: boolean; onCheckedChange: (checked: boolean) => void; className?: string }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onCheckedChange(!checked)}
      className={cn('inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:ring-2 focus-visible:ring-ring', checked ? 'bg-primary' : 'bg-muted', className)}
    >
      <span className={cn('block h-5 w-5 rounded-full bg-white transition-transform', checked ? 'translate-x-5' : 'translate-x-0.5')} />
    </button>
  );
}
