'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function useAnimeList(params: Record<string, string | number | boolean | undefined>) {
  return useQuery({
    queryKey: queryKeys.animeList(params),
    queryFn: () => apiClient.listAnime(params),
  });
}

export function useAnime(id: number) {
  return useQuery({ queryKey: queryKeys.anime(id), queryFn: () => apiClient.getAnime(id), enabled: Number.isFinite(id) });
}

export function useMutations() {
  const queryClient = useQueryClient();
  const invalidateStructure = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['anime'] }),
      queryClient.invalidateQueries({ queryKey: ['random-pick'] }),
      queryClient.invalidateQueries({ queryKey: queryKeys.years() }),
      queryClient.invalidateQueries({ queryKey: queryKeys.stats() }),
    ]);
  };

  return {
    createAnime: useMutation({
      mutationFn: apiClient.createAnime,
      onSuccess: invalidateStructure,
    }),
    updateAnime: useMutation({
      mutationFn: ({ id, body }: { id: number; body: object }) => apiClient.updateAnime(id, body),
      onSuccess: async (data) => {
        queryClient.setQueryData(queryKeys.anime(data.item.id), data);
        await invalidateStructure();
      },
    }),
    deleteAnime: useMutation({
      mutationFn: apiClient.deleteAnime,
      onSuccess: async (_, id) => {
        queryClient.removeQueries({ queryKey: queryKeys.anime(id) });
        await invalidateStructure();
      },
    }),
    updateStatus: useMutation({
      mutationFn: ({ id, status }: { id: number; status: string }) => apiClient.updateStatus(id, status),
      onSuccess: async (data) => {
        queryClient.setQueryData(queryKeys.anime(data.item.id), data);
        await invalidateStructure();
      },
    }),
    updateDownloaded: useMutation({
      mutationFn: ({ id, downloaded }: { id: number; downloaded: boolean }) => apiClient.updateDownloaded(id, downloaded),
      onSuccess: async (data) => {
        queryClient.setQueryData(queryKeys.anime(data.item.id), data);
        await invalidateStructure();
      },
    }),
  };
}
