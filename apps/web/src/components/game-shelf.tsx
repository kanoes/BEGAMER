import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { GameCard } from "@/components/game-card";
import type { GameShelfData } from "@/lib/types";

export function GameShelf({ shelf }: { shelf: GameShelfData }) {
  if (shelf.games.length === 0) return null;

  return (
    <section aria-labelledby={`shelf-${shelf.id}`} className="py-4 md:py-6">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2
            id={`shelf-${shelf.id}`}
            className="text-xl font-semibold tracking-[-0.02em] md:text-2xl"
          >
            {shelf.title}
          </h2>
          <p className="mt-1 text-sm text-muted">{shelf.description}</p>
        </div>
        <Link
          to={`/library?status=${shelf.id === "continue" ? "recent" : shelf.id === "unplayed" ? "unplayed" : "backlog"}`}
          className="hidden min-h-11 items-center gap-1 text-sm font-semibold text-muted transition-colors hover:text-foreground focus-visible:rounded-md focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand sm:flex"
        >
          查看全部 <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
      <div className="grid grid-cols-2 gap-x-3 gap-y-7 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-7">
        {shelf.games.slice(0, 7).map((game) => (
          <GameCard key={game.app_id} game={game} compact />
        ))}
      </div>
    </section>
  );
}
