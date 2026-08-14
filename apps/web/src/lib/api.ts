import type {
  Capabilities,
  CollectionSuggestion,
  Dashboard,
  Game,
  GameList,
  Recommendation,
  SyncResult,
} from "@/lib/types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(
  /\/$/,
  "",
);
const API_PREFIX = `${API_BASE_URL}/api/v1`;

interface ApiErrorShape {
  detail?: string;
  error?: { message?: string };
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiErrorShape;
    throw new ApiError(
      payload.error?.message || payload.detail || "请求没有成功，请稍后重试。",
      response.status,
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/dashboard"),
  capabilities: () => request<Capabilities>("/capabilities"),
  games: (search: URLSearchParams) => request<GameList>(`/games?${search.toString()}`),
  collections: () => request<CollectionSuggestion[]>("/collections"),
  updateGame: (appId: number, body: Partial<Pick<Game, "favorite" | "custom_status" | "note">>) =>
    request<Game>(`/games/${appId}`, { method: "PATCH", body: JSON.stringify(body) }),
  recommend: (prompt: string, preferUnplayed = false) =>
    request<Recommendation>("/recommendations", {
      method: "POST",
      body: JSON.stringify({ prompt, prefer_unplayed: preferUnplayed, max_results: 3 }),
    }),
  syncSteam: (steamId: string) =>
    request<SyncResult>("/steam/sync", {
      method: "POST",
      body: JSON.stringify({ steam_id: steamId || null }),
    }),
  useDemo: () => request("/steam/demo", { method: "POST", body: "{}" }),
};
