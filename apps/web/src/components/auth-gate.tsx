import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Gamepad2, KeyRound, LibraryBig, ShieldCheck, Sparkles } from "lucide-react";
import { type ReactNode, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError, api } from "@/lib/api";
import type { AuthConfig } from "@/lib/types";

interface GoogleCredentialResponse {
  credential: string;
}

interface GoogleIdentityApi {
  initialize: (options: {
    client_id: string;
    callback: (response: GoogleCredentialResponse) => void;
    auto_select?: boolean;
    cancel_on_tap_outside?: boolean;
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options: {
      type: "standard";
      theme: "filled_black";
      size: "large";
      shape: "pill";
      text: "continue_with";
      width: number;
    },
  ) => void;
}

declare global {
  interface Window {
    google?: { accounts: { id: GoogleIdentityApi } };
  }
}

function GoogleButton({ config }: { config: AuthConfig }) {
  const buttonRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const [scriptReady, setScriptReady] = useState(Boolean(window.google));
  const [scriptError, setScriptError] = useState(false);
  const login = useMutation({
    mutationFn: api.googleLogin,
    onSuccess: (user) => {
      queryClient.setQueryData(["auth", "me"], user);
    },
  });

  useEffect(() => {
    if (window.google) {
      setScriptReady(true);
      return;
    }
    const existing = document.querySelector<HTMLScriptElement>("script[data-begamer-google]");
    const script = existing ?? document.createElement("script");
    const onLoad = () => setScriptReady(true);
    const onError = () => setScriptError(true);
    script.addEventListener("load", onLoad);
    script.addEventListener("error", onError);
    if (!existing) {
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.dataset.begamerGoogle = "true";
      document.head.append(script);
    }
    return () => {
      script.removeEventListener("load", onLoad);
      script.removeEventListener("error", onError);
    };
  }, []);

  useEffect(() => {
    if (!scriptReady || !window.google || !buttonRef.current || !config.google_client_id) return;
    const parent = buttonRef.current;
    parent.replaceChildren();
    window.google.accounts.id.initialize({
      client_id: config.google_client_id,
      callback: ({ credential }) => login.mutate(credential),
      auto_select: false,
      cancel_on_tap_outside: true,
    });
    window.google.accounts.id.renderButton(parent, {
      type: "standard",
      theme: "filled_black",
      size: "large",
      shape: "pill",
      text: "continue_with",
      width: Math.min(320, Math.max(240, window.innerWidth - 80)),
    });
  }, [config.google_client_id, login.mutate, scriptReady]);

  if (!config.google_client_id) {
    return (
      <p className="rounded-xl border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
        Google 登录正在完成云端配置，请稍后刷新。
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <div ref={buttonRef} className="flex min-h-11 justify-center" />
      {scriptError ? (
        <p className="text-center text-sm text-danger">
          Google 登录组件加载失败，请检查网络后刷新。
        </p>
      ) : null}
      {login.error ? (
        <p className="text-center text-sm text-danger">
          {login.error instanceof Error ? login.error.message : "登录没有成功，请重试。"}
        </p>
      ) : null}
      {login.isPending ? <p className="text-center text-xs text-muted">正在安全登录…</p> : null}
    </div>
  );
}

function LoginScreen({ config }: { config: AuthConfig }) {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10 sm:px-6">
      <div className="pointer-events-none absolute -left-36 top-[-8rem] size-[32rem] rounded-full bg-brand/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-48 -right-36 size-[38rem] rounded-full bg-ai/15 blur-3xl" />

      <section className="relative w-full max-w-5xl overflow-hidden rounded-[2rem] border bg-surface/80 shadow-[0_32px_100px_rgb(0_0_0/0.28)] backdrop-blur-2xl lg:grid lg:grid-cols-[1.18fr_0.82fr]">
        <div className="relative min-h-[25rem] overflow-hidden p-7 sm:p-10 lg:min-h-[38rem] lg:p-12">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_24%,color-mix(in_srgb,var(--ai)_24%,transparent),transparent_28rem),linear-gradient(145deg,color-mix(in_srgb,var(--brand)_12%,transparent),transparent_58%)]" />
          <div className="relative flex h-full flex-col">
            <div className="flex items-center gap-3">
              <span className="relative flex size-11 items-center justify-center rounded-[13px] bg-brand text-brand-ink shadow-[0_0_28px_color-mix(in_srgb,var(--brand)_28%,transparent)]">
                <Gamepad2 aria-hidden="true" className="size-6" />
                <span className="absolute -bottom-1 -right-1 size-3.5 rounded-full bg-ai" />
              </span>
              <span className="text-xl font-black tracking-[-0.05em]">BEGAMER</span>
            </div>

