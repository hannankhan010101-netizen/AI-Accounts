import type { PersonaId } from "@/lib/tour/types";

/** Default persona until server role templates are wired (P0). */
export function resolvePersona(_permissions: string[], roleName?: string | null): PersonaId {
  const name = (roleName ?? "").toLowerCase();
  if (name.includes("admin")) return "admin";
  if (name.includes("cfo") || name.includes("finance lead")) return "cfo";
  if (name.includes("account")) return "accountant";
  if (name.includes("sales")) return "sales";
  if (name.includes("inventory") || name.includes("warehouse")) return "inventory_manager";
  if (name.includes("procurement") || name.includes("purchase")) return "procurement";
  if (name.includes("view") || name.includes("read")) return "viewer";
  return "general";
}
