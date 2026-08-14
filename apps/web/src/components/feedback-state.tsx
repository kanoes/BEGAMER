import { AlertTriangle, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";

export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div
      role="alert"
      className="flex min-h-80 flex-col items-center justify-center rounded-2xl border border-danger/20 bg-danger/5 p-8 text-center"
    >
      <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-danger/10 text-danger">
        <AlertTriangle aria-hidden="true" className="size-5" />
      </div>
      <h2 className="text-lg font-semibold">暂时没有连上游戏库</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-muted">{message}</p>
      {retry ? (
        <Button variant="secondary" className="mt-6" onClick={retry}>
          <RefreshCw aria-hidden="true" className="size-4" />
          再试一次
        </Button>
      ) : null}
    </div>
  );
}
