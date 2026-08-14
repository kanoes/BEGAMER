export type GameStatus = "unplayed" | "recent" | "deep" | "backlog";

export interface Account {
  steam_id: string;
  display_name: string;
  profile_url: string | null;
  avatar_url: string | null;
  is_demo: boolean;
  last_synced_at: string | null;
}

export interface Game {
  app_id: number;
  name: string;
  icon_url: string | null;
  cover_url: string;
  hero_url: string;
  playtime_forever: number;
  playtime_2weeks: number;
  last_played_at: string | null;
  achievements_unlocked: number | null;
  achievements_total: number | null;
  tags: string[];
  moods: string[];
  favorite: boolean;
  custom_status: string | null;
  note: string | null;
  status: GameStatus;
}

export interface GameList {
  items: Game[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardStats {
  total_games: number;
  total_hours: number;
  unplayed_games: number;
  recent_games: number;
  deep_games: number;
}

export interface GameShelfData {
  id: string;
  title: string;
  description: string;
  games: Game[];
}

export interface Dashboard {
  account: Account;
  stats: DashboardStats;
  spotlight: Game | null;
  shelves: GameShelfData[];
}

export interface CollectionSuggestion {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  accent: "lime" | "violet" | "blue" | "amber";
  games: Game[];
  total: number;
}

export interface Capabilities {
  steam_configured: boolean;
  llm_configured: boolean;
  llm_model: string;
  active_source: "demo" | "steam";
  steam_write_supported: boolean;
}

export interface RecommendationPick {
  game: Game;
  reason: string;
  fit_score: number;
}

export interface Recommendation {
  headline: string;
  summary: string;
  picks: RecommendationPick[];
  generation_mode: "deterministic" | "llm_enhanced";
  model: string | null;
  fallback_reason: string | null;
}

export interface SyncResult {
  account: Account;
  seen_games: number;
  updated_games: number;
  message: string;
}
