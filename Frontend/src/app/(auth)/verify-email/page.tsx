"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { authApi } from "@/lib/api/auth";
import { setTokens } from "@/lib/auth/storage";
import { ApiError } from "@/lib/api/client";
import { AuthFormSkeleton } from "@/components/auth/auth-form-skeleton";

const schema = z.object({
  email: z.string().email(),
  otpCode: z.string().regex(/^\d{6}$/u, "6-digit code"),
});
type FormValues = z.infer<typeof schema>;

function VerifyForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [resentMessage, setResentMessage] = useState<string | null>(null);
  const [devOtp, setDevOtp] = useState<string | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("devOtp");
    if (stored) setDevOtp(stored);
  }, []);
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: params.get("email") ?? "", otpCode: "" },
  });

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      const tokens = await authApi.verifyEmail(values);
      setTokens(tokens);
      sessionStorage.removeItem("devOtp");
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Verification failed");
    }
  });

  async function resend() {
    setError(null);
    setResentMessage(null);
    try {
      const email = getValues("email");
      const result = await authApi.resendOtp({ email, purpose: "signup" });
      if ("devOtp" in result && result.devOtp) {
        sessionStorage.setItem("devOtp", result.devOtp);
        setDevOtp(result.devOtp);
        setResentMessage(
          result.message?.includes("could not deliver")
            ? "Email could not be delivered — use the code below."
            : "New code generated (shown below).",
        );
      } else {
        sessionStorage.removeItem("devOtp");
        setDevOtp(null);
        setResentMessage("New code sent to your email. Check inbox and spam.");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not resend code");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-fg">Verify your email</h1>
        <p className="text-sm text-fg-muted">Enter the 6-digit code sent to your inbox.</p>
      </div>

      {devOtp && (
        <div className="alert-warning-surface rounded-md px-3 py-2 text-sm">
          <p className="font-medium">Development code (email not configured)</p>
          <p className="mt-1 font-mono text-lg tracking-widest">{devOtp}</p>
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <FormField label="Email" htmlFor="email" required error={errors.email?.message}>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
        </FormField>
        <FormField label="Verification code" htmlFor="otpCode" required error={errors.otpCode?.message}>
          <Input id="otpCode" inputMode="numeric" maxLength={6} autoComplete="one-time-code" {...register("otpCode")} />
        </FormField>

        {error && (
          <div role="alert" className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}
        {resentMessage && (
          <div role="status" className="rounded-md border border-status-success/30 bg-status-success/10 px-3 py-2 text-sm text-status-success">
            {resentMessage}
          </div>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Verifying…" : "Verify"}
        </Button>
        <Button type="button" variant="ghost" className="w-full" onClick={resend}>
          Resend code
        </Button>
      </form>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<AuthFormSkeleton />}>
      <VerifyForm />
    </Suspense>
  );
}
