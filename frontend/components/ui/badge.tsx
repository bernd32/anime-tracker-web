import type React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium', {
  variants: {
    variant: {
      default: 'border-transparent bg-primary text-primary-foreground',
      secondary: 'bg-muted text-foreground',
      outline: 'text-foreground',
      success: 'border-transparent bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300',
      warning: 'border-transparent bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300',
    },
  },
  defaultVariants: { variant: 'default' },
});

export function Badge({ className, variant, ...props }: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
