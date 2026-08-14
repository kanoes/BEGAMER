import { describe, expect, it } from "vitest";

import { achievementLabel, formatHours } from "@/lib/utils";

describe("library formatting", () => {
  it("labels unplayed games clearly", () => {
    expect(formatHours(0)).toBe("从未启动");
  });

  it("formats short and long playtime", () => {
    expect(formatHours(90)).toBe("1.5 小时");
    expect(formatHours(3684)).toBe("61 小时");
  });

  it("omits unknown achievement progress", () => {
    expect(achievementLabel({ achievements_unlocked: null, achievements_total: null })).toBeNull();
    expect(achievementLabel({ achievements_unlocked: 42, achievements_total: 49 })).toBe(
      "42/49 成就",
    );
  });
});
