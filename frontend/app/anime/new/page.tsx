import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AnimeForm } from '@/features/anime/anime-form';

export default async function NewAnimePage({
  searchParams,
}: {
  searchParams: Promise<{ year?: string }>;
}) {
  const { year: yearParam } = await searchParams;
  const parsedYear = Number(yearParam);
  const year = Number.isInteger(parsedYear) ? parsedYear : new Date().getFullYear();

  return (
    <Card>
      <CardHeader><CardTitle>Add anime</CardTitle></CardHeader>
      <CardContent><AnimeForm mode="create" initial={{ year, type: 'TV' }} /></CardContent>
    </Card>
  );
}
