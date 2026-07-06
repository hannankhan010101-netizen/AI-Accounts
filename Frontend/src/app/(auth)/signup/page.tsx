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
import { setTokens } from "@/lib/auth/storage";
import { ApiError } from "@/lib/api/client";

const schema = z.object({
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  email: z.string().email(),
  password: z.string().min(8),
  companyName: z.string().min(1),
});
type FormValues = z.infer<typeof schema>;

export default function SignUpPage() {
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
      const result = await authApi.signUp(values);
      // When email verification is skipped server-side, sign-up returns tokens
      // directly — sign the user in and go straight to the dashboard.
      if ("accessToken" in result) {
        setTokens(result);
        sessionStorage.removeItem("devOtp");
        router.push("/dashboard");
        return;
      }
      if (result.devOtp) {
        sessionStorage.setItem("devOtp", result.devOtp);
      } else {
        sessionStorage.removeItem("devOtp");
      }
      router.push(`/verify-email?email=${encodeURIComponent(result.email)}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Sign up failed");
    }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-fg">Create your account</h1>
        <p className="text-sm text-fg-muted">
          We&apos;ll send a 6-digit code to verify your email.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-3 xs:grid-cols-2">
          <FormField label="First name" htmlFor="firstName" required error={errors.firstName?.message}>
            <Input id="firstName" autoComplete="given-name" {...register("firstName")} />
          </FormField>
          <FormField label="Last name" htmlFor="lastName" required error={errors.lastName?.message}>
            <Input id="lastName" autoComplete="family-name" {...register("lastName")} />
          </FormField>
        </div>
        <FormField label="Email" htmlFor="email" required error={errors.email?.message}>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
        </FormField>
        <FormField label="Password" htmlFor="password" required error={errors.password?.message}>
          <Input id="password" type="password" autoComplete="new-password" {...register("password")} />
        </FormField>
        <FormField label="Company name" htmlFor="companyName" required error={errors.companyName?.message}>
          <Input id="companyName" autoComplete="organization" {...register("companyName")} />
        </FormField>

        {error && (
          <div role="alert" className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Creating…" : "Create account"}
        </Button>
      </form>

      <p className="text-sm text-fg-muted">
        Already have an account?{" "}
        <Link href="/login" className="text-brand hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
