"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AssistantMessage } from "@/lib/api/assistant";

export type CopilotStatus = "idle" | "streaming" | "awaiting_tool" | "error";

export type PendingToolCall = {
  threadId: string;
  toolCallId: string;
  name: string;
  arguments: Record<string, unknown>;
};

type CopilotState = {
  open: boolean;
  mode: "erp" | "onboarding";
  threadId: string | null;
  messages: AssistantMessage[];
  status: CopilotStatus;
  streamingContent: string;
  error: string | null;
  errorRetryable: boolean;
  lastFailedUserMessage: string | null;
  pendingTool: PendingToolCall | null;
  fabPosition: { x: number; y: number } | null;
  draft: string;
  setOpen: (open: boolean) => void;
  setMode: (mode: "erp" | "onboarding") => void;
  setThreadId: (id: string | null) => void;
  setDraft: (draft: string) => void;
  setStatus: (status: CopilotStatus) => void;
  setError: (error: string | null, options?: { retryable?: boolean }) => void;
  setLastFailedUserMessage: (message: string | null) => void;
  pushMessage: (msg: AssistantMessage) => void;
  appendToken: (token: string) => void;
  flushStreamingToMessage: () => void;
  setPendingTool: (tool: PendingToolCall | null) => void;
  resetConversation: () => void;
  setFabPosition: (pos: { x: number; y: number } | null) => void;
};

export const useCopilotStore = create<CopilotState>()(
  persist(
    (set, get) => ({
      open: false,
      mode: "erp",
      threadId: null,
      messages: [],
      status: "idle",
      streamingContent: "",
      error: null,
      errorRetryable: false,
      lastFailedUserMessage: null,
      pendingTool: null,
      fabPosition: null,
      draft: "",
      setOpen: (open) => set({ open }),
      setMode: (mode) => set({ mode }),
      setThreadId: (threadId) => set({ threadId }),
      setDraft: (draft) => set({ draft }),
      setStatus: (status) => set({ status }),
      setError: (error, options) =>
        set({
          error,
          errorRetryable: options?.retryable ?? false,
          ...(error === null
            ? { errorRetryable: false, lastFailedUserMessage: null }
            : {}),
        }),
      setLastFailedUserMessage: (lastFailedUserMessage) =>
        set({ lastFailedUserMessage }),
      pushMessage: (msg) =>
        set((s) => ({ messages: [...s.messages, msg] })),
      appendToken: (token) =>
        set((s) => ({ streamingContent: s.streamingContent + token })),
      flushStreamingToMessage: () => {
        const content = get().streamingContent.trim();
        if (content) {
          set((s) => ({
            messages: [
              ...s.messages,
              { role: "assistant" as const, content },
            ],
            streamingContent: "",
          }));
        } else {
          set({ streamingContent: "" });
        }
      },
      setPendingTool: (pendingTool) =>
        set((s) => ({
          pendingTool,
          status: pendingTool ? "awaiting_tool" : s.status === "awaiting_tool" ? "streaming" : s.status,
        })),
      resetConversation: () =>
        set({
          threadId: null,
          messages: [],
          streamingContent: "",
          error: null,
          errorRetryable: false,
          lastFailedUserMessage: null,
          pendingTool: null,
          status: "idle",
        }),
      setFabPosition: (fabPosition) => set({ fabPosition }),
    }),
    {
      name: "fa-assistant:copilot",
      partialize: (s) => ({ fabPosition: s.fabPosition }),
    },
  ),
);
