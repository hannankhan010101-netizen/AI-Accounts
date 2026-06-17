/** Client-side permission checks (mirror server wildcard rules). */

export function hasPermission(permissions: string[], code: string): boolean {
  if (permissions.includes("*")) return true;
  if (permissions.includes(code)) return true;
  const parts = code.split(".");
  for (let i = parts.length - 1; i > 0; i--) {
    const wc = `${parts.slice(0, i).join(".")}.*`;
    if (permissions.includes(wc)) return true;
  }
  return false;
}

export const PERM_USERS_INVITE = "settings.users.invite";
export const PERM_ROLES_MANAGE = "settings.roles.manage";
export const PERM_ACCESS_CONTROL_MANAGE = "settings.access_control.manage";
export const PERM_PLATFORM_PROCESS = "settings.platform.process";
