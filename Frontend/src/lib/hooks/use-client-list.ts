"use client";



import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { useCallback, useMemo, useState } from "react";



import {

  listSearchHref,

  parseListPage,

  parseListQuery,

  patchListSearchParams,

} from "@/lib/navigation/list-search-params";



const DEFAULT_PAGE_SIZE = 25;



export interface UseClientListOptions<T> {

  rows: T[] | undefined;

  pageSize?: number;

  /** Return true if row matches query (lowercase) */

  filterFn?: (row: T, query: string) => boolean;

  /** Persist `q` and `page` in the URL (bookmarkable list state) */

  syncUrl?: boolean;

}



export function useClientList<T>({

  rows,

  pageSize = DEFAULT_PAGE_SIZE,

  filterFn,

  syncUrl = false,

}: UseClientListOptions<T>) {

  const router = useRouter();

  const pathname = usePathname();

  const searchParams = useSearchParams();



  const [localPage, setLocalPage] = useState(1);

  const [localSearch, setLocalSearch] = useState("");



  const page = syncUrl ? parseListPage(searchParams) : localPage;

  const search = syncUrl ? parseListQuery(searchParams) : localSearch;



  const replaceUrl = useCallback(

    (patch: Parameters<typeof patchListSearchParams>[1]) => {

      const next = patchListSearchParams(searchParams, patch);

      router.replace(listSearchHref(pathname, next), { scroll: false });

    },

    [router, pathname, searchParams],

  );



  const setPage = useCallback(

    (p: number) => {

      if (syncUrl) replaceUrl({ page: p });

      else setLocalPage(p);

    },

    [syncUrl, replaceUrl],

  );



  const setSearch = useCallback(

    (q: string) => {

      if (syncUrl) replaceUrl({ q });

      else {

        setLocalSearch(q);

        setLocalPage(1);

      }

    },

    [syncUrl, replaceUrl],

  );



  const all = rows ?? [];



  const filtered = useMemo(() => {

    const q = search.trim().toLowerCase();

    if (!q || !filterFn) return all;

    return all.filter((row) => filterFn(row, q));

  }, [all, search, filterFn]);



  const pageRows = useMemo(() => {

    const start = (page - 1) * pageSize;

    return filtered.slice(start, start + pageSize);

  }, [filtered, page, pageSize]);



  return {

    search,

    setSearch,

    page,

    setPage,

    filtered,

    pageRows,

    totalItems: filtered.length,

    pagination: {

      page,

      pageSize,

      totalItems: filtered.length,

      onPageChange: setPage,

    },

  };

}


