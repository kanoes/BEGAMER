import { useQuery } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, Info, Layers3, LockKeyhole } from "lucide-react";

import { ErrorState } from "@/components/feedback-state";
import { GameArt } from "@/components/game-art";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { CollectionSuggestion } from "@/lib/types";
import { cn } from "@/lib/utils";

const accentStyles: Record<CollectionSuggestion["accent"], string> = {
  lime: "text-brand border-brand/25 bg-brand/8",
  violet: "text-ai border-ai/25 bg-ai/8",
  blue: "text-steam border-steam/25 bg-steam/8",
  amber: "text-warning border-warning/25 bg-warning/8",
};

export function CollectionsPage() {
  const collections = useQuery({ queryKey: ["collections"], queryFn: api.collections });

  return (
    <div>
      <div className="grid gap-6 lg:grid-cols-[1fr_0.55fr] lg:items-end">
        <div>
          <Badge>CURATED SETS</Badge>
          <h2 className="mt-3 text-balance text-3xl font-semibold tracking-[-0.04em] sm:text-5xl">
            让游戏库重新变得有意义。
          </h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-muted sm:text-base">
            这些分类完全由可解释的游玩记录生成。先审核、再导出；每一步都由你决定。
          </p>
        </div>
        <div className="rounded-xl border border-steam/20 bg-steam/5 p-4 text-sm leading-6 text-muted">
          <div className="flex items-start gap-3">
            <LockKeyhole aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-steam" />
            <p>
              <strong className="text-foreground">只生成方案，不会写入 Steam。</strong>
              Steam 没有普通用户可用的 Collection 写入 Web API。
            </p>
          </div>
        </div>
      </div>

      {collections.isError ? (
        <div className="mt-8">
          <ErrorState message={collections.error.message} retry={() => collections.refetch()} />
        </div>
      ) : null}

      {collections.isLoading ? (
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {["collection-a", "collection-b", "collection-c", "collection-d"].map((id) => (
            <Skeleton key={id} className="h-80 rounded-2xl" />
          ))}
        </div>
      ) : null}

      {collections.data ? (
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {collections.data.map((collection) => (
            <CollectionCard key={collection.id} collection={collection} />
          ))}
        </div>
      ) : null}

      <section className="mt-8 grid gap-4 rounded-2xl border bg-surface p-6 sm:grid-cols-3 sm:p-8">
        <ProcessStep
          number="01"
          icon={Layers3}
          title="生成"
          description="按时长、近期记录与状态归类。"
        />
        <ProcessStep
          number="02"
          icon={CheckCircle2}
          title="审核"
          description="确认每一款游戏为什么在这里。"
        />
        <ProcessStep
          number="03"
          icon={Info}
          title="应用"
          description="未来可导出给 Computer Use 执行。"
        />
      </section>
    </div>
  );
}

function CollectionCard({ collection }: { collection: CollectionSuggestion }) {
  return (
    <article className="group overflow-hidden rounded-2xl border bg-surface transition-colors hover:border-white/20">
      <div className="grid h-52 grid-cols-4 gap-1 overflow-hidden bg-raised p-1">
        {collection.games.slice(0, 4).map((game, index) => (
          <GameArt
            key={game.app_id}
            src={game.cover_url}
            alt={`${collection.title} 中的 ${game.name}`}
            className={cn(
              "h-full rounded-md",
              index === 0 && "-rotate-1 scale-[1.03]",
              index === 3 && "rotate-1 scale-[1.03]",
            )}
          />
        ))}
      </div>
      <div className="p-6">
        <div className="flex items-center justify-between gap-4">
          <Badge className={accentStyles[collection.accent]}>{collection.eyebrow}</Badge>
          <span className="font-mono text-xs text-muted">
            {collection.total.toString().padStart(2, "0")} GAMES
          </span>
        </div>
        <h3 className="mt-4 text-2xl font-semibold tracking-[-0.03em]">{collection.title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted">{collection.description}</p>
        <Button variant="ghost" className="mt-4 -ml-4 text-muted group-hover:text-foreground">
          预览分类 <ArrowRight aria-hidden="true" className="size-4" />
        </Button>
      </div>
    </article>
  );
}

function ProcessStep({
  number,
  icon: Icon,
  title,
  description,
}: {
  number: string;
  icon: typeof Layers3;
  title: string;
  description: string;
}) {
  return (
    <div className="border-b pb-5 last:border-b-0 sm:border-b-0 sm:border-r sm:px-5 sm:pb-0 sm:first:pl-0 sm:last:border-r-0">
      <div className="flex items-center justify-between">
        <Icon aria-hidden="true" className="size-5 text-brand" />
        <span className="font-mono text-[10px] font-bold text-muted">{number}</span>
      </div>
      <h3 className="mt-5 font-semibold">{title}</h3>
      <p className="mt-1 text-sm leading-6 text-muted">{description}</p>
    </div>
  );
}
