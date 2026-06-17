"use client";

import { useEffect, useState } from "react";
import type { FieldValues, UseFormReturn } from "react-hook-form";

import { DocumentDraftBanner } from "@/components/patterns/document-draft-banner";
import { useDocumentDraft } from "@/lib/hooks/use-document-draft";
import { useDocumentFormGuard } from "@/lib/hooks/use-document-form-guard";

interface UseDocumentWorkspaceDraftOptions<
  TPersist extends FieldValues,
  TForm extends FieldValues = TPersist,
> {
  scope: string;
  companyId: string | null;
  form: UseFormReturn<TForm>;
  /** Values to autosave (may include side state beyond the form, e.g. allocations). */
  values: TPersist;
  /** Skip autosave, guard, and banner when false (e.g. LineGridForm without draftStorageKey). */
  enabled?: boolean;
  /** Skip autosave until user has entered something meaningful. */
  shouldPersist?: (values: TPersist) => boolean;
  /** Called after restore to apply side state (e.g. allocations). */
  onRestore?: (values: TPersist) => void;
}

/**
 * Bundles draft autosave, restore banner, and beforeunload guard for DocumentWorkspace forms.
 */
export function useDocumentWorkspaceDraft<
  TPersist extends FieldValues,
  TForm extends FieldValues = TPersist,
>({
  scope,
  companyId,
  form,
  values,
  enabled = true,
  shouldPersist = () => true,
  onRestore,
}: UseDocumentWorkspaceDraftOptions<TPersist, TForm>) {
  const draft = useDocumentDraft<TPersist>(`${scope}:${companyId ?? "none"}`);
  const [showDraftBanner, setShowDraftBanner] = useState(false);

  useDocumentFormGuard(enabled && (form.formState.isDirty || draft.hasDraft));

  useEffect(() => {
    if (enabled && draft.hasDraft) setShowDraftBanner(true);
  }, [enabled, draft.hasDraft]);

  useEffect(() => {
    if (!enabled) return;
    if (shouldPersist(values)) draft.persistDraft(values);
  }, [enabled, values, draft, shouldPersist]);

  const topBanner =
    enabled && showDraftBanner && draft.hasDraft ? (
      <DocumentDraftBanner
        savedAt={draft.draftSavedAt}
        onRestore={() => {
          const restored = draft.restoreDraft();
          if (restored) {
            form.reset(restored as unknown as TForm);
            onRestore?.(restored);
          }
          setShowDraftBanner(false);
        }}
        onDiscard={() => {
          draft.discardDraft();
          setShowDraftBanner(false);
        }}
      />
    ) : undefined;

  return {
    draft,
    topBanner,
    clearDraftOnSuccess: () => {
      draft.clearDraft();
      setShowDraftBanner(false);
    },
  };
}
