import { Heart, Play } from "lucide-react";

import { GameArt } from "@/components/game-art";
import { Badge } from "@/components/ui/badge";
import type { Game } from "@/lib/types";
import { achievementLabel, cn, formatHours } from "@/lib/utils";

interface GameCardProps {
  game: Game;
  onFavorite?: (game: Game) => void;
  compact?: boolean;
}

const statusLabel: Record<Game["status"], string> = {
  unplayed: "未启动",
  recent: "近期",
  deep: "深度投入",
  backlog: "待重拾",
};

export function GameCard({ game, onFavorite, compact = false }: GameCardProps) {
  const achievement = achievementLabel(game);

  return (
    <article className="group min-w-0">
      <div
        className={cn(
          "relative overflow-hidden rounded-xl bg-raised transition-transform duration-200 group-hover:-translate-y-0.5 motion-reduce:transform-none",
          compact ? "aspect-[2/3]" : "aspect-[2/3]",
        )}
      >
        <GameArt src={game.cover_url} alt={`${game.name} 封面`} className="size-full" />
        <div className="absolute inset-x-0 bottom-0 flex items-end justify-between bg-gradient-to-t from-black/90 via-black/35 to-transparent p-3 pt-12 opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-within:opacity-100">
          <span className="flex items-center gap-1.5 text-xs font-semibold text-white">
            <Play aria-hidden="true" className="size-3.5 fill-current" />
            {formatHours(game.playtime_forever)}
          </span>
          {onFavorite ? (
            <button
              type="button"
              aria-label={game.favorite ? `取消收藏 ${game.name}` : `收藏 ${game.name}`}
              aria-pressed={game.favorite}
              onClick={() => onFavorite(game)}
              className="flex size-10 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-md transition-colors hover:bg-black/80 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand"
            >
              <Heart
                aria-hidden="true"
                className={cn("size-4", game.favorite && "fill-brand text-brand")}
              />
            </button>
          ) : null}
        </div>
        {game.status === "recent" ? (
          <div className="absolute left-0 top-4 h-8 w-1 rounded-r-full bg-brand shadow-[0_0_20px_var(--brand)]" />
        ) : null}
      </div>
      <div className="mt-3 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h3 className="truncate text-sm font-semibold leading-5 text-foreground">{game.name}</h3>
          {game.favorite ? (
            <Heart aria-label="已收藏" className="mt-0.5 size-3.5 shrink-0 fill-brand text-brand" />
          ) : null}
        </div>
        <div className="mt-1.5 flex items-center gap-2 overflow-hidden text-xs text-muted">
          <Badge className="shrink-0 py-0.5 text-[9px]">{statusLabel[game.status]}</Badge>
          <span className="truncate">{achievement || formatHours(game.playtime_forever)}</span>
        </div>
      </div>
    </article>
  );
}
