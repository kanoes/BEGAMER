import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatHours(minutes: number): string {
  if (minutes === 0) return "从未启动";
  const hours = minutes / 60;
  return hours < 10 ? `${hours.toFixed(1)} 小时` : `${Math.round(hours)} 小时`;
}

export function formatRelativeDate(value: string | null): string {
  if (!value) return "还没有玩过";
  const date = new Date(value);
  const days = Math.max(0, Math.floor((Date.now() - date.getTime()) / 86_400_000));
  if (days === 0) return "今天玩过";
  if (days === 1) return "昨天玩过";
  if (days < 30) return `${days} 天前玩过`;
  if (days < 365) return `${Math.floor(days / 30)} 个月前玩过`;
  return `${Math.floor(days / 365)} 年前玩过`;
}

export function achievementLabel(game: {
  achievements_unlocked: number | null;
  achievements_total: number | null;
}): string | null {
  if (game.achievements_unlocked === null || !game.achievements_total) return null;
  return `${game.achievements_unlocked}/${game.achievements_total} 成就`;
}
