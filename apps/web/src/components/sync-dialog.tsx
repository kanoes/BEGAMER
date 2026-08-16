import * as Dialog from "@radix-ui/react-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Database, KeyRound, LoaderCircle, RefreshCw, X } from "lucide-react";
import { type FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function SyncDialog() {
  const [open, setOpen] = useState(false);
  const [steamId, setSteamId] = useState("");
  const queryClient = useQueryClient();
  const capabilities = useQuery({ queryKey: ["capabilities"], queryFn: api.capabilities });

  const refreshData = async () => {
    await queryClient.invalidateQueries();
  };
  const sync = useMutation({
    mutationFn: () => api.syncSteam(steamId.trim()),
    onSuccess: refreshData,
  });
  const demo = useMutation({
    mutationFn: api.useDemo,
    onSuccess: async () => {
      await refreshData();
      setOpen(false);
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sync.mutate();
  };

  const isConfigured = capabilities.data?.steam_configured ?? false;
  const trimmedSteamId = steamId.trim();
  const isSteamIdInputValid = trimmedSteamId.length === 0 || /^\d{17}$/.test(trimmedSteamId);
  const showSteamIdError = !isSteamIdInputValid;

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <Button
          variant="secondary"
          size="icon"
          aria-label="同步 Steam"
          className="sm:h-9 sm:min-h-9 sm:w-auto sm:px-3"
        >
          <RefreshCw aria-hidden="true" className="size-3.5" />
          <span className="hidden sm:inline">同步 Steam</span>
        </Button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm data-[state=closed]:animate-none" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-white/10 bg-surface p-6 shadow-2xl focus:outline-none sm:p-7">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-xl font-semibold tracking-[-0.02em]">
                连接你的 Steam 世界
              </Dialog.Title>
              <Dialog.Description className="mt-2 text-sm leading-6 text-muted">
                只读取公开游戏库与游玩记录。BEGAMER 不会修改 Steam，也不会接触你的密码。
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button
                variant="ghost"
                size="icon"
                aria-label="关闭同步窗口"
                className="-mr-2 -mt-2 shrink-0"
              >
                <X aria-hidden="true" className="size-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border bg-raised/55 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <KeyRound aria-hidden="true" className="size-4 text-steam" />
                Steam API
              </div>
              <p className="mt-2 text-xs leading-5 text-muted">
                {isConfigured ? "后端密钥已配置，可以同步。" : "尚未配置 STEAM_WEB_API_KEY。"}
              </p>
            </div>
            <div className="rounded-xl border bg-raised/55 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <Database aria-hidden="true" className="size-4 text-ai" />
                私有云端
              </div>
              <p className="mt-2 text-xs leading-5 text-muted">
                同步异常时不会删除已有数据或标记。
              </p>
            </div>
          </div>

          <form className="mt-6" onSubmit={handleSubmit}>
            <label htmlFor="steam-id" className="text-sm font-semibold">
              SteamID64
            </label>
            <p id="steam-id-help" className="mt-1 text-xs text-muted">
              17 位数字 ID；留空时使用后端 `.env` 中的 STEAM_ID。
            </p>
            <input
              id="steam-id"
              value={steamId}
              onChange={(event) => setSteamId(event.target.value)}
              aria-describedby={showSteamIdError ? "steam-id-help steam-id-error" : "steam-id-help"}
              aria-invalid={showSteamIdError}
              autoComplete="off"
              inputMode="numeric"
              maxLength={17}
              pattern="[0-9]{17}"
              placeholder="7656119xxxxxxxxxx"
              className="mt-3 h-12 w-full rounded-xl border border-white/10 bg-background/70 px-4 font-mono text-sm text-foreground outline-none transition focus:border-brand/60 focus:ring-3 focus:ring-brand/20 aria-invalid:border-danger/70 aria-invalid:focus:ring-danger/20"
            />
            {showSteamIdError ? (
              <p id="steam-id-error" role="alert" className="mt-2 text-xs leading-5 text-danger">
                这不是 SteamID64。这里只能填写 17 位纯数字；32 位十六进制字符串是 API Key，
                不应填在这里。
              </p>
            ) : null}

            <div aria-live="polite" className="mt-3 min-h-6 text-sm">
              {sync.isSuccess ? (
                <p className="flex items-center gap-2 text-success">
                  <CheckCircle2 aria-hidden="true" className="size-4" />
                  {sync.data.message}
                </p>
              ) : null}
              {sync.isError ? <p className="text-danger">{sync.error.message}</p> : null}
            </div>

            <div className="mt-4 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
              <Button
                variant="ghost"
                disabled={demo.isPending}
                onClick={() => demo.mutate()}
                className="sm:justify-start"
              >
                {demo.isPending ? <LoaderCircle className="size-4 animate-spin" /> : null}
                使用演示数据
              </Button>
              <Button
                type="submit"
                disabled={!isConfigured || !isSteamIdInputValid || sync.isPending}
              >
                {sync.isPending ? <LoaderCircle className="size-4 animate-spin" /> : null}
                {sync.isPending ? "正在同步…" : "开始安全同步"}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
