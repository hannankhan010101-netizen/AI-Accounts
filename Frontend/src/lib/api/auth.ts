/**
 * Typed wrappers for /api/v1/auth/* and /api/v1/companies/*.
 * Matches Backend/src/app/models/{requests,responses}/auth_*.py.
 */
import { apiFetch } from "./client";

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

export interface SignUpPending {
  message: string;
  email: string;
  expiresAt: string;
  devOtp?: string | null;
}

export interface AuthMessage {
  message: string;
}

export interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string | null;
  emailVerified: boolean;
}

export interface Company {
  id: string;
  name: string;
  createdAt?: string;
  updatedAt?: string;
}

/** API may return legacy ``companyId``; normalize to ``id``. */
export function normalizeCompany(raw: Company & { companyId?: string }): Company {
  return {
    id: raw.id ?? raw.companyId ?? "",
    name: raw.name,
    createdAt: raw.createdAt,
    updatedAt: raw.updatedAt,
  };
}

export const authApi = {
  signUp: (body: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    companyName: string;
  }) =>
    apiFetch<SignUpPending | AuthTokens>("/api/v1/auth/sign-up", {
      method: "POST",
      body,
      anonymous: true,
    }),

  verifyEmail: (body: { email: string; otpCode: string }) =>
    apiFetch<AuthTokens>("/api/v1/auth/verify-email", {
      method: "POST",
      body,
      anonymous: true,
    }),

  resendOtp: (body: { email: string; purpose: "signup" | "password_reset" }) =>
    apiFetch<SignUpPending | AuthMessage>("/api/v1/auth/resend-otp", {
      method: "POST",
      body,
      anonymous: true,
    }),

  forgotPassword: (body: { email: string }) =>
    apiFetch<SignUpPending | AuthMessage>("/api/v1/auth/forgot-password", {
      method: "POST",
      body,
      anonymous: true,
    }),

  resetPassword: (body: {
    email: string;
    otpCode: string;
    newPassword: string;
    purpose?: "password_reset" | "user_invite";
  }) =>
    apiFetch<AuthMessage>("/api/v1/auth/reset-password", {
      method: "POST",
      body,
      anonymous: true,
    }),

  acceptInvite: (body: { email: string; otpCode: string; newPassword: string }) =>
    apiFetch<AuthMessage>("/api/v1/auth/accept-invite", {
      method: "POST",
      body,
      anonymous: true,
    }),

  login: (body: { email: string; password: string }) =>
    apiFetch<AuthTokens>("/api/v1/auth/login", {
      method: "POST",
      body,
      anonymous: true,
    }),

  logout: () =>
    apiFetch<{ message: string }>("/api/v1/auth/logout", { method: "POST" }),

  me: () => apiFetch<UserProfile>("/api/v1/auth/me"),

  updateProfile: (body: { firstName?: string; lastName?: string; phone?: string | null }) =>
    apiFetch<UserProfile>("/api/v1/auth/me", {
      method: "PATCH",
      body,
    }),

  changePassword: (body: { currentPassword: string; newPassword: string }) =>
    apiFetch<AuthMessage>("/api/v1/auth/change-password", {
      method: "POST",
      body,
    }),
};

export const companiesApi = {
  list: async () => {
    const data = await apiFetch<{ result: (Company & { companyId?: string })[] }>(
      "/api/v1/companies",
    );
    return { result: data.result.map(normalizeCompany) };
  },
  create: (body: { name: string }) =>
    apiFetch<Company>("/api/v1/companies", { method: "POST", body }),
  switch: (companyId: string) =>
    apiFetch<AuthTokens>(`/api/v1/companies/${companyId}/switch`, { method: "POST" }),
};
