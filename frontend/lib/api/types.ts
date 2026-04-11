export type ScopeKind = 'all' | 'pre2010' | 'year';
export type AnimeStatus = 'unwatched' | 'watching' | 'completed';
export type AnimeSeason = 'winter' | 'spring' | 'summer' | 'fall' | 'other';

export type ScopeInfo = {
  kind: ScopeKind;
  year: number | null;
};

export type AnimeItem = {
  id: number;
  name: string;
  year: number;
  season: AnimeSeason;
  status: AnimeStatus;
  type: string;
  comment: string;
  url: string;
  downloaded: boolean;
  scope: ScopeInfo;
  created_at: string;
  updated_at: string;
};

export type AnimeResponse = { item: AnimeItem };
export type AnimeListResponse = {
  items: AnimeItem[];
  meta: {
    total: number;
    scope: ScopeInfo;
    search: string | null;
  };
};

export type YearListItem = {
  year: number;
  has_entries: boolean;
  has_scaffold: boolean;
  counts: { total: number; completed: number };
};

export type YearListResponse = { items: YearListItem[] };

export type Preferences = {
  last_scope_kind: 'year' | 'pre2010' | 'all';
  last_scope_year: number | null;
  last_used_season: AnimeSeason | null;
  density: 'compact' | 'comfortable';
  theme: 'light' | 'dark' | 'system';
};

export type StatsResponse = {
  totals: { total: number; completed: number; completion_percent: number };
  by_status: Record<AnimeStatus, number>;
  by_type: { type: string; count: number }[];
  by_scope: {
    pre2010: { total: number; completed: number };
    years: { year: number; total: number; completed: number }[];
  };
};

export type RandomPickResponse = {
  item: AnimeItem | null;
  meta: {
    candidate_count: number;
    scope: ScopeInfo;
  };
};

export type ShikimoriInfoResponse = {
  anime_id: number;
  search_key: string;
  cache: { source: string; expires_at: string | null; stale: boolean };
  result: {
    russian: string | null;
    japanese: string | null;
    score: string | null;
    episodes: number | null;
    aired_on: string | null;
    fansubbers: string[];
    studios: string[];
    genres: string[];
    description: string | null;
  };
};

export type CsvImportResponse = {
  summary: {
    total_rows: number;
    inserted: number;
    duplicates_skipped: number;
    invalid_rows: number;
    dry_run: boolean;
  };
  errors: { row_number: number; code: string; message: string }[];
  warnings: { row_number: number; code: string; message: string }[];
};

export type ApiError = {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    request_id?: string;
  };
};
