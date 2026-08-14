import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ArrowUp,
  Bot,
  BrainCircuit,
  Clock3,
  Lightbulb,
  LoaderCircle,
  Sparkles,
  WandSparkles,
} from "lucide-react";
import { type FormEvent, useState } from "react";

import { GameArt } from "@/components/game-art";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { formatHours } from "@/lib/utils";

const prompts = [
  "今晚只有 90 分钟，推荐一款不用重新学太多操作的游戏",
  "我想轻松一点，从还没启动的游戏里挑三款",
  "找一款有挑战感、但最近还有手感的游戏",
  "把我曾经玩过一点的游戏按重拾价值推荐",
];

export function AssistantPage() {
  const [prompt, setPrompt] = useState("");
  const capabilities = useQuery({ queryKey: ["capabilities"], queryFn: api.capabilities });
  const recommend = useMutation({ mutationFn: (value: string) => api.recommend(value) });

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = prompt.trim();
    if (value.length >= 2) recommend.mutate(value);
  };

  const runPrompt = (value: string) => {
    setPrompt(value);
    recommend.mutate(value);
  };

  return (
    <div className="mx-auto max-w-6xl">
      <div className="text-center">
        <div className="mx-auto flex size-14 items-center justify-center rounded-2xl border border-ai/25 bg-ai/10 text-ai">
          <WandSparkles aria-hidden="true" className="size-6" />
        </div>
        <Badge className="mt-5 border-ai/25 bg-ai/8 text-ai">PERSONAL CURATOR</Badge>
        <h2 className="text-balance mx-auto mt-4 max-w-3xl text-4xl font-semibold tracking-[-0.05em] sm:text-5xl">
          不是更多选择，而是更好的选择。
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-sm leading-6 text-muted sm:text-base">
          描述你今晚的时间、心情或玩法偏好。推荐只会从自己的游戏库中产生。
        </p>
      </div>

      <form onSubmit={submit} className="relative mx-auto mt-9 max-w-3xl">
        <label htmlFor="curator-prompt" className="sr-only">
          告诉策展助手你想玩什么
        </label>
        <textarea
          id="curator-prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          rows={4}
          maxLength={500}
          placeholder="例如：今晚只有一个半小时，我想要有一点挑战但不想重新学习复杂系统…"
          className="min-h-40 w-full resize-none rounded-2xl border border-white/12 bg-surface p-5 pb-16 text-base leading-7 text-foreground shadow-[0_20px_70px_rgba(0,0,0,.18)] outline-none transition focus:border-ai/50 focus:ring-3 focus:ring-ai/15"
        />
        <div className="absolute inset-x-3 bottom-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 pl-2 text-[11px] text-muted">
            {capabilities.data?.llm_configured ? (
              <>
                <BrainCircuit aria-hidden="true" className="size-3.5 text-ai" />
                {capabilities.data.llm_model}
              </>
            ) : (
              <>
                <Lightbulb aria-hidden="true" className="size-3.5 text-brand" />
                本地策展模式
              </>
            )}
          </div>
          <Button
            type="submit"
            size="icon"
            aria-label="生成推荐"
            disabled={prompt.trim().length < 2 || recommend.isPending}
            className="rounded-xl bg-ai text-white hover:bg-ai/90"
          >
            {recommend.isPending ? (
              <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
            ) : (
              <ArrowUp aria-hidden="true" className="size-4" />
            )}
          </Button>
        </div>
      </form>

      {!recommend.data ? (
        <div className="mx-auto mt-6 grid max-w-3xl gap-2 sm:grid-cols-2">
          {prompts.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => runPrompt(item)}
              className="min-h-14 rounded-xl border bg-surface px-4 py-3 text-left text-xs leading-5 text-muted transition-colors hover:border-ai/30 hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ai/50"
            >
              “{item}”
            </button>
          ))}
        </div>
      ) : null}

      <div aria-live="polite" className="mt-10">
        {recommend.isPending ? (
          <div className="flex min-h-64 flex-col items-center justify-center rounded-2xl border border-ai/15 bg-ai/5 text-center">
            <Sparkles aria-hidden="true" className="size-6 animate-pulse text-ai" />
            <p className="mt-4 font-semibold">正在阅读你的游戏脉络…</p>
            <p className="mt-2 text-sm text-muted">只会评估库中已有的候选。</p>
          </div>
        ) : null}

        {recommend.isError ? (
          <div
            role="alert"
            className="rounded-xl border border-danger/20 bg-danger/5 p-5 text-sm text-danger"
          >
            {recommend.error.message}
          </div>
        ) : null}

        {recommend.data ? (
          <section
            aria-labelledby="recommendation-title"
            className="rounded-2xl border bg-surface p-5 sm:p-7"
          >
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge
                    className={
                      recommend.data.generation_mode === "llm_enhanced"
                        ? "border-ai/25 bg-ai/8 text-ai"
                        : "border-brand/25 bg-brand/8 text-brand"
                    }
                  >
                    {recommend.data.generation_mode === "llm_enhanced"
                      ? "AI ENHANCED"
                      : "LOCAL CURATION"}
                  </Badge>
                  {recommend.data.model ? (
                    <span className="font-mono text-[10px] text-muted">{recommend.data.model}</span>
                  ) : null}
                </div>
                <h2
                  id="recommendation-title"
                  className="mt-4 text-2xl font-semibold tracking-[-0.03em] sm:text-3xl"
                >
                  {recommend.data.headline}
                </h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                  {recommend.data.summary}
                </p>
              </div>
              <Bot aria-hidden="true" className="size-6 shrink-0 text-ai" />
            </div>

            <div className="mt-7 grid gap-4 lg:grid-cols-3">
              {recommend.data.picks.map((pick, index) => (
                <article
                  key={pick.game.app_id}
                  className="grid grid-cols-[92px_1fr] gap-4 rounded-xl border bg-background/45 p-3 lg:grid-cols-1"
                >
                  <GameArt
                    src={pick.game.cover_url}
                    alt={`${pick.game.name} 封面`}
                    className="aspect-[2/3] w-[92px] rounded-lg lg:aspect-[16/9] lg:w-full"
                  />
                  <div className="min-w-0 lg:p-2">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-mono text-[9px] font-bold tracking-[0.12em] text-ai">
                          PICK 0{index + 1}
                        </p>
                        <h3 className="mt-1 truncate font-semibold">{pick.game.name}</h3>
                      </div>
                      <span className="font-mono text-xs font-bold text-brand">
                        {pick.fit_score}%
                      </span>
                    </div>
                    <p className="mt-3 text-xs leading-5 text-muted">{pick.reason}</p>
                    <p className="mt-3 flex items-center gap-1.5 text-[11px] text-muted">
                      <Clock3 aria-hidden="true" className="size-3.5" />
                      {formatHours(pick.game.playtime_forever)}
                    </p>
                  </div>
                </article>
              ))}
            </div>

            {recommend.data.fallback_reason ? (
              <p className="mt-5 rounded-lg border border-warning/15 bg-warning/5 px-4 py-3 text-xs leading-5 text-warning">
                {recommend.data.fallback_reason}
              </p>
            ) : null}
          </section>
        ) : null}
      </div>
    </div>
  );
}