            <div className="my-auto max-w-xl py-12">
              <p className="font-mono text-[10px] font-bold tracking-[0.2em] text-brand">
                YOUR PERSONAL GAME CURATOR
              </p>
              <h1 className="mt-4 text-balance text-4xl font-black leading-[0.98] tracking-[-0.06em] sm:text-6xl">
                今晚，不再对着游戏库发呆。
              </h1>
              <p className="mt-6 max-w-lg text-base leading-7 text-muted sm:text-lg">
                同步 Steam，整理你的游玩脉络，再让 AI 从真正属于你的游戏里挑出下一段体验。
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { icon: LibraryBig, label: "跨设备游戏库" },
                { icon: Sparkles, label: "个性化策展" },
                { icon: ShieldCheck, label: "仅本人可访问" },
              ].map(({ icon: Icon, label }) => (
                <div
                  key={label}
                  className="flex items-center gap-2 rounded-xl border bg-background/45 p-3 text-xs font-semibold text-muted"
                >
                  <Icon aria-hidden="true" className="size-4 shrink-0 text-brand" />
                  {label}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center border-t bg-background/55 p-7 sm:p-10 lg:border-l lg:border-t-0 lg:p-12">
          <div className="w-full">
            <div className="flex size-12 items-center justify-center rounded-2xl border bg-surface text-brand">
              <KeyRound aria-hidden="true" className="size-5" />
            </div>
            <h2 className="mt-7 text-2xl font-bold tracking-[-0.035em]">欢迎回来</h2>
            <p className="mt-2 text-sm leading-6 text-muted">
              使用你已授权的 Google 账号继续。BEGAMER 不会获取你的 Google 密码。
            </p>

            <div className="mt-8">
              <GoogleButton config={config} />
            </div>

            <div className="mt-8 border-t pt-5 text-xs leading-5 text-muted">
              登录状态使用安全的 HttpOnly Cookie 保存；Steam 与 AI 密钥只存在 Cloudflare Secrets
              中。
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function LoadingScreen() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="text-center">
        <span className="mx-auto flex size-12 animate-pulse items-center justify-center rounded-2xl bg-brand text-brand-ink">
          <Gamepad2 aria-hidden="true" className="size-6" />
        </span>
        <p className="mt-4 text-sm font-semibold text-muted">正在打开你的游戏空间…</p>
      </div>
    </main>
  );
}

export function AuthGate({ children }: { children: ReactNode }) {
  const config = useQuery({ queryKey: ["auth", "config"], queryFn: api.authConfig, retry: false });
  const session = useQuery({
    queryKey: ["auth", "me"],
    queryFn: api.me,
    enabled: config.isSuccess,
    retry: false,
  });

  if (config.isLoading || (config.isSuccess && session.isLoading)) return <LoadingScreen />;
  if (config.data && session.error instanceof ApiError && session.error.status === 401) {
    return <LoginScreen config={config.data} />;
  }
  if (config.error || session.error) {
    const error = config.error ?? session.error;
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <div className="max-w-md rounded-2xl border bg-surface p-7 text-center shadow-xl">
          <h1 className="text-xl font-bold">暂时无法打开 BEGAMER</h1>
          <p className="mt-3 text-sm leading-6 text-muted">
            {error instanceof Error ? error.message : "请稍后重试。"}
          </p>
          <Button className="mt-6" onClick={() => window.location.reload()}>
            重新加载
          </Button>
        </div>
      </main>
    );
  }
  return session.data ? children : <LoadingScreen />;
}
