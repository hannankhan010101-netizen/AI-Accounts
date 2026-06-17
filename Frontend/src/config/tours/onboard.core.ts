import type { TourDefinition } from "@/lib/tour/types";

/** First-login orientation — 5 steps, ~3 min. */
export const onboardCoreTour: TourDefinition = {
  id: "onboard.core",
  version: 1,
  type: "onboard",
  title: "Welcome to Fast Accounts",
  personas: ["general", "admin", "accountant", "sales", "cfo", "viewer"],
  experience: "interactive",
  metadata: { estimatedMinutes: 3, priority: 100 },
  steps: [
    {
      id: "workspace",
      target: { kind: "panel" },
      presentation: "panel",
      content: {
        title: "Your workspace",
        why: "Every task happens in this main area — lists, forms, and reports.",
        how: "Use the sidebar to switch modules. Your work always appears here.",
        assistantLine: "Welcome — I'll be your guide while you explore Fast Accounts.",
      },
      placement: "bottom",
      skippable: true,
    },
    {
      id: "navigation",
      target: { kind: "tour", id: "sidebar-nav" },
      presentation: "spotlight",
      content: {
        title: "Module navigation",
        why: "Sell, Buy, Money, and Stock map to how finance teams think about work.",
        how: "On desktop, use the sidebar. On mobile, open the menu (☰) to see the same modules.",
        bestPractice: "Collapse the sidebar on smaller screens for more space.",
        assistantLine: "I'll expand the menu so you can see every module.",
      },
      placement: "right",
      skippable: true,
    },
    {
      id: "company",
      target: { kind: "tour", id: "company-switcher" },
      presentation: "spotlight",
      content: {
        title: "Company context",
        why: "Books, permissions, and reports are always scoped to one company.",
        how: "Switch companies here if you manage more than one entity.",
        assistantLine: "Every number you see belongs to the active company — switch anytime.",
      },
      cursor: { enabled: true },
      placement: "auto",
      skippable: true,
    },
    {
      id: "search",
      target: { kind: "tour", id: "command-palette" },
      presentation: "spotlight",
      content: {
        title: "Jump anywhere fast",
        why: "Power users save time by searching instead of clicking through menus.",
        how: "Press Ctrl+K (Cmd+K on Mac) to open the command palette.",
      },
      placement: "auto",
      action: { type: "none" },
      skippable: true,
    },
    {
      id: "help",
      target: { kind: "tour", id: "tour-button" },
      presentation: "spotlight",
      content: {
        title: "Learning hub",
        why: "Guided tours adapt to your role and show only what you can access.",
        how: "Open this button anytime for tours, shortcuts, and what's new.",
      },
      placement: "top",
      action: { type: "none" },
      skippable: false,
    },
  ],
};
