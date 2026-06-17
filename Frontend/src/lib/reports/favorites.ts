const STORAGE_KEY = "fa-report-favorites";

export function loadReportFavorites(companyId: string | null): Set<string> {
  if (!companyId || typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(`${STORAGE_KEY}:${companyId}`);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw) as string[];
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
}

export function saveReportFavorites(companyId: string | null, hrefs: Set<string>) {
  if (!companyId || typeof window === "undefined") return;
  localStorage.setItem(`${STORAGE_KEY}:${companyId}`, JSON.stringify([...hrefs]));
}

export async function fetchReportFavorites(companyId: string | null): Promise<Set<string>> {
  if (!companyId) return new Set();
  try {
    const token =
      typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
    const res = await fetch(`/api/v1/companies/${companyId}/settings/report-favorites`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) return loadReportFavorites(companyId);
    const data = (await res.json()) as { result?: { hrefs?: string[] } };
    const hrefs = data.result?.hrefs ?? [];
    const set = new Set(hrefs);
    saveReportFavorites(companyId, set);
    return set;
  } catch {
    return loadReportFavorites(companyId);
  }
}

export async function persistReportFavorites(
  companyId: string | null,
  hrefs: Set<string>,
): Promise<Set<string>> {
  saveReportFavorites(companyId, hrefs);
  if (!companyId) return hrefs;
  try {
    const token =
      typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
    const res = await fetch(`/api/v1/companies/${companyId}/settings/report-favorites`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ hrefs: [...hrefs] }),
    });
    if (!res.ok) return hrefs;
    const data = (await res.json()) as { result?: { hrefs?: string[] } };
    const stored = data.result?.hrefs;
    if (Array.isArray(stored)) {
      const set = new Set(stored);
      saveReportFavorites(companyId, set);
      return set;
    }
  } catch {
    /* keep local cache */
  }
  return hrefs;
}

export function toggleReportFavorite(
  companyId: string | null,
  href: string,
  current: Set<string>,
): Set<string> {
  const next = new Set(current);
  if (next.has(href)) next.delete(href);
  else next.add(href);
  saveReportFavorites(companyId, next);
  return next;
}
