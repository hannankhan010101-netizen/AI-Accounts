"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

import { cn } from "@/lib/utils";

type MarkdownMessageProps = {
  content: string;
  className?: string;
  variant?: "assistant" | "user";
};

const assistantMarkdownClass =
  "text-sm leading-relaxed text-fg [&_p]:my-1.5 [&_p:first-child]:mt-0 [&_p:last-child]:mb-0 [&_ul]:my-1.5 [&_ol]:my-1.5 [&_li]:text-fg [&_strong]:font-semibold [&_strong]:text-fg [&_a]:font-medium [&_a]:text-brand-700 [&_a]:underline [&_a:hover]:text-brand-800 dark:[&_a]:text-brand-300 dark:[&_a:hover]:text-brand-200 [&_code]:rounded [&_code]:bg-surface-muted [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-xs [&_code]:text-fg [&_pre]:my-2 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:border [&_pre]:border-border-subtle [&_pre]:bg-surface-muted [&_pre]:p-2 [&_pre]:text-xs [&_pre]:text-fg";

const userMarkdownClass =
  "text-sm leading-relaxed text-inherit [&_p]:my-1 [&_a]:text-inherit [&_a]:underline [&_code]:rounded [&_code]:bg-white/15 [&_code]:px-1";

export function MarkdownMessage({ content, className, variant = "assistant" }: MarkdownMessageProps) {
  return (
    <div
      className={cn(
        variant === "user" ? userMarkdownClass : assistantMarkdownClass,
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
