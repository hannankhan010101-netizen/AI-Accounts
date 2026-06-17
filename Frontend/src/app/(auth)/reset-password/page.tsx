"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { AuthFormSkeleton } from "@/components/auth/auth-form-skeleton";

const schema = z.object({
  email: z.string().email(),
  otpCode: z.string().regex(/^\d{6}$/u, "6-digit code"),
  newPassword: z.string().min(8),
});
type FormValues = z.infer<typeof schema>;

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: params.get("email") ?? "", otpCode: "", newPassword: "" },
  });

  const isInvite = params.get("invite") === "1";

  const onSubmit = handleSubmit(async (values) => {
    setError(null);
    try {
      if (isInvite) {
        await authApi.acceptInvite(values);
      } else {
        await authApi.resetPassword(values);
      }
      router.push("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Reset failed");
    }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-fg">
          {isInvite ? "Set your password" : "Reset password"}
        </h1>
        <p className="text-sm text-fg-muted">
          {isInvite
            ? "Enter the code from your invite email and choose a password."
            : "Enter the code and your new password."}
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <FormField label="Email" htmlFor="email" required error={errors.email?.message}>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
        </FormField>
        <FormField label="Verification code" htmlFor="otpCode" required error={errors.otpCode?.message}>
          <Input id="otpCode" inputMode="numeric" maxLength={6} autoComplete="one-time-code" {...register("otpCode")} />
        </FormField>
        <FormField label="New password" htmlFor="newPassword" required error={errors.newPassword?.message}>
          <Input id="newPassword" type="password" autoComplete="new-password" {...register("newPassword")} />
        </FormField>

        {error && (
          <div role="alert" className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Saving…" : isInvite ? "Set password" : "Reset password"}
        </Button>
      </form>

      <Link href="/login" className="text-sm text-brand hover:underline">
        Back to sign in
      </Link>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<AuthFormSkeleton />}>
      <ResetForm />
    </Suspense>
  );
}
