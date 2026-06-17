"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_PREFIX = "fa-draft:";

function storageKey(key: string) {
  return `${STORAGE_PREFIX}${key}`;
}

export interface DocumentDraftState<T> {
  hasDraft: boolean;
  draftSavedAt: string | null;
  restoreDraft: () => T | null;
  discardDraft: () => void;
  clearDraft: () => void;
  persistDraft: (values: T) => void;
}

/**
 * Local draft autosave for document forms (per browser + company-scoped key).
 */
export function useDocumentDraft<T>(draftKey: string): DocumentDraftState<T> {
  const [hasDraft, setHasDraft] = useState(false);
  const [draftSavedAt, setDraftSavedAt] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey(draftKey));
      if (raw) {
        const parsed = JSON.parse(raw) as { savedAt?: string };
        setHasDraft(true);
        setDraftSavedAt(parsed.savedAt ?? null);
      }
    } catch {
      /* ignore corrupt draft */
    }
  }, [draftKey]);

  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(storageKey(draftKey));
    } catch {
      /* ignore */
    }
    setHasDraft(false);
    setDraftSavedAt(null);
  }, [draftKey]);

  const persistDraft = useCallback(
    (values: T) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        try {
          const savedAt = new Date().toISOString();
          localStorage.setItem(
            storageKey(draftKey),
            JSON.stringify({ savedAt, values }),
          );
          setHasDraft(true);
          setDraftSavedAt(savedAt);
        } catch {
          /* quota exceeded etc. */
        }
      }, 600);
    },
    [draftKey],
  );

  const restoreDraft = useCallback((): T | null => {
    try {
      const raw = localStorage.getItem(storageKey(draftKey));
      if (!raw) return null;
      const parsed = JSON.parse(raw) as { values?: T };
      return parsed.values ?? null;
    } catch {
      return null;
    }
  }, [draftKey]);

  const discardDraft = clearDraft;

  useEffect(
    () => () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    },
    [],
  );

  return {
    hasDraft,
    draftSavedAt,
    restoreDraft,
    discardDraft,
    clearDraft,
    persistDraft,
  };
}
