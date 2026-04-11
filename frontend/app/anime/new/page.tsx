import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AnimeForm } from '@/features/anime/anime-form';

export default function NewAnimePage() {
  return (
    <Card>
      <CardHeader><CardTitle>Add anime</CardTitle></CardHeader>
      <CardContent><AnimeForm mode="create" /></CardContent>
    </Card>
  );
}
