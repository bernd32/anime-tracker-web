import { AnimeScopePage } from '@/components/anime/anime-scope-page';

export default async function YearPage({
  params,
  searchParams,
}: {
  params: Promise<{ year: string }>;
  searchParams: Promise<{ search?: string }>;
}) {
  const { year: yearParam } = await params;
  const { search } = await searchParams;
  const year = Number(yearParam);

  return <AnimeScopePage title={`${year}`} description={`Anime grouped by season for ${year}.`} scopeKind="year" scopeYear={year} search={search ?? ''} />;
}
