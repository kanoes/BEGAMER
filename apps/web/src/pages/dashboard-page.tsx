import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, Clock3, Gamepad2, LibraryBig, Sparkles, Trophy } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { ErrorState } from "@/components/feedback-state";
import { GameArt } from "@/components/game-art";
import { GameShelf } from "@/components/game-shelf";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { achievementLabel, formatHours, formatRelativeDate } from "@/lib/utils";

export function DashboardPage() {
  const navigate = useNavigate();
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });

  if (dashboard.isLoading) return <DashboardSkeleton />;
  if (dashboard.isError) {
    return <ErrorState message={dashboard.error.message} retry={() => dashboard.refetch()} />;
  }
  if (!dashboard.data) return null;

  const { account, stats, spotlight, shelves } = dashboard.data;

  return (
    <div>
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="font-mono text-[10px] font-bold tracking-[0.18em] text-brand">
            GOOD EVENING · {account.display_name.toUpperCase()}
          </p>
          <h2 className="mt-2 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            今晚，玩点真正想玩的。
          </h2>
        </div>
        <p className="max-w-sm text-sm leading-6 text-muted">
          {account.is_demo ? "正在使用精心准备的演示游戏库。" : "你的 Steam 游戏库已经接入。"}
          数据只读，规则策展随时可用。
        </p>
      </div>

      {spotlight ? (
        <section
          aria-labelledby="spotlight-title"
          className="relative min-h-[440px] overflow-hidden rounded-2xl border bg-surface sm:min-h-[500px]"
        >
          <GameArt
            src={spotlight.hero_url}
            alt={`${spotlight.name} 主视觉`}
            eager
            className="absolute inset-0 size-full rounded-none"
          />
          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(3,5,8,.96)_0%,rgba(3,5,8,.72)_43%,rgba(3,5,8,.15)_75%),linear-gradient(0deg,rgba(3,5,8,.88)_0%,transparent_50%)]" />
          <div className="relative flex min-h-[440px] max-w-2xl flex-col justify-end p-6 text-white sm:min-h-[500px] sm:p-10 lg:p-12">
            <div className="mb-auto flex items-center gap-2">
              <Badge className="border-brand/30 bg-brand/12 text-brand">TONIGHT'S PICK</Badge>
              {spotlight.playtime_2weeks > 0 ? (
                <Badge className="border-white/15 bg-black/25 text-white/75">正在进行</Badge>
              ) : null}
            </div>
            <h2
              id="spotlight-title"
              className="text-balance text-5xl font-black leading-[0.92] tracking-[-0.065em] sm:text-6xl lg:text-7xl"
            >
              {spotlight.name}
            </h2>
            <p className="mt-5 max-w-xl text-sm leading-6 text-white/70 sm:text-base">
              {spotlight.playtime_2weeks > 0
                ? `最近两周又投入了 ${formatHours(spotlight.playtime_2weeks)}，现在接上手感正合适。`
                : "这款游戏正在你的库里安静等候，也许今晚就是第一次见面的时机。"}
            </p>
            <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs font-semibold text-white/65 sm:text-sm">
              <span className="flex items-center gap-1.5">
                <Clock3 aria-hidden="true" className="size-4" />
                {formatHours(spotlight.playtime_forever)}
              </span>
              <span className="flex items-center gap-1.5">
                <Gamepad2 aria-hidden="true" className="size-4" />
                {formatRelativeDate(spotlight.last_played_at)}
              </span>
              {achievementLabel(spotlight) ? (
                <span className="flex items-center gap-1.5">
                  <Trophy aria-hidden="true" className="size-4" />
                  {achievementLabel(spotlight)}
                </span>
              ) : null}
            </div>
            <div className="mt-7 flex flex-wrap gap-3">
              <a
                href={`steam://run/${spotlight.app_id}`}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] bg-brand px-5 text-sm font-semibold text-brand-ink transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand focus-visible:ring-offset-2 focus-visible:ring-offset-black active:scale-[0.98] motion-reduce:transform-none"
              >
                <Gamepad2 aria-hidden="true" className="size-4" />在 Steam 中启动
              </a>
              <Button variant="secondary" onClick={() => navigate("/assistant")}>
                <Sparkles aria-hidden="true" className="size-4 text-ai" />
                换一个推荐
              </Button>
            </div>
          </div>
        </section>
      ) : null}

      <section
        aria-label="游戏库概览"
        className="mt-4 grid gap-px overflow-hidden rounded-xl border bg-border sm:grid-cols-2 xl:grid-cols-5"
      >
        <StatItem label="游戏总数" value={stats.total_games.toLocaleString()} suffix="款" />
        <StatItem label="累计游玩" value={stats.total_hours.toLocaleString()} suffix="小时" />
        <StatItem label="从未启动" value={stats.unplayed_games.toLocaleString()} suffix="款" />
        <StatItem label="最近两周" value={stats.recent_games.toLocaleString()} suffix="款" />
        <StatItem label="百小时以上" value={stats.deep_games.toLocaleString()} suffix="款" />
      </section>

      <section className="mt-8 grid gap-4 lg:grid-cols-[1fr_0.54fr]">
        <button
          type="button"
          onClick={() => navigate("/assistant")}
          className="group flex min-h-40 items-end justify-between overflow-hidden rounded-2xl border border-ai/25 bg-[radial-gradient(circle_at_15%_0%,color-mix(in_srgb,var(--ai)_22%,transparent),transparent_52%),var(--surface)] p-6 text-left transition-colors hover:border-ai/45 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ai/60 sm:p-7"
        >
          <div>
            <Badge className="border-ai/30 bg-ai/10 text-ai">AI CURATOR</Badge>
            <h2 className="mt-4 text-2xl font-semibold tracking-[-0.03em]">
              告诉我，今晚是什么心情？
            </h2>
            <p className="mt-2 text-sm text-muted">用时间、氛围或玩法约束，从自己的库里找答案。</p>
          </div>
          <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-ai text-white transition-transform group-hover:-translate-y-1 group-hover:translate-x-1 motion-reduce:transform-none">
            <ArrowUpRight aria-hidden="true" className="size-5" />
          </span>
        </button>
        <button
          type="button"
          onClick={() => navigate("/library")}
          className="group flex min-h-40 items-end justify-between rounded-2xl border bg-surface p-6 text-left transition-colors hover:border-white/20 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand/60 sm:p-7"
        >
          <div>
            <Badge>THE ARCHIVE</Badge>
            <h2 className="mt-4 text-xl font-semibold tracking-[-0.03em]">打开完整游戏库</h2>
            <p className="mt-2 text-sm text-muted">搜索、筛选与收藏。</p>
          </div>
          <LibraryBig
            aria-hidden="true"
            className="size-7 text-muted transition-colors group-hover:text-brand"
          />
        </button>
      </section>

      <div className="mt-6 divide-y divide-white/8">
        {shelves.map((shelf) => (
          <GameShelf key={shelf.id} shelf={shelf} />
        ))}
      </div>
    </div>
  );
}

function StatItem({ label, value, suffix }: { label: string; value: string; suffix: string }) {
  return (
    <div className="bg-surface p-5">
      <p className="font-mono text-[9px] font-bold uppercase tracking-[0.16em] text-muted">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold tracking-[-0.04em]">
        {value} <span className="text-xs font-medium text-muted">{suffix}</span>
      </p>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div role="status" aria-label="正在加载今日策展" aria-busy="true">
      <Skeleton className="h-10 w-72" />
      <Skeleton className="mt-6 h-[500px] w-full rounded-2xl" />
      <div className="mt-4 grid grid-cols-2 gap-2 xl:grid-cols-5">
        {["stat-a", "stat-b", "stat-c", "stat-d", "stat-e"].map((id) => (
          <Skeleton key={id} className="h-24" />
        ))}
      </div>
      <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {["game-a", "game-b", "game-c", "game-d", "game-e", "game-f"].map((id) => (
          <Skeleton key={id} className="aspect-[2/3]" />
        ))}
      </div>
    </div>
  );
}
