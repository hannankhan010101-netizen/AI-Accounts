/** UI strings for assistant (multilingual-ready). */

export const assistantI18n = {
  en: {
    title: "AI-Assistant",
    subtitle: "Help for",
    onboardingTitle: "Guide",
    onboardingSubtitle: "Tours & tips",
    placeholder: "Ask about this screen…",
    send: "Send",
    close: "Close",
    thinking: "…",
    workingOnTool: "{tool}…",
    stop: "Stop",
    composerHint: "Enter · Shift+Enter new line",
    welcomeTitle: "Ask me anything",
    welcomeBody: "Help with {screen} — or tap a suggestion.",
    welcomeHint: "",
    statusOnline: "Ready",
    statusThinking: "…",
    newChat: "New chat",
    retry: "Retry",
    engineGroq: "AI",
    engineRules: "Rules",
    errorGeneric: "Something went wrong.",
    openCopilot: "Open AI-Assistant",
    quickActions: "Suggestions",
  },
} as const;

export type AssistantLocale = keyof typeof assistantI18n;

export function t(locale: AssistantLocale, key: keyof (typeof assistantI18n)["en"]) {
  return assistantI18n[locale]?.[key] ?? assistantI18n.en[key];
}
