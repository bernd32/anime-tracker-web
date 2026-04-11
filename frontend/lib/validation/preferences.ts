import { z } from 'zod';

export const preferencesSchema = z.object({
  density: z.enum(['compact', 'comfortable']),
  theme: z.enum(['light', 'dark', 'system']),
  last_scope_kind: z.enum(['year', 'pre2010', 'all']),
  last_scope_year: z.number().int().min(1960).max(2100).nullable(),
  last_used_season: z.enum(['winter', 'spring', 'summer', 'fall', 'other']).nullable(),
});

export type PreferencesFormValues = z.infer<typeof preferencesSchema>;
