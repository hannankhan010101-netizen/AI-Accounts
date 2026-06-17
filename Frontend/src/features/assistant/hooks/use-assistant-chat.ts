"use client";

import { useCallback, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";

import { executeClientTool } from "@/features/assistant/tools/client-tool-executor";
import { formatAssistantError } from "@/features/assistant/errors";
import { assistantApi, type AssistantStreamEvent } from "@/lib/api/assistant";
import { isAbortError } from "@/lib/api/abort-error";
import { resolveScreenContext } from "@/lib/assistant/screen-registry";
import { useTour } from "@/lib/tour/tour-context";
import { useCopilotStore } from "@/stores/assistant/copilot-store";

export function useAssistantChat() {
  const router = useRouter();
  const pathname = usePathname();
  const { startTour } = useTour();
  const abortRef = useRef<AbortController | null>(null);
  const streamGenerationRef = useRef(0);

  const threadId = useCopilotStore((s) => s.threadId);
  const mode = useCopilotStore((s) => s.mode);
  const setThreadId = useCopilotStore((s) => s.setThreadId);
  const setStatus = useCopilotStore((s) => s.setStatus);
  const setError = useCopilotStore((s) => s.setError);
  const setLastFailedUserMessage = useCopilotStore(
    (s) => s.setLastFailedUserMessage,
  );
  const pushMessage = useCopilotStore((s) => s.pushMessage);
  const appendToken = useCopilotStore((s) => s.appendToken);
  const flushStreamingToMessage = useCopilotStore((s) => s.flushStreamingToMessage);
  const setPendingTool = useCopilotStore((s) => s.setPendingTool);

  const handleEvent = useCallback(
    async (event: AssistantStreamEvent) => {
      if (event.type === "thread" && event.threadId) {
        setThreadId(event.threadId);
      }
      if (event.type === "token") {
        appendToken(event.content);
      }
      if (event.type === "tool_call") {
        flushStreamingToMessage();
        setPendingTool({
          threadId: event.threadId,
          toolCallId: event.toolCallId,
          name: event.name,
          arguments: event.arguments,
        });
        const result = await executeClientTool(event.name, event.arguments, {
          router,
          pathname,
          startTour,
        });
        setStatus("streaming");
        await assistantApi.postToolResult(
          {
            threadId: event.threadId,
            toolCallId: event.toolCallId,
            result,
          },
          (e) => void handleEvent(e),
          abortRef.current?.signal,
        );
        setPendingTool(null);
      }
      if (event.type === "done") {
        flushStreamingToMessage();
        setStatus("idle");
      }
      if (event.type === "error") {
        if (
          event.message.toLowerCase().includes("abort") ||
          event.message.toLowerCase().includes("aborted")
        ) {
          return;
        }
        setError(formatAssistantError(event.message, event.code), {
          retryable: event.retryable === true,
        });
        setStatus("error");
        flushStreamingToMessage();
      }
    },
    [
      appendToken,
      flushStreamingToMessage,
      pathname,
      router,
      setError,
      setPendingTool,
      setStatus,
      setThreadId,
      startTour,
    ],
  );

  const streamToAssistant = useCallback(
    async (
      trimmed: string,
      options?: { locale?: string; skipUserBubble?: boolean },
    ) => {
      const generation = ++streamGenerationRef.current;
      abortRef.current?.abort();
      abortRef.current = new AbortController();

      setError(null);
      setLastFailedUserMessage(trimmed);
      setStatus("streaming");
      if (!options?.skipUserBubble) {
        pushMessage({ role: "user", content: trimmed });
      }

      const screen = resolveScreenContext(pathname);
      try {
        await assistantApi.streamChat(
          {
            message: trimmed,
            pathname,
            threadId,
            locale: options?.locale ?? "en",
            mode: mode === "onboarding" ? "onboarding" : undefined,
            entityContext: {
              module: screen.module,
              title: screen.title,
            },
          },
          (e) => void handleEvent(e),
          abortRef.current.signal,
        );
      } catch (err) {
        if (isAbortError(err) || streamGenerationRef.current !== generation) {
          return;
        }
        const msg = err instanceof Error ? err.message : "Stream failed";
        setError(msg, { retryable: true });
        setStatus("error");
        flushStreamingToMessage();
      } finally {
        if (streamGenerationRef.current !== generation) return;
        const st = useCopilotStore.getState().status;
        if (st === "streaming") {
          flushStreamingToMessage();
          setStatus("idle");
        }
      }
    },
    [
      handleEvent,
      mode,
      pathname,
      pushMessage,
      setError,
      setLastFailedUserMessage,
      setStatus,
      threadId,
      flushStreamingToMessage,
    ],
  );

  const sendMessage = useCallback(
    async (message: string, options?: { locale?: string }) => {
      const trimmed = message.trim();
      if (!trimmed) return;
      await streamToAssistant(trimmed, options);
    },
    [streamToAssistant],
  );

  const retryLastMessage = useCallback(async () => {
    const prompt = useCopilotStore.getState().lastFailedUserMessage?.trim();
    if (!prompt) return;
    await streamToAssistant(prompt, { skipUserBubble: true });
  }, [streamToAssistant]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    flushStreamingToMessage();
    setError(null);
    setStatus("idle");
  }, [flushStreamingToMessage, setError, setStatus]);

  return { sendMessage, retryLastMessage, cancel };
}
