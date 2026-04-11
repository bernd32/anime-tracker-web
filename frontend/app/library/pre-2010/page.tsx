import { AnimeScopePage } from '@/components/anime/anime-scope-page';

export default async function Pre2010Page({ searchParams }: { searchParams: Promise<{ search?: string }> }) {
  const { search } = await searchParams;
  return <AnimeScopePage title="Pre-2010" description="All anime released before 2010." scopeKind="pre2010" search={search ?? ''} />;
}
