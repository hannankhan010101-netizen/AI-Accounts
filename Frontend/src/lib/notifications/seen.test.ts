import { beforeEach, describe, expect, it, vi } from "vitest";

import { countUnreadNotifications, getSeenNotificationIds, markNotificationsSeen } from "./seen";

describe("notification seen state", () => {
  const store = new Map<string, string>();

  beforeEach(() => {
    store.clear();
    vi.stubGlobal("sessionStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => {
        store.set(key, value);
      },
    });
  });

  it("marks ids as seen and counts unread", () => {
    markNotificationsSeen("co1", ["a", "b"]);
    expect(getSeenNotificationIds("co1")).toEqual(new Set(["a", "b"]));
    expect(
      countUnreadNotifications("co1", [{ id: "a" }, { id: "b" }, { id: "c" }]),
    ).toBe(1);
  });
});
