'use client';

import { Download, Upload } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useRequireOwnerAction } from '@/features/auth/require-owner-action';
import { ImportCsvDialog } from '@/features/import-export/import-preview-dialog';
import { apiClient } from '@/lib/api/client';

export function ImportExportMenu() {
  const [openImport, setOpenImport] = useState(false);
  const { requireOwnerAction } = useRequireOwnerAction();

  const download = async () => {
    const blob = await apiClient.exportCsv();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'anime_backlog.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">Import / Export</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onSelect={() => {
            if (requireOwnerAction()) setOpenImport(true);
          }}>
            <Upload className="mr-2 h-4 w-4" />Import CSV
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => {
            if (requireOwnerAction()) void download();
          }}>
            <Download className="mr-2 h-4 w-4" />Export CSV
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <ImportCsvDialog open={openImport} onOpenChange={setOpenImport} />
    </>
  );
}
