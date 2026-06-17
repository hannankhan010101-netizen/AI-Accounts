"use client";

import { Bot, User } from "lucide-react";

import { cn } from "@/lib/utils";

type AssistantAvatarProps = {
  role: "assistant" | "user";
  pulse?: boolean;
  className?: string;
};

export function AssistantAvatar({ role, pulse, className }: AssistantAvatarProps) {
  const isBot = role === "assistant";

  return (
    <div
      className={cn(
        "relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
        isBot
          ? "bg-brand-600/12 text-brand-700 dark:bg-brand-400/15 dark:text-brand-200"
          : "bg-surface-muted text-fg-muted",
        className,
      )}
      aria-hidden
    >
      {pulse && isBot ? (
        <span className="absolute inset-0 animate-ping rounded-full bg-brand-400/25 motion-reduce:animate-none" />
      ) : null}
      {isBot ? (
        <Bot className="relative h-4 w-4" />
      ) : (
        <User className="relative h-4 w-4" />
      )}
    </div>
  );
}
