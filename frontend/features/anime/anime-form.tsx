'use client';
import type React from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useMutations } from '@/features/anime/hooks';
import type { AnimeItem, AnimeSeason, AnimeStatus } from '@/lib/api/types';
import { animeFormSchema, type AnimeFormValues } from '@/lib/validation/anime';

const seasons: AnimeSeason[] = ['winter', 'spring', 'summer', 'fall', 'other'];
const statuses: AnimeStatus[] = ['unwatched', 'watching', 'completed'];

export function AnimeForm({ initial, mode, onSuccess }: { initial?: Partial<AnimeItem>; mode: 'create' | 'edit'; onSuccess?: () => void }) {
  const router = useRouter();
  const { createAnime, updateAnime } = useMutations();
  const defaultValues = useMemo<AnimeFormValues>(() => ({
    name: initial?.name ?? '',
    year: initial?.year ?? new Date().getFullYear(),
    season: initial?.season ?? 'other',
    status: initial?.status ?? 'unwatched',
    type: initial?.type ?? '',
    comment: initial?.comment ?? '',
    url: initial?.url ?? '',
    downloaded: initial?.downloaded ?? false,
  }), [initial]);

  const form = useForm<AnimeFormValues>({ resolver: zodResolver(animeFormSchema), defaultValues });
  const year = form.watch('year');

  useEffect(() => {
    if (year < 2010) form.setValue('season', 'other');
  }, [form, year]);

  const onSubmit = form.handleSubmit(async (values: AnimeFormValues) => {
    if (mode === 'create') {
      await createAnime.mutateAsync(values);
    } else if (initial?.id) {
      await updateAnime.mutateAsync({ id: initial.id, body: values });
    }
    onSuccess?.();
    router.back();
  });

  const isPending = createAnime.isPending || updateAnime.isPending;
  const serverError = createAnime.error?.message ?? updateAnime.error?.message;

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Name" error={form.formState.errors.name?.message}>
          <Input {...form.register('name')} />
        </Field>
        <Field label="Year" error={form.formState.errors.year?.message}>
          <Input type="number" {...form.register('year', { valueAsNumber: true })} />
        </Field>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Season" error={form.formState.errors.season?.message}>
          <Select value={form.watch('season')} onValueChange={(value) => form.setValue('season', value as AnimeSeason)} disabled={year < 2010}>
            <SelectTrigger><SelectValue placeholder="Select season" /></SelectTrigger>
            <SelectContent>{seasons.map((season) => <SelectItem key={season} value={season}>{season}</SelectItem>)}</SelectContent>
          </Select>
        </Field>
        <Field label="Status" error={form.formState.errors.status?.message}>
          <Select value={form.watch('status')} onValueChange={(value) => form.setValue('status', value as AnimeStatus)}>
            <SelectTrigger><SelectValue placeholder="Select status" /></SelectTrigger>
            <SelectContent>{statuses.map((status) => <SelectItem key={status} value={status}>{status}</SelectItem>)}</SelectContent>
          </Select>
        </Field>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Type" error={form.formState.errors.type?.message}><Input {...form.register('type')} /></Field>
        <Field label="External URL" error={form.formState.errors.url?.message}><Input {...form.register('url')} /></Field>
      </div>
      <Field label="Comment" error={form.formState.errors.comment?.message}><Textarea {...form.register('comment')} /></Field>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" {...form.register('downloaded')} />
        Downloaded
      </label>
      {serverError ? <p className="text-sm text-red-600" role="alert">{serverError}</p> : null}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
        <Button type="submit" disabled={isPending}>{mode === 'create' ? 'Create anime' : 'Save changes'}</Button>
      </div>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      {children}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </div>
  );
}
