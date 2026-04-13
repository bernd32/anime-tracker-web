import type {
  AnimeListResponse,
  AnimeResponse,
  CsvImportResponse,
  Preferences,
  RandomPickResponse,
  ShikimoriInfoResponse,
  StatsResponse,
  YearListResponse,
  ApiError,
} from '@/lib/api/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:43968/api/v1';

type RequestOptions = RequestInit & { query?: Record<string, string | number | boolean | undefined | null> };

function buildUrl(path: string, query?: RequestOptions['query']) {
  const url = new URL(`${API_BASE}${path}`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

export class ApiClientError extends Error {
  status: number;
  payload?: ApiError;

  constructor(status: number, message: string, payload?: ApiError) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(buildUrl(path, options.query), {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
      },
      cache: 'no-store',
    });
  } catch (error) {
    throw new ApiClientError(0, 'Network request failed. Check that the API is reachable.', {
      error: {
        code: 'network_error',
        message: error instanceof Error ? error.message : 'Network request failed.',
      },
    });
  }

  if (!response.ok) {
    let payload: ApiError | undefined;
    try {
      payload = (await response.json()) as ApiError;
    } catch {
      payload = undefined;
    }
    throw new ApiClientError(response.status, payload?.error.message ?? 'Request failed', payload);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  if (response.headers.get('content-type')?.includes('text/csv')) {
    return (await response.text()) as T;
  }
  return (await response.json()) as T;
}

export const apiClient = {
  listAnime: (query: RequestOptions['query']) => request<AnimeListResponse>('/anime', { query }),
  getAnime: (id: number) => request<AnimeResponse>(`/anime/${id}`),
  createAnime: (body: object) => request<AnimeResponse>('/anime', { method: 'POST', body: JSON.stringify(body) }),
  updateAnime: (id: number, body: object) => request<AnimeResponse>(`/anime/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteAnime: (id: number) => request<void>(`/anime/${id}`, { method: 'DELETE' }),
  updateStatus: (id: number, status: string) => request<AnimeResponse>(`/anime/${id}/status`, { method: 'POST', body: JSON.stringify({ status }) }),
  updateDownloaded: (id: number, downloaded: boolean) => request<AnimeResponse>(`/anime/${id}/downloaded`, { method: 'POST', body: JSON.stringify({ downloaded }) }),
  getRandomPick: (query: RequestOptions['query']) => request<RandomPickResponse>('/anime/random-pick', { query }),
  getStats: () => request<StatsResponse>('/anime/stats'),
  getYears: () => request<YearListResponse>('/years'),
  deleteYear: (year: number) => request(`/years/${year}`, { method: 'DELETE' }),
  getPreferences: () => request<Preferences>('/preferences'),
  updatePreferences: (body: Partial<Preferences>) => request<Preferences>('/preferences', { method: 'PATCH', body: JSON.stringify(body) }),
  importCsv: (file: File, dryRun: boolean) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<CsvImportResponse>('/import/csv', { method: 'POST', body: formData, query: { dry_run: dryRun } });
  },
  exportCsv: async () => {
    const response = await fetch(buildUrl('/export/csv'), { cache: 'no-store' });
    if (!response.ok) throw new Error('Failed to export CSV');
    return response.blob();
  },
  getShikimori: (id: number, forceRefresh = false) => request<ShikimoriInfoResponse>(`/anime/${id}/shikimori`, { query: { force_refresh: forceRefresh } }),
  resetShikimori: (id: number) => request<void>(`/anime/${id}/shikimori`, { method: 'DELETE' }),
};
