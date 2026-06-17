"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bot, Send, Sparkles, X } from "lucide-react";

import { AssistantDrawer } from "@/components/assistant/assistant-drawer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { tourApi } from "@/lib/api/tour";
import { useFeatureDiscovery } from "@/features/onboarding/hooks/use-feature-discovery";
import { useTour } from "@/lib/tour/tour-context";
import { useAssistantStore } from "@/stores/onboarding/assistant-store";

export function TourAiPanel() {
  const router = useRouter();
  const pathname = usePathname();
  const { aiPanelOpen, setAiPanelOpen, startTour } = useTour();
  const { hints } = useFeatureDiscovery(3);
  const pushQuestion = useAssistantStore((s) => s.pushQuestion);
  const setLastPathname = useAssistantStore((s) => s.setLastPathname);
  const [question, setQuestion] = useState("");

  const { data, isLoading, refetch } = useTenantListQuery(
    ["tour-suggestions", pathname],
    () => tourApi.getSuggestions(pathname),
    { enabled: aiPanelOpen, staleTime: 30_000 },
  );

  const chatMut = useMutation({
    mutationFn: () =>
      tourApi.postAssistant({ message: question.trim(), pathname }),
    onSuccess: () => {
      pushQuestion(question);
      setQuestion("");
    },
  });

  useEffect(() => {
    if (aiPanelOpen) {
      setLastPathname(pathname);
      void refetch();
    }
  }, [aiPanelOpen, pathname, refetch, setLastPathname]);

  const suggestions = data?.result.suggestions ?? [];
  const engine = data?.result.engine ?? "rules";

  return (
    <AssistantDrawer
      open={aiPanelOpen}
      onClose={() => setAiPanelOpen(false)}
      title={
        <div>
          <h2 className="flex items-center gap-2 text-base font-semibold tracking-tight text-fg">
            <Bot className="h-5 w-5 text-brand-600 dark:text-brand-100" aria-hidden />
            Learning assistant
          </h2>
          <p className="mt-1 text-xs text-fg-muted">
            Context-aware suggestions for this screen
          </p>
        </div>
      }
      headerAction={
        <button
          type="button"
          onClick={() => setAiPanelOpen(false)}
          className="rounded-md p-1.5 text-fg-muted hover:bg-canvas focus-ring"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
      }
    >
      <div className="p-4">
        <p className="text-sm text-fg-muted">
          What should I do next on{" "}
          <span className="font-mono text-xs text-fg">{pathname}</span>?
          <span className="ml-2 rounded bg-canvas px-1.5 py-0.5 text-xs font-medium text-fg">
            {engine === "llm" ? "AI" : "Rules"}
          </span>
        </p>

        <form
          className="mt-4 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!question.trim() || chatMut.isPending) return;
            chatMut.mutate();
          }}
        >
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask how to do something…"
            aria-label="Question for learning assistant"
          />
          <Button
            type="submit"
            size="sm"
            variant="primary"
            disabled={!question.trim() || chatMut.isPending}
            aria-label="Send question"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>

        {chatMut.data?.result.reply && (
          <p className="mt-3 rounded-md border border-border bg-canvas/50 p-3 text-sm text-fg">
            {chatMut.data.result.reply}
          </p>
        )}
        {chatMut.error instanceof Error && (
          <p className="mt-2 text-sm text-status-danger">{chatMut.error.message}</p>
        )}

        {hints.length > 0 && (
          <section className="mt-6" aria-labelledby="feature-discovery-heading">
            <h3
              id="feature-discovery-heading"
              className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-fg-muted"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Discover features
            </h3>
            <ul className="mt-2 space-y-2">
              {hints.map((h) => (
                <li
                  key={h.id}
                  className="rounded-md border border-border bg-canvas/40 px-3 py-2 text-sm"
                >
                  <p className="font-medium text-fg">{h.title}</p>
                  <p className="text-xs text-fg-muted">{h.body}</p>
                </li>
              ))}
            </ul>
          </section>
        )}

        {isLoading && <p className="mt-4 text-sm text-fg-muted">Thinking…</p>}

        {!isLoading && suggestions.length === 0 && (
          <p className="mt-4 rounded-md border border-dashed border-border p-4 text-sm text-fg-muted">
            No suggestions right now. Try the compass menu for tours.
          </p>
        )}

        <ul className="mt-4 space-y-3">
          {suggestions.map((s) => (
            <li key={s.id} className="rounded-md border border-border bg-canvas/50 p-3">
              <p className="font-medium text-fg">{s.title}</p>
              <p className="mt-1 text-sm text-fg-muted">{s.reason}</p>
              <div className="mt-3 flex gap-2">
                {s.tourId && (
                  <Button
                    type="button"
                    size="sm"
                    variant="primary"
                    onClick={() => {
                      if (s.href) router.push(s.href);
                      startTour(s.tourId!);
                      setAiPanelOpen(false);
                    }}
                  >
                    Start tour
                  </Button>
                )}
                {!s.tourId && s.href && (
                  <LinkButton href={s.href} onClose={() => setAiPanelOpen(false)} />
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </AssistantDrawer>
  );
}

function LinkButton({ href, onClose }: { href: string; onClose: () => void }) {
  const router = useRouter();
  return (
    <Button
      type="button"
      size="sm"
      variant="outline"
      onClick={() => {
        router.push(href);
        onClose();
      }}
    >
      Open page
    </Button>
  );
}
