const STORAGE_PREFIX = "expiry-notifications-seen:";

export function markNotificationsSeen(companyId: string, ids: string[]): void {
  if (typeof sessionStorage === "undefined") return;
  sessionStorage.setItem(`${STORAGE_PREFIX}${companyId}`, JSON.stringify(ids));
}

export function getSeenNotificationIds(companyId: string): Set<string> {
  if (typeof sessionStorage === "undefined") return new Set();
  try {
    const raw = sessionStorage.getItem(`${STORAGE_PREFIX}${companyId}`);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw) as unknown;
    return new Set(Array.isArray(parsed) ? parsed.filter((id) => typeof id === "string") : []);
  } catch {
    return new Set();
  }
}

export function countUnreadNotifications(
  companyId: string,
  items: Array<{ id: string }>,
): number {
  const seen = getSeenNotificationIds(companyId);
  return items.filter((item) => !seen.has(item.id)).length;
}
