import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useMutations } from '@/features/anime/hooks';
import { queryKeys } from '@/lib/query/keys';

const apiClientMock = vi.hoisted(() => ({
  createAnime: vi.fn(),
  updateAnime: vi.fn(),
  deleteAnime: vi.fn(),
  updateStatus: vi.fn(),
  updateDownloaded: vi.fn(),
}));

vi.mock('@/lib/api/client', () => ({
  apiClient: apiClientMock,
}));

function createWrapper(queryClient: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('useMutations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('invalidates list, years, stats, and random-pick queries after create', async () => {
    const queryClient = new QueryClient();
    const invalidateQueries = vi.spyOn(queryClient, 'invalidateQueries');
    apiClientMock.createAnime.mockResolvedValue({
      item: { id: 1 },
    });

    const { result } = renderHook(() => useMutations(), {
      wrapper: createWrapper(queryClient),
    });

    await act(async () => {
      await result.current.createAnime.mutateAsync({ name: 'Frieren' });
    });

    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['anime'] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['random-pick'] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: queryKeys.years() });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: queryKeys.stats() });
  });

  it('updates the anime detail cache and removes it on delete', async () => {
    const queryClient = new QueryClient();
    const setQueryData = vi.spyOn(queryClient, 'setQueryData');
    const removeQueries = vi.spyOn(queryClient, 'removeQueries');
    apiClientMock.updateAnime.mockResolvedValue({
      item: { id: 7, name: 'Frieren' },
    });
    apiClientMock.deleteAnime.mockResolvedValue(undefined);

    const { result } = renderHook(() => useMutations(), {
      wrapper: createWrapper(queryClient),
    });

    await act(async () => {
      await result.current.updateAnime.mutateAsync({ id: 7, body: { name: 'Frieren' } });
    });
    expect(setQueryData).toHaveBeenCalledWith(queryKeys.anime(7), {
      item: { id: 7, name: 'Frieren' },
    });

    await act(async () => {
      await result.current.deleteAnime.mutateAsync(7);
    });
    expect(removeQueries).toHaveBeenCalledWith({ queryKey: queryKeys.anime(7) });
  });
});
