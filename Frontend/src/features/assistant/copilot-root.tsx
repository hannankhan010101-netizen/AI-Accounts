"use client";

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

import { CopilotFAB } from "@/features/assistant/components/copilot-fab";
import { CopilotPanel } from "@/features/assistant/components/copilot-panel";

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
