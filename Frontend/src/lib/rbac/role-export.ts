/** Resolve role clone targets from export JSON — P42/P43. */

export type TableRole = { id: string; name: string };

type ExportRoleRow = { id?: string; name?: string };

function parseExportRoleRows(text: string): ExportRoleRow[] {
  const data = JSON.parse(text) as unknown;
  let rows: unknown[] = [];
  if (Array.isArray(data)) {
    rows = data;
  } else if (data && typeof data === "object" && Array.isArray((data as { roles?: unknown }).roles)) {
    rows = (data as { roles: unknown[] }).roles;
  } else {
    throw new Error('JSON must be { "roles": [...] } or a role array');
  }
  const parsed: ExportRoleRow[] = [];
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const id =
      "id" in row && (row as { id: unknown }).id != null
        ? String((row as { id: unknown }).id).trim()
        : undefined;
    const name =
      "name" in row && (row as { name: unknown }).name != null
        ? String((row as { name: unknown }).name).trim()
        : undefined;
    if (id || name) parsed.push({ id: id || undefined, name: name || undefined });
  }
  if (parsed.length === 0) {
    throw new Error("No roles found in export file");
  }
  return parsed;
}

function normalizeName(name: string): string {
  return name.trim().toLowerCase();
}

/** Resolve ids from export rows (by id, else by name on the current table). */
export function resolveRoleCloneIdsFromExport(
  text: string,
  tableRoles: TableRole[],
  selected: Set<string>
): string[] {
  const rows = parseExportRoleRows(text);
  const onPageByName = new Map<string, string>();
  for (const r of tableRoles) {
    const key = normalizeName(r.name);
    if (!onPageByName.has(key)) onPageByName.set(key, r.id);
  }

  const ids: string[] = [];
  const unmatched: string[] = [];
  for (const row of rows) {
    if (row.id) {
      ids.push(row.id);
      continue;
    }
    if (row.name) {
      const id = onPageByName.get(normalizeName(row.name));
      if (id) ids.push(id);
      else unmatched.push(row.name);
    }
  }
  if (unmatched.length > 0) {
    throw new Error(`No roles on this page match: ${unmatched.join(", ")}`);
  }
  const unique = [...new Set(ids)];
  if (unique.length === 0) {
    throw new Error("No role ids or names could be resolved from export");
  }

  const onPage = new Set(tableRoles.map((r) => r.id));
  const roleIds =
    selected.size > 0
      ? unique.filter((id) => selected.has(id))
      : unique.filter((id) => onPage.has(id));
  if (roleIds.length === 0) {
    throw new Error(
      "No matching roles — select table rows or use ids/names from roles on this page"
    );
  }
  return roleIds;
}

/** @deprecated Use resolveRoleCloneIdsFromExport — ids-only path kept for tests. */
export function parseRoleIdsFromExportJson(text: string): string[] {
  const rows = parseExportRoleRows(text);
  const ids = rows.map((r) => r.id).filter((id): id is string => Boolean(id));
  if (ids.length === 0) {
    throw new Error("No role ids found in export file");
  }
  return [...new Set(ids)];
}
