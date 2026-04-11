import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function percent(completed: number, total: number): number {
  if (!total) return 0;
  return Math.round((completed / total) * 100);
}

export function titleCaseSeason(value: string): string {
  return value === 'other' ? 'Other' : value.charAt(0).toUpperCase() + value.slice(1);
}
