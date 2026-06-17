"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo } from "react";

import {
  listSearchHref,
  parseListPage,
  parseListQuery,
  parseListStatus,
  patchListSearchParams,
} from "@/lib/navigation/list-search-params";

/** Server-paginated lists — sync `q`, `page`, and optional `status` to the URL. */
export function useUrlServerList(pageSize = 25) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const page = useMemo(() => parseListPage(searchParams), [searchParams]);
  const search = useMemo(() => parseListQuery(searchParams), [searchParams]);
  const statusFilter = useMemo(() => parseListStatus(searchParams), [searchParams]);

  const replace = useCallback(
    (patch: Parameters<typeof patchListSearchParams>[1]) => {
      const next = patchListSearchParams(searchParams, patch);
      router.replace(listSearchHref(pathname, next), { scroll: false });
    },
    [router, pathname, searchParams],
  );

  const setPage = useCallback((p: number) => replace({ page: p }), [replace]);
  const setSearch = useCallback((q: string) => replace({ q }), [replace]);
  const setStatusFilter = useCallback(
    (status: "" | "active" | "inactive") => replace({ status }),
    [replace],
  );

  return {
    page,
    pageSize,
    search,
    setSearch,
    setPage,
    statusFilter,
    setStatusFilter,
  };
}
