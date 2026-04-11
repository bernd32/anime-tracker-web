import { animeFormSchema } from '@/lib/validation/anime';

describe('animeFormSchema', () => {
  it('forces pre-2010 season to other', () => {
    const result = animeFormSchema.safeParse({
      name: 'Nana',
      year: 2006,
      season: 'spring',
      status: 'unwatched',
      type: 'TV',
      comment: '',
      url: '',
      downloaded: false,
    });
    expect(result.success).toBe(false);
  });
});
