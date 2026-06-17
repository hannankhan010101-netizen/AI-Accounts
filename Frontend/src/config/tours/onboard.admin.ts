import type { TourDefinition } from "@/lib/tour/types";

export const onboardAdminTour: TourDefinition = {
  id: "onboard.admin",
  version: 1,
  type: "onboard",
  title: "Team & access",
  module: "financial",
  personas: ["admin"],
  prerequisites: {
    completedTours: ["onboard.core"],
    permissions: ["settings.users.invite"],
  },
  metadata: { estimatedMinutes: 3, priority: 65 },
  steps: [
    {
      id: "users",
      target: { kind: "tour", id: "settings-users-header" },
      presentation: "spotlight",
      content: {
        title: "Users",
        why: "Each teammate needs a login, role, and module access.",
        how: "Invite users and assign roles that match their job function.",
      },
      placement: "bottom",
    },
    {
      id: "roles",
      target: { kind: "panel" },
      presentation: "panel",
      content: {
        title: "Roles & permissions",
        how: "Open **Settings → Roles** to define what each role can see and do.",
        bestPractice: "Start with a small set of roles and expand only when needed.",
      },
    },
  ],
};
