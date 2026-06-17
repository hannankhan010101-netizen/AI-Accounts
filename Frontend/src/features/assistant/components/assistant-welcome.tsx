"use client";

import { m } from "framer-motion";

import { AssistantAvatar } from "@/features/assistant/components/assistant-avatar";
import { t } from "@/features/assistant/i18n";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

type AssistantWelcomeProps = {
  screenTitle: string;
};

export function AssistantWelcome({ screenTitle }: AssistantWelcomeProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      initial={reduced ? false : { opacity: 0, y: 6 }}
      animate={reduced ? undefined : { opacity: 1, y: 0 }}
      transition={{ duration: 0.15 }}
      className="flex flex-col items-center px-4 py-6 text-center"
    >
      <AssistantAvatar role="assistant" className="mb-3 h-10 w-10 [&_svg]:h-5 [&_svg]:w-5" />
      <h3 className="text-sm font-semibold text-fg">{t("en", "welcomeTitle")}</h3>
      <p className="mt-1 max-w-xs text-xs text-fg-muted">
        {t("en", "welcomeBody").replace("{screen}", screenTitle)}
      </p>
    </m.div>
  );
}
