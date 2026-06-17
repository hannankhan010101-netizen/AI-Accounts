/** Deep-link helpers for Users settings (P39/P40). */

export function usersHref(userId?: string): string {
  if (!userId?.trim()) return "/settings/users";
  return `/settings/users?userId=${encodeURIComponent(userId.trim())}`;
}

export function reinviteUserHref(userId: string): string {
  return `/settings/users?reinviteUserId=${encodeURIComponent(userId.trim())}`;
}

export function reinviteEmailHref(email: string): string {
  return `/settings/users?reinviteEmail=${encodeURIComponent(email.trim())}`;
}
