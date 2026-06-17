"use client";

import { useEffect, useRef, useState } from "react";

import { tourApi } from "@/lib/api/tour";
import type { TourStep } from "@/lib/tour/types";

const replyCache = new Map<string, { reply: string; engine: "rules" | "llm" }>();

function buildStepPrompt(
  step: TourStep,
  tourTitle: string | undefined,
  tourId: string,
  pathname: string,
): string {
  if (step.assistantPrompt) return step.assistantPrompt;
  const parts = [
    `You are a warm ERP onboarding coach. Reply in 1-2 short sentences.`,
    `Step: "${step.content.title}".`,
    step.content.why ? `Why: ${step.content.why}` : "",
    `How: ${step.content.how}`,
    `Tour: ${tourTitle ?? tourId}. Screen: ${pathname}.`,
    `Do not mention UI buttons. Be encouraging and concrete.`,
  ];
  return parts.filter(Boolean).join(" ");
}

type UseStepAssistantOptions = {
  step: TourStep;
  tourId: string;
  tourTitle?: string;
  pathname: string;
  enabled: boolean;
};

export function useStepAssistant({
  step,
  tourId,
  tourTitle,
  pathname,
  enabled,
}: UseStepAssistantOptions) {
  const [reply, setReply] = useState<string | null>(step.content.assistantLine ?? null);
  const [engine, setEngine] = useState<"rules" | "llm">("rules");
  const [loading, setLoading] = useState(false);
  const fetchedRef = useRef<string | null>(null);

  useEffect(() => {
    if (!enabled) {
      setReply(step.content.assistantLine ?? null);
      return;
    }

    const cacheKey = `${tourId}:${step.id}:${pathname}`;
    const cached = replyCache.get(cacheKey);
    if (cached) {
      setReply(cached.reply);
      setEngine(cached.engine);
      return;
    }

    if (fetchedRef.current === cacheKey) return;
    fetchedRef.current = cacheKey;

    let cancelled = false;
    setLoading(true);
    const message = buildStepPrompt(step, tourTitle, tourId, pathname);

    void tourApi
      .postAssistant({ message, pathname })
      .then((res) => {
        if (cancelled) return;
        const text =
          res.result.reply?.trim() ||
          step.content.assistantLine ||
          step.content.how;
        replyCache.set(cacheKey, { reply: text, engine: res.result.engine });
        setReply(text);
        setEngine(res.result.engine);
      })
      .catch(() => {
        if (!cancelled) {
          setReply(step.content.assistantLine ?? step.content.how);
          setEngine("rules");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [
    enabled,
    step.id,
    step.content.assistantLine,
    step.content.how,
    step.assistantPrompt,
    tourId,
    tourTitle,
    pathname,
  ]);

  return { reply, engine, loading };
}
