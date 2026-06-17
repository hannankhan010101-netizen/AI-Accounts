"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { useState, type ReactNode } from "react";

import { ThemeProvider } from "@/components/providers/theme-provider";
import { MotionProvider } from "@/components/motion/motion-provider";
import { ToastProvider } from "@/components/ui/toast";
import { GC_DEFAULT_MS, STALE_LIST_MS } from "@/lib/query/defaults";
import {
  createSessionQueryPersister,
  shouldPersistTenantQuery,
} from "@/lib/query/persist";

export function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: STALE_LIST_MS,
            gcTime: GC_DEFAULT_MS,
            retry: 1,
            refetchOnMount: true,
            refetchOnWindowFocus: true,
            refetchOnReconnect: true,
          },
        },
      }),
  );
  const [persister] = useState(() => createSessionQueryPersister());

  const content = (
    <ThemeProvider>
      <ToastProvider>
        <MotionProvider>{children}</MotionProvider>
      </ToastProvider>
    </ThemeProvider>
  );

  if (!persister) {
    return <QueryClientProvider client={client}>{content}</QueryClientProvider>;
  }

  return (
    <PersistQueryClientProvider
      client={client}
      persistOptions={{
        persister,
        dehydrateOptions: {
          shouldDehydrateQuery: shouldPersistTenantQuery,
        },
      }}
    >
      {content}
    </PersistQueryClientProvider>
  );
}
