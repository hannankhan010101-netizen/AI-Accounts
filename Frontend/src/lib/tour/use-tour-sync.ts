"use client";

import { useCallback, useRef } from "react";

import { tourApi } from "@/lib/api/tour";
import { mergeTourProgress } from "@/lib/tour/merge-progress";
import { normalizeTourProgress } from "@/lib/tour/normalize-progress";
import { readProgress, writeProgress } from "@/lib/tour/progress-store";
import type { ReleaseItem, UserTourProgress } from "@/lib/tour/types";

const PUT_DEBOUNCE_MS = 600;

export function useTourSync(companyId: string | null, userKey: string) {
  const putTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadMerged = useCallback(async (): Promise<{
    progress: UserTourProgress;
    roleName: string | null;
    permissions: string[];
    releases: ReleaseItem[];
  } | null> => {
    if (!companyId) return null;
    const local = readProgress(companyId, userKey);
    try {
      const { result } = await tourApi.getMe({ attemptDigest: true });
      const serverProgress = normalizeTourProgress(result.progress);
      const hasServer = Object.keys(serverProgress.tours).length > 0;
      const hasLocal = Object.keys(local.tours).length > 0;
      let merged: UserTourProgress;
      if (!hasServer && hasLocal) {
        merged = local;
        void tourApi.putProgress(local);
      } else {
        merged = mergeTourProgress(serverProgress, local);
      }
      writeProgress(companyId, userKey, merged);
      return {
        progress: merged,
        roleName: result.roleName,
        permissions: result.permissions,
        releases: result.releases ?? [],
      };
    } catch {
      return { progress: local, roleName: null, permissions: [], releases: [] };
    }
  }, [companyId, userKey]);

  const schedulePut = useCallback(
    (progress: UserTourProgress) => {
      if (!companyId) return;
      writeProgress(companyId, userKey, progress);
      if (putTimer.current) clearTimeout(putTimer.current);
      putTimer.current = setTimeout(() => {
        void tourApi.putProgress(progress).catch(() => {});
      }, PUT_DEBOUNCE_MS);
    },
    [companyId, userKey],
  );

  return { loadMerged, schedulePut };
}
