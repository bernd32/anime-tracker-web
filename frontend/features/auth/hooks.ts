'use client';

import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export function useAuthSession() {
  return useQuery({
    queryKey: queryKeys.authSession(),
    queryFn: apiClient.getAuthSession,
  });
}
