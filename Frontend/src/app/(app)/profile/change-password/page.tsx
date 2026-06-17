/** Change password — catalog §2.3 session rail. */
"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

const schema = z
  .object({
    currentPassword: z.string().min(8, "Min 8 characters"),
    newPassword: z.string().min(8, "Min 8 characters"),
    confirmPassword: z.string().min(8, "Min 8 characters"),
  })
  .refine((v) => v.newPassword === v.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });
type FormValues = z.infer<typeof schema>;

export default function ChangePasswordPage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const save = useMutation({
    mutationFn: (values: FormValues) =>
      authApi.changePassword({
        currentPassword: values.currentPassword,
        newPassword: values.newPassword,
      }),
    onSuccess: (res) => {
      reset();
      setError(null);
      setMessage(res.message);
    },
    onError: (err) => {
      setMessage(null);
      setError(err instanceof ApiError ? err.message : "Could not change password.");
    },
  });

  return (
    <>
      <PageHeader
        title="Change password"
        breadcrumb="Account / Change password"
        actions={
          <Link
            href="/profile"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
          >
            ← Profile
          </Link>
        }
      />

      <form
        onSubmit={handleSubmit((values) => save.mutate(values))}
        className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField label="Current password" error={errors.currentPassword?.message}>
          <Input type="password" autoComplete="current-password" {...register("currentPassword")} />
        </FormField>
        <FormField label="New password" error={errors.newPassword?.message}>
          <Input type="password" autoComplete="new-password" {...register("newPassword")} />
        </FormField>
        <FormField label="Confirm new password" error={errors.confirmPassword?.message}>
          <Input type="password" autoComplete="new-password" {...register("confirmPassword")} />
        </FormField>
        {message && <p className="text-sm text-status-success">{message}</p>}
        {error && <p className="text-sm text-status-danger">{error}</p>}
        <Button type="submit" disabled={save.isPending}>
          {save.isPending ? "Updating…" : "Update password"}
        </Button>
      </form>
    </>
  );
}
