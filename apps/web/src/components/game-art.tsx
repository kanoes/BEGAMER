import { ImageOff } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/utils";

interface GameArtProps {
  src: string;
  alt: string;
  className?: string;
  eager?: boolean;
}

export function GameArt({ src, alt, className, eager = false }: GameArtProps) {
  const [failed, setFailed] = useState(false);

  return (
    <div className={cn("cover-fallback relative overflow-hidden", className)}>
      {!failed ? (
        <img
          src={src}
          alt={alt}
          loading={eager ? "eager" : "lazy"}
          className="size-full object-cover"
          onError={() => setFailed(true)}
        />
      ) : (
        <div className="flex size-full flex-col items-center justify-center gap-2 p-4 text-center text-white/60">
          <ImageOff aria-hidden="true" className="size-5" />
          <span className="line-clamp-2 text-xs font-semibold">{alt}</span>
        </div>
      )}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-white/10"
      />
    </div>
  );
}
