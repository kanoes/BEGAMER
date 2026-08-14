import { useQuery } from "@tanstack/react-query";
import {
  Command,
  Gamepad2,
  Home,
  Layers3,
  LibraryBig,
  Moon,
  Search,
  Sparkles,
  Sun,
} from "lucide-react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import { AccountAvatar } from "@/components/account-avatar";
import { SyncDialog } from "@/components/sync-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useTheme } from "@/hooks/use-theme";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "今日", icon: Home, end: true },
  { to: "/library", label: "游戏库", icon: LibraryBig },
  { to: "/collections", label: "分类方案", icon: Layers3 },
  { to: "/assistant", label: "AI 助手", icon: Sparkles },
];

const pageTitles: Record<string, { eyebrow: string; title: string }> = {
  "/": { eyebrow: "YOUR NIGHT SHELF", title: "今日策展" },
  "/library": { eyebrow: "THE ARCHIVE", title: "游戏库" },
  "/collections": { eyebrow: "CURATED SETS", title: "分类方案" },
  "/assistant": { eyebrow: "PERSONAL CURATOR", title: "AI 助手" },
};

function BrandMark() {
  return (
    <Link
      to="/"
      aria-label="BEGAMER 首页"
      className="flex min-h-11 items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand"
    >
      <span className="relative flex size-9 items-center justify-center overflow-hidden rounded-[10px] bg-brand text-brand-ink">
        <Gamepad2 aria-hidden="true" className="size-5" />
        <span className="absolute -bottom-1 -right-1 size-3 rounded-full bg-ai" />
      </span>
      <span className="text-lg font-black tracking-[-0.04em]">BEGAMER</span>
    </Link>
  );
}

export function AppShell() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  const capabilities = useQuery({ queryKey: ["capabilities"], queryFn: api.capabilities });
  const heading = pageTitles[location.pathname] ?? pageTitles["/"];

  return (
    <div className="min-h-screen">
      <a
        href="#main-content"
        className="sr-only z-[100] rounded-md bg-brand px-4 py-2 font-semibold text-brand-ink focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        跳到主要内容
      </a>

      <aside className="fixed inset-y-0 left-0 z-40 hidden w-56 border-r bg-background/85 px-5 py-6 backdrop-blur-xl lg:flex lg:flex-col">
        <BrandMark />
        <nav aria-label="主导航" className="mt-12 space-y-2">
          {navigation.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "group relative flex min-h-11 items-center gap-3 rounded-[10px] px-3 text-sm font-semibold text-muted transition-colors hover:bg-white/[0.05] hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand/60",
                  isActive && "bg-white/[0.07] text-foreground",
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive ? (
                    <span className="absolute -left-5 h-7 w-1 rounded-r-full bg-brand shadow-[0_0_16px_var(--brand)]" />
                  ) : null}
                  <Icon aria-hidden="true" className="size-[18px]" />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto rounded-xl border bg-surface/80 p-4">
          <div className="flex items-center justify-between gap-2">
            <span className="font-mono text-[10px] font-semibold tracking-[0.12em] text-muted">
              DATA SOURCE
            </span>
            <span
              className={cn(
                "size-2 rounded-full",
                capabilities.data?.active_source === "steam" ? "bg-steam" : "bg-brand",
              )}
            />
          </div>
          <p className="mt-2 text-sm font-semibold">
            {capabilities.data?.active_source === "steam" ? "Steam Library" : "Demo Library"}
          </p>
          <p className="mt-1 text-xs text-muted">
            {capabilities.data?.llm_configured ? "AI 策展已开启" : "本地策展模式"}
          </p>
        </div>
      </aside>

      <div className="lg:pl-56">
        <header className="sticky top-0 z-30 border-b bg-background/78 backdrop-blur-xl">
          <div className="flex h-18 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8 xl:px-10">
            <div className="flex min-w-0 items-center gap-4">
              <div className="lg:hidden">
                <BrandMark />
              </div>
              <div className="hidden min-w-0 sm:block lg:block">
                <p className="font-mono text-[9px] font-bold tracking-[0.16em] text-muted">
                  {heading?.eyebrow}
                </p>
                <h1 className="truncate text-base font-semibold">{heading?.title}</h1>
              </div>
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2">
              <Link
                to="/library"
                aria-label="搜索游戏库"
                className="hidden h-10 w-52 items-center gap-2 rounded-[10px] border bg-white/[0.035] px-3 text-sm text-muted transition-colors hover:border-white/20 hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand/60 md:flex"
              >
                <Search aria-hidden="true" className="size-4" />
                <span>搜索游戏</span>
                <span className="ml-auto flex items-center gap-0.5 rounded border px-1.5 py-0.5 font-mono text-[9px]">
                  <Command aria-hidden="true" className="size-2.5" />K
                </span>
              </Link>
              <SyncDialog />
              <Button variant="ghost" size="icon" aria-label="切换明暗主题" onClick={toggleTheme}>
                {theme === "dark" ? (
                  <Sun aria-hidden="true" className="size-4" />
                ) : (
                  <Moon aria-hidden="true" className="size-4" />
                )}
              </Button>
              {dashboard.isLoading ? (
                <Skeleton className="size-9 rounded-full" />
              ) : (
                <AccountAvatar
                  src={dashboard.data?.account.avatar_url}
                  name={dashboard.data?.account.display_name ?? "BEGAMER Player"}
                />
              )}
            </div>
          </div>
        </header>

        <main id="main-content" className="px-4 pb-28 pt-6 sm:px-6 lg:px-8 lg:pb-12 xl:px-10">
          <div className="mx-auto max-w-[1480px]">
            <Outlet />
          </div>
        </main>
      </div>

      <nav
        aria-label="移动端主导航"
        className="fixed inset-x-3 bottom-3 z-40 grid h-16 grid-cols-4 rounded-2xl border bg-background/90 p-1.5 shadow-2xl backdrop-blur-xl lg:hidden"
      >
        {navigation.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex min-h-11 flex-col items-center justify-center gap-1 rounded-xl text-[10px] font-semibold text-muted focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-brand/60",
                isActive && "bg-brand text-brand-ink",
              )
            }
          >
            <Icon aria-hidden="true" className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
