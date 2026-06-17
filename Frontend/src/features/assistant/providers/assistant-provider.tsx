"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { usePathname } from "next/navigation";

import { resolveScreenContext, type ScreenContext } from "@/lib/assistant/screen-registry";
import { useCopilotStore } from "@/stores/assistant/copilot-store";

type PageContextValue = Record<string, unknown>;

const PageContext = createContext<{
  pageContext: PageContextValue;
  setPageContext: (ctx: PageContextValue) => void;
} | null>(null);

export function AssistantPageProvider({
  children,
  value,
}: {
  children: ReactNode;
  value?: PageContextValue;
}) {
  const [pageContext, setPageContext] = useState<PageContextValue>(value ?? {});
  const merged = useMemo(
    () => ({ pageContext, setPageContext }),
    [pageContext],
  );
  return <PageContext.Provider value={merged}>{children}</PageContext.Provider>;
}

export function useAssistantPageContext() {
  const ctx = useContext(PageContext);
  return ctx?.pageContext ?? {};
}

type AssistantContextValue = {
  pathname: string;
  screen: ScreenContext;
  openCopilot: (opts?: { mode?: "erp" | "onboarding"; draft?: string }) => void;
  closeCopilot: () => void;
};

const AssistantContext = createContext<AssistantContextValue | null>(null);

export function AssistantProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const setOpen = useCopilotStore((s) => s.setOpen);
  const setMode = useCopilotStore((s) => s.setMode);
  const setDraft = useCopilotStore((s) => s.setDraft);

  const screen = useMemo(() => resolveScreenContext(pathname), [pathname]);

  const openCopilot = useCallback(
    (opts?: { mode?: "erp" | "onboarding"; draft?: string }) => {
      if (opts?.mode) setMode(opts.mode);
      if (opts?.draft) setDraft(opts.draft);
      setOpen(true);
    },
    [setDraft, setMode, setOpen],
  );

  const closeCopilot = useCallback(() => setOpen(false), [setOpen]);

  const value = useMemo(
    () => ({ pathname, screen, openCopilot, closeCopilot }),
    [closeCopilot, openCopilot, pathname, screen],
  );

  return (
    <AssistantContext.Provider value={value}>{children}</AssistantContext.Provider>
  );
}

export function useAssistant() {
  const ctx = useContext(AssistantContext);
  if (!ctx) throw new Error("useAssistant must be used within AssistantProvider");
  return ctx;
}
