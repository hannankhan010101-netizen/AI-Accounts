"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { FieldValues, UseFormReturn } from "react-hook-form";

import {
  clearFormDraft,
  draftsEqual,
  formDraftKey,
  readFormDraft,
  writeFormDraft,
} from "@/lib/draft/form-draft";

const DEBOUNCE_MS = 800;

interface UseFormDraftOptions<T extends FieldValues> {
  scope: string;
  companyId: string | null;
  form: UseFormReturn<T>;
  serverValues: T | undefined;
  enabled?: boolean;
}

export function useFormDraft<T extends FieldValues>({
  scope,
  companyId,
  form,
  serverValues,
  enabled = true,
}: UseFormDraftOptions<T>) {
  const [hasRecoverableDraft, setHasRecoverableDraft] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const key = companyId ? formDraftKey(companyId, scope) : null;

  useEffect(() => {
    if (!enabled || !key || serverValues === undefined) return;
    const draft = readFormDraft<T>(key);
    if (draft && !draftsEqual(draft, serverValues)) {
      setHasRecoverableDraft(true);
    } else {
      setHasRecoverableDraft(false);
    }
  }, [enabled, key, serverValues]);

  useEffect(() => {
    if (!enabled || !key) return;
    const sub = form.watch((values) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        writeFormDraft(key, values as T);
      }, DEBOUNCE_MS);
    });
    return () => {
      sub.unsubscribe();
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [enabled, key, form]);

  const restoreDraft = useCallback(() => {
    if (!key) return;
    const draft = readFormDraft<T>(key);
    if (draft) {
      form.reset(draft);
      setHasRecoverableDraft(false);
    }
  }, [key, form]);

  const discardDraft = useCallback(() => {
    if (!key) return;
    clearFormDraft(key);
    if (serverValues !== undefined) form.reset(serverValues);
    setHasRecoverableDraft(false);
  }, [key, form, serverValues]);

  const clearDraftOnSave = useCallback(() => {
    if (key) clearFormDraft(key);
    setHasRecoverableDraft(false);
  }, [key]);

  return {
    hasRecoverableDraft,
    restoreDraft,
    discardDraft,
    clearDraftOnSave,
  };
}
