import { z } from 'zod';

export const animeFormSchema = z.object({
  name: z.string().trim().min(1).max(255),
  year: z.number().int().min(1960).max(2100),
  season: z.enum(['winter', 'spring', 'summer', 'fall', 'other']),
  status: z.enum(['unwatched', 'watching', 'completed']),
  type: z.string().trim().max(100),
  comment: z.string().max(10000),
  url: z.union([z.literal(''), z.string().url()]).refine((value) => value === '' || /^https?:\/\//.test(value), {
    message: 'URL must use http or https',
  }),
  downloaded: z.boolean(),
}).superRefine((value, ctx) => {
  if (value.year < 2010 && value.season !== 'other') {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['season'], message: 'Pre-2010 entries must use Other season.' });
  }
});

export type AnimeFormValues = z.infer<typeof animeFormSchema>;
