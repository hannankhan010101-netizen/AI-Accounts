/** User profile — catalog §2.3 / §12.1 session rail. */
"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { authApi } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";


const schema = z.object({
  firstName: z.string().min(1, "Required"),
  lastName: z.string().min(1, "Required"),
  phone: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: profile, isLoading } = useTenantReferenceQuery(["auth-me"], () => authApi.me());

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: profile
      ? {
          firstName: profile.firstName,
          lastName: profile.lastName,
          phone: profile.phone ?? "",
        }
      : undefined,
  });

  const save = useMutation({
    mutationFn: (values: FormValues) =>
      authApi.updateProfile({
        firstName: values.firstName,
        lastName: values.lastName,
        phone: values.phone?.trim() || null,
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["auth-me"], updated);
      reset({
        firstName: updated.firstName,
        lastName: updated.lastName,
        phone: updated.phone ?? "",
      });
      setError(null);
      setMessage("Profile saved.");
    },
    onError: (err) => {
      setMessage(null);
      setError(err instanceof ApiError ? err.message : "Could not save profile.");
    },
  });

  return (
    <>
      <PageHeader
        title="Profile"
        breadcrumb="Account / Profile"
        description="Your name and contact details across all companies."
        actions={
          <Link
            href="/profile/change-password"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
          >
            Change password
          </Link>
        }
      />

      {isLoading && <p className="text-sm text-fg-muted">Loading profile…</p>}

      <form
        onSubmit={handleSubmit((values) => save.mutate(values))}
        className="max-w-lg space-y-4 rounded-lg border border-border bg-surface p-6"
      >
        <FormField label="Email">
          <Input value={profile?.email ?? ""} disabled readOnly />
        </FormField>
        <FormField label="First name" error={errors.firstName?.message}>
          <Input {...register("firstName")} />
        </FormField>
        <FormField label="Last name" error={errors.lastName?.message}>
          <Input {...register("lastName")} />
        </FormField>
        <FormField label="Phone" error={errors.phone?.message}>
          <Input {...register("phone")} />
        </FormField>
        {message && <p className="text-sm text-status-success">{message}</p>}
        {error && <p className="text-sm text-status-danger">{error}</p>}
        <Button type="submit" disabled={!isDirty || save.isPending}>
          {save.isPending ? "Saving…" : "Save profile"}
        </Button>
      </form>
    </>
  );
}
