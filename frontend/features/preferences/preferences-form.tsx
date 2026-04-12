'use client';
import type React from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';

import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';
import { preferencesSchema, type PreferencesFormValues } from '@/lib/validation/preferences';

export function PreferencesForm() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: queryKeys.preferences(), queryFn: apiClient.getPreferences });
  const mutation = useMutation({
    mutationFn: apiClient.updatePreferences,
    onSuccess: async (data) => {
      queryClient.setQueryData(queryKeys.preferences(), data);
    },
  });

  const form = useForm<PreferencesFormValues>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: query.data ?? {
      last_scope_kind: 'year',
      last_scope_year: null,
      last_used_season: null,
    },
  });

  useEffect(() => {
    if (query.data) {
      form.reset(query.data);
    }
  }, [form, query.data]);

  const onSubmit = form.handleSubmit(async (values: PreferencesFormValues) => {
    await mutation.mutateAsync(values);
  });

  return (
    <form onSubmit={onSubmit} className="grid max-w-xl gap-4">
      <Field label="Last scope kind">
        <Select value={form.watch('last_scope_kind')} onValueChange={(value) => form.setValue('last_scope_kind', value as 'year' | 'pre2010' | 'all')}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="year">Year</SelectItem>
            <SelectItem value="pre2010">Pre-2010</SelectItem>
            <SelectItem value="all">All</SelectItem>
          </SelectContent>
        </Select>
      </Field>
      <Button type="submit" className="w-fit" disabled={mutation.isPending}>Save preferences</Button>
      {mutation.isSuccess ? <p className="text-sm text-green-600">Saved.</p> : null}
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}
