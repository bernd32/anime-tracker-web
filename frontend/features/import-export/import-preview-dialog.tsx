'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function ImportCsvDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (value: boolean) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const queryClient = useQueryClient();
  const dryRunMutation = useMutation({ mutationFn: (selected: File) => apiClient.importCsv(selected, true) });
  const importMutation = useMutation({
    mutationFn: (selected: File) => apiClient.importCsv(selected, false),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['anime'] }),
        queryClient.invalidateQueries({ queryKey: queryKeys.years() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.stats() }),
      ]);
    },
  });

  const preview = async () => {
    if (!file) return;
    await dryRunMutation.mutateAsync(file);
  };
  const importNow = async () => {
    if (!file) return;
    await importMutation.mutateAsync(file);
  };

  const result = importMutation.data ?? dryRunMutation.data;
  const error = importMutation.error ?? dryRunMutation.error;

  useEffect(() => {
    if (!open) {
      setFile(null);
      dryRunMutation.reset();
      importMutation.reset();
    }
    // Intentionally keyed only to dialog visibility so closing the dialog
    // clears transient state once instead of on every render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Import CSV</DialogTitle>
          <DialogDescription>Upload a CSV file. Use preview first to validate legacy rows and duplicates.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="csv-file" className="text-sm font-medium">CSV file</label>
            <Input id="csv-file" type="file" accept=".csv,text/csv" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="outline" onClick={preview} disabled={!file || dryRunMutation.isPending}>Preview</Button>
            <Button type="button" onClick={importNow} disabled={!file || importMutation.isPending}>Import</Button>
          </div>
          {error ? <p className="text-sm text-red-600" role="alert">{error.message}</p> : null}
          {result ? (
            <div className="space-y-3 rounded-lg border p-4 text-sm" aria-live="polite">
              <p>Rows: {result.summary.total_rows}</p>
              <p>Would insert / inserted: {result.summary.inserted}</p>
              <p>Duplicates skipped: {result.summary.duplicates_skipped}</p>
              <p>Invalid rows: {result.summary.invalid_rows}</p>
              {result.errors.length ? <><Separator /><div className="space-y-2"><p className="font-medium">Errors</p>{result.errors.map((issue) => <p key={`${issue.row_number}-${issue.message}`} className="text-red-600">Row {issue.row_number}: {issue.message}</p>)}</div></> : null}
              {result.warnings.length ? <><Separator /><div className="space-y-2"><p className="font-medium">Warnings</p>{result.warnings.map((issue) => <p key={`${issue.row_number}-${issue.code}-${issue.message}`} className="text-amber-600">Row {issue.row_number}: {issue.message}</p>)}</div></> : null}
            </div>
          ) : null}
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
