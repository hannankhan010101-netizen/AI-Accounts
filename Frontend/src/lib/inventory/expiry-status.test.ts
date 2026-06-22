import { describe, expect, it } from "vitest";

import { EXPIRY_ALERT_WINDOW_DAYS, getExpiryStatus, matchesExpiryFilter } from "@/lib/inventory/expiry-status";

describe("getExpiryStatus", () => {
  const now = new Date("2026-06-23T12:00:00.000Z");

  it("marks expired batches", () => {
    const result = getExpiryStatus("2026-06-22T00:00:00.000Z", {
      now,
      quantityOnHand: 5,
    });
    expect(result.status).toBe("expired");
    expect(result.variant).toBe("danger");
  });

  it("marks expiring soon within window", () => {
    const result = getExpiryStatus("2026-07-10T00:00:00.000Z", {
      now,
      windowDays: EXPIRY_ALERT_WINDOW_DAYS,
      quantityOnHand: 1,
    });
    expect(result.status).toBe("expiring_soon");
    expect(result.variant).toBe("warning");
  });

  it("excludes zero quantity", () => {
    const result = getExpiryStatus("2026-07-10T00:00:00.000Z", {
      now,
      quantityOnHand: 0,
    });
    expect(result.alertable).toBe(false);
  });
});

describe("matchesExpiryFilter", () => {
  it("filters expiring rows", () => {
    expect(matchesExpiryFilter({ expiryStatus: "expired" }, "expiring")).toBe(true);
    expect(matchesExpiryFilter({ expiryStatus: "ok" }, "expiring")).toBe(false);
  });
});
