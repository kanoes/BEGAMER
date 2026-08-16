import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowDownAZ,
  ChevronLeft,
  ChevronRight,
  Grid2X2,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";

import { ErrorState } from "@/components/feedback-state";
import { GameCard } from "@/components/game-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { Game, GameStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const filters: Array<{ value: GameStatus | "all"; label: string }> = [
  { value: "all", label: "全部" },
  { value: "recent", label: "最近玩过" },
  { value: "unplayed", label: "从未启动" },
  { value: "backlog", label: "待重拾" },
  { value: "deep", label: "百小时+" },
];

export function LibraryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const status = searchParams.get("status") || "all";
  const query = searchParams.get("q") || "";
  const sort = searchParams.get("sort") || "playtime";
  const page = Math.max(1, Number(searchParams.get("page") || "1"));

  const apiParams = useMemo(() => {
    const params = new URLSearchParams({ page: String(page), page_size: "48", sort });
    if (query) params.set("q", query);
    if (status !== "all") params.set("status", status);
    return params;
  }, [page, query, sort, status]);

  const games = useQuery({
    queryKey: ["games", apiParams.toString()],
    queryFn: () => api.games(apiParams),
    placeholderData: (previous) => previous,
  });
  const favorite = useMutation({
    mutationFn: (game: Game) => api.updateGame(game.app_id, { favorite: !game.favorite }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["games"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
      ]);
    },
  });

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (!value || value === "all") next.delete(key);
    else next.set(key, value);
    if (key !== "page") next.delete("page");
    setSearchParams(next, { replace: true });
  };

  return (
    <div>
      <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
        <div>
          <Badge>THE ARCHIVE</Badge>
          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            你的每一个世界
          </h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-muted">
            搜索、筛选和标记喜欢。所有修改会安全同步到你的 BEGAMER 云端空间。
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted">
          <Grid2X2 aria-hidden="true" className="size-4" />
          {games.data ? `${games.data.total} 款游戏` : "正在整理封面墙"}
        </div>
      </div>

      <div className="sticky top-18 z-20 -mx-4 mt-8 border-y bg-background/92 px-4 py-3 backdrop-blur-xl sm:-mx-6 sm:px-6 lg:mx-0 lg:rounded-xl lg:border lg:px-3">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center">
          <label className="relative block min-w-0 flex-1">
            <span className="sr-only">搜索游戏名</span>
            <Search
              aria-hidden="true"
              className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted"
            />
            <input
              type="search"
              value={query}
              onChange={(event) => updateParam("q", event.target.value)}
              placeholder="输入游戏名…"
              className="h-11 w-full rounded-[10px] border bg-surface pl-10 pr-4 text-sm outline-none transition focus:border-brand/50 focus:ring-3 focus:ring-brand/15"
            />
          </label>
          <fieldset className="flex min-w-0 gap-2 overflow-x-auto pb-1 xl:pb-0">
            <legend className="sr-only">游戏状态筛选</legend>
            {filters.map((filter) => (
              <button
                key={filter.value}
                type="button"
                aria-pressed={status === filter.value}
                onClick={() => updateParam("status", filter.value)}
                className={cn(
                  "min-h-10 shrink-0 rounded-[9px] border px-3.5 text-xs font-semibold text-muted transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand/60",
                  status === filter.value
                    ? "border-brand/40 bg-brand text-brand-ink"
                    : "bg-surface hover:border-white/20 hover:text-foreground",
                )}
              >
                {filter.label}
              </button>
            ))}
          </fieldset>
          <label className="relative flex h-10 items-center gap-2 rounded-[9px] border bg-surface px-3 text-xs font-semibold text-muted">
            <ArrowDownAZ aria-hidden="true" className="size-4" />
            <span className="sr-only">排序方式</span>
            <select
              value={sort}
              onChange={(event) => updateParam("sort", event.target.value)}
              className="appearance-none bg-transparent pr-5 text-foreground outline-none"
            >
              <option value="playtime">游玩时长</option>
              <option value="recent">最近游玩</option>
              <option value="name">名称</option>
              <option value="added">最近入库</option>
            </select>
            <SlidersHorizontal
              aria-hidden="true"
              className="pointer-events-none absolute right-2.5 size-3 text-muted"
            />
          </label>
        </div>
      </div>

      {games.isError ? (
        <div className="mt-8">
          <ErrorState message={games.error.message} retry={() => games.refetch()} />
        </div>
      ) : null}

      {games.isLoading ? (
        <div className="mt-8 grid grid-cols-2 gap-x-3 gap-y-8 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-7">
          {[
            "library-a",
            "library-b",
            "library-c",
            "library-d",
            "library-e",
            "library-f",
            "library-g",
            "library-h",
            "library-i",
            "library-j",
            "library-k",
            "library-l",
            "library-m",
            "library-n",
          ].map((id) => (
            <div key={id}>
              <Skeleton className="aspect-[2/3]" />
              <Skeleton className="mt-3 h-4 w-4/5" />
            </div>
          ))}
        </div>
      ) : null}

      {games.data?.items.length === 0 ? (
        <div className="mt-8 flex min-h-80 flex-col items-center justify-center rounded-2xl border border-dashed p-8 text-center">
          <Search aria-hidden="true" className="size-7 text-muted" />
          <h3 className="mt-4 text-lg font-semibold">没有找到符合条件的游戏</h3>
          <p className="mt-2 text-sm text-muted">换个关键词，或清除当前筛选。</p>
          <Button variant="secondary" className="mt-5" onClick={() => setSearchParams({})}>
            清除筛选
          </Button>
        </div>
      ) : null}

      {games.data && games.data.items.length > 0 ? (
        <div
          className={cn(
            "mt-8 grid grid-cols-2 gap-x-3 gap-y-8 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-7",
            games.isFetching && "opacity-65",
          )}
        >
          {games.data.items.map((game) => (
            <GameCard key={game.app_id} game={game} onFavorite={(item) => favorite.mutate(item)} />
          ))}
        </div>
      ) : null}

      {games.data && games.data.total > games.data.page_size ? (
        <div className="mt-10 flex items-center justify-between border-t pt-6">
          <p className="text-xs text-muted">
            第 {games.data.page} / {Math.ceil(games.data.total / games.data.page_size)} 页
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => updateParam("page", String(page - 1))}
            >
              <ChevronLeft aria-hidden="true" className="size-4" /> 上一页
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= Math.ceil(games.data.total / games.data.page_size)}
              onClick={() => updateParam("page", String(page + 1))}
            >
              下一页 <ChevronRight aria-hidden="true" className="size-4" />
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
