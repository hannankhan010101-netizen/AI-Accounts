"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

const schema = z.object({ email: z.string().email() });
type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      const result = await authApi.forgotPassword(values);
      const email = encodeURIComponent(values.email);
      if ("expiresAt" in result) {
        if (result.devOtp) {
          sessionStorage.setItem("devOtp", result.devOtp);
        }
        router.push(`/verify-email?email=${email}`);
        return;
      }
      router.push(`/reset-password?email=${email}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Request failed");
    }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-fg">Forgot password</h1>
        <p className="text-sm text-fg-muted">
          Enter your email and we&apos;ll send a 6-digit reset code.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <FormField label="Email" htmlFor="email" required error={errors.email?.message}>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
        </FormField>

        {error && (
          <div role="alert" className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Sending…" : "Send reset code"}
        </Button>
      </form>

      <Link href="/login" className="text-sm text-brand hover:underline">
        Back to sign in
      </Link>
    </div>
  );
}
