export const queryKeys = {
  years: () => ['years'] as const,
  preferences: () => ['preferences'] as const,
  stats: () => ['stats'] as const,
  animeList: (params: Record<string, unknown>) => ['anime', 'list', params] as const,
  anime: (id: number) => ['anime', id] as const,
  randomPick: (params: Record<string, unknown>) => ['random-pick', params] as const,
  shikimori: (id: number) => ['shikimori', id] as const,
};
