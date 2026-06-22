"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AlertCircle,
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  Shield,
} from "lucide-react";

import { AuthInputField } from "@/components/auth/auth-input-field";
import { LoginBrandPanel } from "@/components/auth/login-brand-panel";
import { BrandLogo } from "@/components/brand/brand-logo";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { setTokens } from "@/lib/auth/storage";
import { useHydrated } from "@/lib/hooks/use-hydrated";
import { cn } from "@/lib/utils";

const REMEMBER_EMAIL_KEY = "auth.rememberEmail";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Min 8 characters"),
});
type FormValues = z.infer<typeof schema>;

const MOBILE_FEATURES = [
  { icon: Shield, label: "Secure" },
  { icon: Mail, label: "Verified" },
] as const;

export function LoginScreen() {
  const router = useRouter();
  const hydrated = useHydrated();
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const emailField = register("email");
  const passwordField = register("password");

  useEffect(() => {
    try {
      const saved = localStorage.getItem(REMEMBER_EMAIL_KEY);
      if (saved) {
        setValue("email", saved);
        setRememberMe(true);
      }
    } catch {
      /* storage unavailable */
    }
  }, [setValue]);

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      if (rememberMe) {
        localStorage.setItem(REMEMBER_EMAIL_KEY, values.email);
      } else {
        localStorage.removeItem(REMEMBER_EMAIL_KEY);
      }

      const tokens = await authApi.login(values);
      setTokens(tokens);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sign in failed");
    }
  });

  return (
    <div className="grid min-h-dvh bg-canvas lg:grid-cols-[minmax(0,1.05fr)_minmax(22rem,480px)] xl:grid-cols-[minmax(0,1.15fr)_minmax(24rem,520px)]">
      <LoginBrandPanel />

      <div className="relative flex flex-col justify-center overflow-y-auto px-safe py-10 sm:py-12 lg:px-10 lg:py-16 xl:px-14">
        <div className="auth-form-glow pointer-events-none absolute inset-y-0 left-0 hidden w-px lg:block" />

        <div
          className={cn(
            "mx-auto w-full max-w-md",
            hydrated && "auth-enter",
          )}
        >
          <div className="mb-8 flex flex-col items-center text-center lg:items-start lg:text-left">
            <div className="mb-6 lg:hidden">
              <BrandLogo variant="auth" href="/login" priority />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand">
              Welcome back
            </p>
            <h1 className="mt-2 text-[var(--text-display)] font-semibold tracking-tight text-fg">
              Sign in to your workspace
            </h1>
            <p className="mt-2 max-w-sm text-sm leading-relaxed text-fg-muted">
              Access your books, dashboards, and AI assistant — all in one place.
            </p>
          </div>

          <div className="gradient-border-brand rounded-2xl bg-surface-elevated p-6 shadow-premium sm:p-8">
            <form onSubmit={onSubmit} method="post" className="space-y-5">
              <AuthInputField
                label="Work email"
                icon={Mail}
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                required
                error={errors.email?.message}
                name={emailField.name}
                onBlur={emailField.onBlur}
                onChange={emailField.onChange}
                ref={emailField.ref}
              />

              <AuthInputField
                label="Password"
                icon={Lock}
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                required
                error={errors.password?.message}
                name={passwordField.name}
                onBlur={passwordField.onBlur}
                onChange={passwordField.onChange}
                ref={passwordField.ref}
                trailing={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="inline-flex h-9 w-9 items-center justify-center rounded-md text-fg-muted motion-safe-transition hover:bg-canvas hover:text-fg focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" strokeWidth={1.75} />
                    ) : (
                      <Eye className="h-4 w-4" strokeWidth={1.75} />
                    )}
                  </button>
                }
              />

              <div className="flex flex-wrap items-center justify-between gap-3 pt-0.5">
                <div className="inline-flex items-center gap-2">
                  <Checkbox
                    id="remember-me"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="min-h-0 min-w-0"
                  />
                  <label
                    htmlFor="remember-me"
                    className="cursor-pointer text-sm text-fg-muted"
                  >
                    Remember email
                  </label>
                </div>
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-brand motion-safe-transition hover:text-brand-700 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/40 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-elevated"
                >
                  Forgot password?
                </Link>
              </div>

              {error && (
                <div
                  role="alert"
                  className="flex items-start gap-2.5 rounded-lg border border-status-danger/25 bg-status-danger/8 px-3.5 py-3 text-sm text-status-danger"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" strokeWidth={1.75} />
                  <span>{error}</span>
                </div>
              )}

              <Button
                type="submit"
                disabled={isSubmitting}
                size="lg"
                className={cn(
                  "group relative w-full overflow-hidden shadow-md",
                  "motion-safe-transition hover:shadow-lg",
                )}
              >
                <span className="inline-flex items-center gap-2">
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2} />
                      Signing in…
                    </>
                  ) : (
                    <>
                      Sign in
                      <ArrowRight
                        className="h-4 w-4 motion-safe-transition group-hover:translate-x-0.5"
                        strokeWidth={2}
                      />
                    </>
                  )}
                </span>
              </Button>
            </form>

            <div className="mt-6 flex items-center gap-3">
              <div className="h-px flex-1 bg-border-subtle" />
              <span className="text-[10px] font-medium uppercase tracking-wider text-fg-muted">
                or
              </span>
              <div className="h-px flex-1 bg-border-subtle" />
            </div>

            <p className="mt-5 text-center text-sm text-fg-muted">
              New to AI-Accounts?{" "}
              <Link
                href="/signup"
                className="font-medium text-brand motion-safe-transition hover:text-brand-700 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
              >
                Create an account
              </Link>
            </p>
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-4 lg:justify-start">
            {MOBILE_FEATURES.map(({ icon: Icon, label }) => (
              <span
                key={label}
                className="inline-flex items-center gap-1.5 text-xs text-fg-muted"
              >
                <Icon className="h-3.5 w-3.5 text-brand" strokeWidth={1.75} />
                {label}
              </span>
            ))}
            <span className="hidden text-xs text-fg-muted sm:inline">·</span>
            <span className="text-xs text-fg-muted">SOC 2 aligned practices</span>
          </div>
        </div>
      </div>
    </div>
  );
}
