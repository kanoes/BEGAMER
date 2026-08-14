import { UserRound } from "lucide-react";
import { useState } from "react";

interface AccountAvatarProps {
  src: string | null | undefined;
  name: string;
}

export function AccountAvatar({ src, name }: AccountAvatarProps) {
  const [failed, setFailed] = useState(false);

  return (
    <div
      title={name}
      className="size-9 overflow-hidden rounded-full border border-white/15 bg-raised"
    >
      {src && !failed ? (
        <img
          src={src}
          alt={`${name} 的头像`}
          className="size-full object-cover"
          onError={() => setFailed(true)}
        />
      ) : (
        <div className="flex size-full items-center justify-center bg-[linear-gradient(135deg,color-mix(in_srgb,var(--ai)_35%,var(--raised)),var(--raised))] text-muted">
          <UserRound aria-label={`${name} 的头像占位图`} className="size-4" />
        </div>
      )}
    </div>
  );
}
