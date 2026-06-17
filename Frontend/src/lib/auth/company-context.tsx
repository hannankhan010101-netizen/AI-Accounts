"use client";



import {

  createContext,

  useCallback,

  useContext,

  useEffect,

  useMemo,

  useState,

  type ReactNode,

} from "react";



import { useQueryClient } from "@tanstack/react-query";

import { useRouter } from "next/navigation";



import { resetShellHttpCache, warmupShellCache } from "@/lib/query/shell-warmup";



import { ApiError } from "@/lib/api/client";

import { withTimeout } from "@/lib/api/with-timeout";

import { companiesApi, type Company } from "@/lib/api/auth";

import { getCompanyIdFromAccessToken } from "@/lib/auth/jwt";

import {

  clearTokens,

  getCurrentCompanyId,

  getTokens,

  setCurrentCompanyId,

  setTokens,

} from "@/lib/auth/storage";



type CompanyContextValue = {

  companyId: string | null;

  companies: Company[];

  isLoading: boolean;

  bootstrapError: string | null;

  retryBootstrap: () => void;

  selectCompany: (id: string) => Promise<void>;

};



const CompanyContext = createContext<CompanyContextValue | null>(null);



export function CompanyProvider({ children }: { children: ReactNode }) {

  const router = useRouter();

  const queryClient = useQueryClient();

  const [companyId, setCompanyIdState] = useState<string | null>(null);

  const [companies, setCompanies] = useState<Company[]>([]);

  const [isLoading, setIsLoading] = useState(true);

  const [bootstrapError, setBootstrapError] = useState<string | null>(null);

  const [bootstrapAttempt, setBootstrapAttempt] = useState(0);



  /** Keep React state and localStorage aligned — tenant APIs read storage. */

  const applyCompanyId = useCallback((id: string | null) => {

    setCurrentCompanyId(id);

    setCompanyIdState(id);

  }, []);



  const selectCompany = useCallback(

    async (id: string) => {

      if (!id) return;

      const tokens = await withTimeout(

        companiesApi.switch(id),

        undefined,

        "Company switch timed out. Check that the backend is running.",

      );

      setTokens(tokens);

      applyCompanyId(id);

      resetShellHttpCache(id);

      void queryClient.invalidateQueries({ queryKey: ["tenant"] });

      void warmupShellCache(queryClient, id);

    },

    [applyCompanyId, queryClient],

  );



  useEffect(() => {

    let cancelled = false;



    async function bootstrap() {

      setBootstrapError(null);



      if (!getTokens()) {

        setIsLoading(false);

        return;

      }



      setIsLoading(true);



      try {

        const { result } = await withTimeout(

          companiesApi.list(),

          undefined,

          "Loading companies timed out. Check that the backend and database are reachable.",

        );

        if (cancelled) return;

        setCompanies(result);



        const stored = getCurrentCompanyId();

        const validStored = stored && result.some((c) => c.id === stored);

        const targetId = validStored ? stored! : result[0]?.id;



        if (targetId) {

          const accessToken = getTokens()?.accessToken;

          const tokenCompanyId = accessToken

            ? getCompanyIdFromAccessToken(accessToken)

            : null;

          const needsSwitch =

            !validStored || stored !== targetId || tokenCompanyId !== targetId;

          if (needsSwitch) {

            await selectCompany(targetId);

          } else {

            applyCompanyId(targetId);

            void warmupShellCache(queryClient, targetId);

          }

        } else {

          applyCompanyId(null);

        }

      } catch (err) {

        if (cancelled) return;



        if (err instanceof ApiError && err.status === 401) {

          clearTokens();

          router.replace("/login");

          return;

        }



        const message =

          err instanceof Error

            ? err.message

            : "Could not load your workspace. Check that the backend is running on port 8000.";

        setBootstrapError(message);

      } finally {

        if (!cancelled) setIsLoading(false);

      }

    }



    void bootstrap();

    return () => {

      cancelled = true;

    };

  }, [applyCompanyId, selectCompany, queryClient, router, bootstrapAttempt]);



  const retryBootstrap = useCallback(() => {

    setBootstrapAttempt((n) => n + 1);

  }, []);



  const value = useMemo(

    () => ({

      companyId,

      companies,

      isLoading,

      bootstrapError,

      retryBootstrap,

      selectCompany,

    }),

    [companyId, companies, isLoading, bootstrapError, retryBootstrap, selectCompany],

  );



  return <CompanyContext.Provider value={value}>{children}</CompanyContext.Provider>;

}



export function useCompany(): CompanyContextValue {

  const ctx = useContext(CompanyContext);

  if (!ctx) {

    throw new Error("useCompany must be used within CompanyProvider");

  }

  return ctx;

}

