import type { AuditLogFilters } from "@/lib/api/tenant";

const STORAGE_KEY = "ai-accounts-audit-log-saved-presets";

export type SavedAuditPreset = {
  id: string;
  label: string;
  draft: AuditLogFilters & { type?: string };
};

function readAll(): SavedAuditPreset[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (p): p is SavedAuditPreset =>
        Boolean(
          p &&
            typeof p === "object" &&
            typeof (p as SavedAuditPreset).id === "string" &&
            typeof (p as SavedAuditPreset).label === "string" &&
            typeof (p as SavedAuditPreset).draft === "object"
        )
    );
  } catch {
    return [];
  }
}

function writeAll(presets: SavedAuditPreset[]): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(presets));
}

export function loadSavedAuditPresets(): SavedAuditPreset[] {
  return readAll();
}

export function saveAuditPreset(
  label: string,
  draft: AuditLogFilters & { type?: string }
): SavedAuditPreset {
  const trimmed = label.trim();
  if (!trimmed) {
    throw new Error("Preset name is required");
  }
  const preset: SavedAuditPreset = {
    id: `saved-${Date.now()}`,
    label: trimmed,
    draft: { ...draft },
  };
  writeAll([...readAll(), preset]);
  return preset;
}

export function deleteSavedAuditPreset(id: string): void {
  writeAll(readAll().filter((p) => p.id !== id));
}

export function exportSavedAuditPresetsJson(): string {
  return JSON.stringify({ version: 1, presets: readAll() }, null, 2);
}

function normalizeImportedPreset(raw: unknown, index: number): SavedAuditPreset | null {
  if (!raw || typeof raw !== "object") return null;
  const row = raw as SavedAuditPreset;
  const label = String(row.label ?? "").trim();
  if (!label || !row.draft || typeof row.draft !== "object") return null;
  return {
    id: String(row.id ?? `saved-import-${Date.now()}-${index}`),
    label,
    draft: { ...row.draft },
  };
}

/** Import presets from exported JSON; returns count imported. */
export function importSavedAuditPresetsFromJson(
  text: string,
  options: { merge?: boolean } = {}
): number {
  const data = JSON.parse(text) as unknown;
  let rows: unknown[] = [];
  if (Array.isArray(data)) {
    rows = data;
  } else if (data && typeof data === "object" && Array.isArray((data as { presets?: unknown }).presets)) {
    rows = (data as { presets: unknown[] }).presets;
  } else {
    throw new Error('JSON must be { "version": 1, "presets": [...] } or a preset array');
  }
  const imported = rows
    .map((row, i) => normalizeImportedPreset(row, i))
    .filter((p): p is SavedAuditPreset => p !== null);
  if (imported.length === 0) {
    throw new Error("No valid presets found in file");
  }
  const merge = options.merge !== false;
  const next = merge
    ? [...readAll(), ...imported.map((p) => ({ ...p, id: `saved-${Date.now()}-${p.label}` }))]
    : imported;
  writeAll(next);
  return imported.length;
}
