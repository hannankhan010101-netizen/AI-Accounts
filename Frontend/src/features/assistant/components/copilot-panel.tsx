"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useQuery } from "@tanstack/react-query";
import { Bot, RotateCcw, X } from "lucide-react";
import { useCallback, useEffect } from "react";

import { AssistantDrawer } from "@/components/assistant/assistant-drawer";
import { AssistantComposer } from "@/features/assistant/components/assistant-composer";
import { AssistantMessageList } from "@/features/assistant/components/assistant-message-list";
import { AssistantWelcome } from "@/features/assistant/components/assistant-welcome";
import { QuickActions } from "@/features/assistant/components/quick-actions";
import { InlineAlert } from "@/components/ui/inline-alert";
import { useAssistantChat } from "@/features/assistant/hooks/use-assistant-chat";
import { t } from "@/features/assistant/i18n";
import { useAssistant } from "@/features/assistant/providers/assistant-provider";
import { assistantApi } from "@/lib/api/assistant";
import { useCopilotStore } from "@/stores/assistant/copilot-store";
import { cn } from "@/lib/utils";

type CopilotPanelProps = {
  mode?: "erp" | "onboarding";
};

export function CopilotPanel({ mode: modeProp }: CopilotPanelProps) {
  const { pathname, screen, closeCopilot } = useAssistant();
  const open = useCopilotStore((s) => s.open);
  const mode = useCopilotStore((s) => s.mode);
  const messages = useCopilotStore((s) => s.messages);
  const status = useCopilotStore((s) => s.status);
  const streamingContent = useCopilotStore((s) => s.streamingContent);
  const error = useCopilotStore((s) => s.error);
  const errorRetryable = useCopilotStore((s) => s.errorRetryable);
  const pendingTool = useCopilotStore((s) => s.pendingTool);
  const draft = useCopilotStore((s) => s.draft);
  const setDraft = useCopilotStore((s) => s.setDraft);
  const setOpen = useCopilotStore((s) => s.setOpen);
  const resetConversation = useCopilotStore((s) => s.resetConversation);
  const setMode = useCopilotStore((s) => s.setMode);
  const threadId = useCopilotStore((s) => s.threadId);
  const { sendMessage, retryLastMessage, cancel } = useAssistantChat();
  const isOnboarding = (modeProp ?? mode) === "onboarding";
  const isBusy = status === "streaming" || status === "awaiting_tool";

  useEffect(() => {
    if (modeProp) setMode(modeProp);
  }, [modeProp, setMode]);

  useEffect(() => {
    if (!open || !threadId || messages.length > 0) return;
    void assistantApi.getThreadMessages(threadId).then((res) => {
      const loaded = res.result.messages.filter(
        (m) => m.role === "user" || m.role === "assistant",
      );
      if (loaded.length > 0) {
        useCopilotStore.setState({ messages: loaded });
      }
    });
  }, [open, threadId, messages.length]);

  const { data: suggestionsData } = useTenantListQuery(
    ["assistant-suggestions", pathname],
    () => assistantApi.getSuggestions(pathname),
    { enabled: open, staleTime: 30_000 },
  );

  const handleSend = useCallback(async () => {
    const text = draft;
    setDraft("");
    await sendMessage(text);
  }, [draft, sendMessage, setDraft]);

  const handleClose = () => {
    cancel();
    setOpen(false);
    closeCopilot();
  };

  const showWelcome =
    messages.length === 0 && !streamingContent && status !== "streaming" && status !== "awaiting_tool";

  return (
    <AssistantDrawer
      open={open}
      onClose={handleClose}
      title={
        <div>
          <h2 className="flex items-center gap-1.5 text-sm font-semibold text-fg">
            <Bot className="h-4 w-4 text-brand dark:text-brand-400" aria-hidden />
            {isOnboarding ? t("en", "onboardingTitle") : t("en", "title")}
          </h2>
          <p className="mt-0.5 flex items-center gap-1.5 text-[11px] text-fg-muted">
            <span
              className={cn(
                "inline-flex h-1.5 w-1.5 shrink-0 rounded-full",
                isBusy ? "animate-pulse bg-status-warning" : "bg-status-success",
              )}
              aria-hidden
            />
            {!isOnboarding ? (
              <>
                <span>{t("en", "subtitle")}</span>
                <span className="truncate font-medium text-fg">{screen.title}</span>
              </>
            ) : (
              <span>{t("en", "onboardingSubtitle")}</span>
            )}
          </p>
        </div>
      }
      headerAction={
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => resetConversation()}
            className="rounded-lg p-1.5 text-fg-muted hover:bg-surface-muted focus-ring"
            aria-label={t("en", "newChat")}
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg p-1.5 text-fg-muted hover:bg-surface-muted focus-ring"
            aria-label={t("en", "close")}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      }
      className="z-[calc(var(--z-tour)+4)]"
    >
      <QuickActions
        screen={screen}
        suggestions={suggestionsData?.result.suggestions}
        onSelect={(text) => {
          setDraft("");
          void sendMessage(text);
        }}
      />
      <div className="min-h-0 flex-1 overflow-y-auto bg-gradient-to-b from-canvas/30 to-transparent dark:from-transparent">
        {showWelcome ? <AssistantWelcome screenTitle={screen.title} /> : null}
        <AssistantMessageList
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={status === "streaming"}
          status={status}
          pendingToolName={pendingTool?.name ?? null}
        />
        {error && (
          <div className="px-4 pb-2">
            <InlineAlert variant="error" role="alert" className="flex-wrap gap-2">
              <span className="flex-1 text-sm">{error}</span>
              {errorRetryable && (
                <button
                  type="button"
                  onClick={() => void retryLastMessage()}
                  disabled={isBusy}
                  className="shrink-0 rounded-md border border-status-danger/30 bg-surface px-2 py-1 text-xs font-medium text-fg hover:bg-canvas focus-ring disabled:opacity-50"
                >
                  {t("en", "retry")}
                </button>
              )}
            </InlineAlert>
          </div>
        )}
      </div>
      <AssistantComposer
        value={draft}
        onChange={setDraft}
        onSubmit={() => void handleSend()}
        disabled={isBusy}
        isBusy={isBusy}
        onStop={cancel}
      />
    </AssistantDrawer>
  );
}
