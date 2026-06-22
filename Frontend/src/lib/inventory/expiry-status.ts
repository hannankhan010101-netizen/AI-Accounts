/** Batch expiry status helpers — mirrors backend BatchExpiryAlertService rules. */

export const EXPIRY_ALERT_WINDOW_DAYS = 30;

export type ExpiryStatus =
  | "expired"
  | "expiring_soon"
  | "ok"
  | "no_expiry";

export type ExpiryBadgeVariant = "danger" | "warning" | "default";

export type ExpiryStatusResult = {
  status: ExpiryStatus;
  label: string;
  variant: ExpiryBadgeVariant;
  daysLeft: number | null;
  alertable: boolean;
};

function toUtcDate(value: string | Date | null | undefined): Date | null {
  if (!value) return null;
  const d = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(d.getTime())) return null;
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
}

function todayUtc(now: Date = new Date()): Date {
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
}

export function getExpiryStatus(
  expiryDate: string | Date | null | undefined,
  options?: { now?: Date; windowDays?: number; quantityOnHand?: number | string | null },
): ExpiryStatusResult {
  const windowDays = options?.windowDays ?? EXPIRY_ALERT_WINDOW_DAYS;
  const qty = options?.quantityOnHand;
  const qtyNum = qty === null || qty === undefined || qty === "" ? 0 : Number(qty);
  if (!Number.isFinite(qtyNum) || qtyNum <= 0) {
    return {
      status: "no_expiry",
      label: "—",
      variant: "default",
      daysLeft: null,
      alertable: false,
    };
  }

  const exp = toUtcDate(expiryDate);
  if (!exp) {
    return {
      status: "no_expiry",
      label: "No expiry",
      variant: "default",
      daysLeft: null,
      alertable: false,
    };
  }

  const now = todayUtc(options?.now);
  const msPerDay = 86400000;
  const daysLeft = Math.round((exp.getTime() - now.getTime()) / msPerDay);

  if (daysLeft < 0) {
    return {
      status: "expired",
      label: "Expired",
      variant: "danger",
      daysLeft,
      alertable: true,
    };
  }
  if (daysLeft <= windowDays) {
    return {
      status: "expiring_soon",
      label: daysLeft === 0 ? "Expires today" : `Expires in ${daysLeft}d`,
      variant: "warning",
      daysLeft,
      alertable: true,
    };
  }
  return {
    status: "ok",
    label: exp.toLocaleDateString(),
    variant: "default",
    daysLeft,
    alertable: false,
  };
}

export function sortBatchesByExpiryUrgency<
  T extends { expiryDate?: string | null; expiryStatus?: string; daysToExpiry?: number | null },
>(rows: T[]): T[] {
  const rank = (r: T) => {
    if (r.expiryStatus === "expired") return 0;
    if (r.expiryStatus === "expiring_soon") return 1;
    if (r.expiryStatus === "ok") return 2;
    return 3;
  };
  return [...rows].sort((a, b) => {
    const ra = rank(a);
    const rb = rank(b);
    if (ra !== rb) return ra - rb;
    const da = a.daysToExpiry ?? 9999;
    const db = b.daysToExpiry ?? 9999;
    return da - db;
  });
}

export function matchesExpiryFilter(
  row: { expiryStatus?: string },
  filter: string | null | undefined,
): boolean {
  if (!filter || filter === "all") return true;
  if (filter === "expired") return row.expiryStatus === "expired";
  if (filter === "expiring") {
    return row.expiryStatus === "expired" || row.expiryStatus === "expiring_soon";
  }
  return true;
}
