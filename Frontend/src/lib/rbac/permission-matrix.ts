import { hasPermission } from "@/lib/rbac/permissions";

export type MatrixAction = string;

export type PermissionMatrixModule = {
  module: string;
  moduleLabel: string;
  resources: {
    resource: string;
    label: string;
    actions: Record<string, string>;
  }[];
};

export type PermissionMatrixSchema = {
  actions: MatrixAction[];
  modules: PermissionMatrixModule[];
};

export function codesFromMatrixSelection(
  schema: PermissionMatrixSchema,
  selected: Set<string>,
): string[] {
  return Array.from(selected);
}

export function matrixSelectionFromCodes(
  schema: PermissionMatrixSchema,
  codes: string[],
): Set<string> {
  const allCodes = new Set<string>();
  for (const mod of schema.modules) {
    for (const res of mod.resources) {
      for (const code of Object.values(res.actions)) {
        allCodes.add(code);
      }
    }
  }
  const selected = new Set<string>();
  for (const code of codes) {
    if (code === "*" || allCodes.has(code) || code.endsWith(".*")) {
      selected.add(code);
    }
  }
  if (codes.includes("*")) {
    return new Set(["*"]);
  }
  return selected;
}

export function toggleMatrixCode(selected: Set<string>, code: string): Set<string> {
  if (code === "*") {
    return selected.has("*") ? new Set() : new Set(["*"]);
  }
  const next = new Set(selected);
  next.delete("*");
  if (next.has(code)) next.delete(code);
  else next.add(code);
  return next;
}

export function isMatrixCellGranted(selected: Set<string>, code: string | undefined): boolean {
  if (!code) return false;
  if (selected.has("*")) return true;
  if (selected.has(code)) return true;
  return hasPermission(Array.from(selected), code);
}

export function toggleMatrixCell(
  selected: Set<string>,
  code: string | undefined,
): Set<string> {
  if (!code) return selected;
  return toggleMatrixCode(selected, code);
}

export function grantMatrixColumn(
  schema: PermissionMatrixModule,
  selected: Set<string>,
  action: string,
): Set<string> {
  const next = new Set(selected);
  next.delete("*");
  for (const res of schema.resources) {
    const code = res.actions[action];
    if (code) next.add(code);
  }
  return next;
}

export function clearMatrixColumn(
  schema: PermissionMatrixModule,
  selected: Set<string>,
  action: string,
): Set<string> {
  const next = new Set(selected);
  for (const res of schema.resources) {
    const code = res.actions[action];
    if (code) next.delete(code);
  }
  return next;
}
