"use client";

import dynamic from "next/dynamic";
import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

import { CopilotFAB } from "@/features/assistant/components/copilot-fab";

// The panel pulls in react-markdown/remark/rehype; keep it out of the shared bundle.
const CopilotPanel = dynamic(
  () =>
    import("@/features/assistant/components/copilot-panel").then(
      (mod) => mod.CopilotPanel,
    ),
  { ssr: false },
);

export function CopilotRoot() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return createPortal(
    <>
      <CopilotFAB />
      <CopilotPanel />
    </>,
    document.body,
  );
}
