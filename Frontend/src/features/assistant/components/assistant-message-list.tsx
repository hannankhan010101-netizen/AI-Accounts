"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { AnimatePresence, m } from "framer-motion";

import { AssistantAvatar } from "@/features/assistant/components/assistant-avatar";
import { AssistantThinking, AssistantToolThinking } from "@/features/assistant/components/assistant-thinking";
import { MarkdownMessage } from "@/features/assistant/components/markdown-message";
import type { CopilotStatus } from "@/stores/assistant/copilot-store";
import type { AssistantMessage } from "@/lib/api/assistant";
import { brandSolidClasses } from "@/lib/design-tokens/brand-surfaces";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type AssistantMessageListProps = {
  messages: AssistantMessage[];
  streamingContent: string;
  isStreaming: boolean;
  status: CopilotStatus;
  pendingToolName?: string | null;
};

const messageMotion = {
  hidden: { opacity: 0, y: 5 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0 },
};

const messageSpring = { type: "spring" as const, stiffness: 560, damping: 36, mass: 0.8 };

function StreamingCursor() {
  return (
    <m.span
      className="ml-0.5 inline-block h-[1em] w-0.5 translate-y-px rounded-full bg-brand-500 align-middle dark:bg-brand-400"
      animate={{ opacity: [1, 0.2, 1] }}
      transition={{ duration: 0.5, repeat: Infinity, ease: "easeInOut" }}
      aria-hidden
    />
  );
}

function ChatRow({
  role,
  children,
  animate = true,
}: {
  role: "assistant" | "user";
  children: ReactNode;
  animate?: boolean;
}) {
  const reduced = useReducedMotion();
  const isUser = role === "user";

  const content = (
    <div
      className={cn(
        "flex max-w-full gap-2.5",
        isUser ? "ml-auto flex-row-reverse" : "mr-auto",
      )}
    >
      <AssistantAvatar role={role} className={cn(isUser && "mt-0.5")} />
      <div className="min-w-0 max-w-[min(100%,18rem)] sm:max-w-[20rem]">{children}</div>
    </div>
  );

  if (!animate || reduced) return content;

  return (
    <m.div
      layout={false}
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={messageMotion}
      transition={messageSpring}
    >
      {content}
    </m.div>
  );
}

export function AssistantMessageList({
  messages,
  streamingContent,
  isStreaming,
  status,
  pendingToolName,
}: AssistantMessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  const showTokenThinking = isStreaming && !streamingContent;
  const showToolThinking = status === "awaiting_tool" && Boolean(pendingToolName);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "auto", block: "end" });
  }, [messages, streamingContent, isStreaming, status, pendingToolName]);

  const userBubbleClass = cn(
    "rounded-2xl rounded-br-md px-3 py-2 text-sm shadow-sm",
    brandSolidClasses,
  );

  const assistantBubbleClass =
    "rounded-2xl rounded-bl-md border border-border-subtle/60 bg-surface-elevated px-3 py-2 text-sm text-fg shadow-xs dark:border-transparent dark:bg-surface-muted/45 dark:shadow-sm";

  return (
    <div className="flex flex-col gap-2.5 px-3 py-3">
      <AnimatePresence initial={false} mode="popLayout">
        {messages.map((msg, i) => (
          <ChatRow key={msg.id ?? `msg-${i}`} role={msg.role === "user" ? "user" : "assistant"}>
            <div
              className={cn(
                msg.role === "user" ? userBubbleClass : assistantBubbleClass,
              )}
            >
              {msg.role === "assistant" ? (
                <MarkdownMessage content={msg.content} variant="assistant" />
              ) : (
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              )}
            </div>
          </ChatRow>
        ))}

        {streamingContent ? (
          <ChatRow role="assistant" animate={false}>
            <div className={assistantBubbleClass}>
              <MarkdownMessage content={streamingContent} variant="assistant" />
              {isStreaming ? <StreamingCursor /> : null}
            </div>
          </ChatRow>
        ) : null}

        {showToolThinking && pendingToolName ? (
          <AssistantToolThinking key="tool-thinking" toolName={pendingToolName} />
        ) : showTokenThinking ? (
          <AssistantThinking key="token-thinking" />
        ) : null}
      </AnimatePresence>
      <div ref={endRef} className="h-px shrink-0" aria-hidden />
    </div>
  );
}
