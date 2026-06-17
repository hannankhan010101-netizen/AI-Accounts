/**
 * Token storage. localStorage for now; swap to httpOnly cookies for production.
 */

import { getCompanyIdFromAccessToken } from "@/lib/auth/jwt";

const ACCESS_KEY = "fa.accessToken";
const REFRESH_KEY = "fa.refreshToken";
const COMPANY_KEY = "fa.currentCompanyId";

export interface Tokens {
  accessToken: string;
  refreshToken: string;
}

export function getTokens(): Tokens | null {
  if (typeof window === "undefined") return null;
  const accessToken = window.localStorage.getItem(ACCESS_KEY);
  const refreshToken = window.localStorage.getItem(REFRESH_KEY);
  if (!accessToken || !refreshToken) return null;
  return { accessToken, refreshToken };
}

export type SetTokensOptions = {
  /** When false, keep `fa.currentCompanyId` (e.g. token refresh after company switch). */
  syncCompanyFromToken?: boolean;
};

export function setTokens(tokens: Tokens, options?: SetTokensOptions): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_KEY, tokens.accessToken);
  window.localStorage.setItem(REFRESH_KEY, tokens.refreshToken);
  if (options?.syncCompanyFromToken === false) return;
  const companyId = getCompanyIdFromAccessToken(tokens.accessToken);
  if (companyId) setCurrentCompanyId(companyId);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
  window.localStorage.removeItem(COMPANY_KEY);
}

export function getCurrentCompanyId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(COMPANY_KEY);
}

export function setCurrentCompanyId(id: string | null): void {
  if (typeof window === "undefined") return;
  if (id) window.localStorage.setItem(COMPANY_KEY, id);
  else window.localStorage.removeItem(COMPANY_KEY);
}
