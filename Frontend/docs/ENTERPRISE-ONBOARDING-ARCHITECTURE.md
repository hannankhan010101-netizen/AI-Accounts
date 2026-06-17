# Enterprise Onboarding & Guided Tour Architecture

Production onboarding platform for Fast Accounts — universal tours, contextual learning, feature adoption, and AI-assisted guidance.

## Stack

| Layer | Technology |
|-------|------------|
| UI | React 18, Next.js 14 App Router, Tailwind, shadcn/ui |
| Motion | Framer Motion (`LazyMotion` + `domAnimation`), CSS tokens |
| Positioning | Floating UI (`@floating-ui/react`) |
| State | Tour engine (React Context + reducer), Zustand (UI + analytics mirror) |
| Data | TanStack Query (`/me/onboarding`, assistant API) |
| A11y | Focus trap, `aria-*`, `prefers-reduced-motion`, keyboard shortcuts |

## Folder structure

```
src/
  app/(app)/layout.tsx          # TourRoot
  components/
    tour/                       # Shell: FAB, overlay, menu, banners
    motion/                     # MotionProvider
    overlays/spotlight-overlay  # Animated spotlight mask
    tooltips/tooltip-card       # Floating UI + motion tooltip
    assistant/assistant-drawer  # AI panel shell
  features/onboarding/
    providers/onboarding-provider.tsx
    bridge/tour-zustand-bridge.tsx
    hooks/                      # useTourAnalytics, useFeatureDiscovery, useOnboardingKeyboard
  stores/onboarding/            # tour-ui, tour-progress, assistant
  lib/
    tour/                       # Engine: context, registry, resolver, analytics
    motion/                     # Tokens, variants, presets
  config/tours/                 # Tour definitions (onboard.*, workflow.*)
```

## Subsystems

### 1. Tour engine (`lib/tour/tour-context.tsx`)

- **State machine**: `idle` → `running` / `waiting_target` → `completed`
- **Cross-page**: `navigate` actions + route-aware registry
- **Targeting**: `data-tour` selectors, grid bridge, oversized-target → panel mode
- **Persistence**: local + server merge via `useTourSync`

### 2. Motion system (`lib/motion/`)

- Timing: 80 / 150 / 220 / 320 ms
- Presets: `fade`, `slideUp`, `scale`, `spotlight`, `tooltip`, `fab`, `drawer`
- `MotionProvider`: global `MotionConfig` + reduced motion

### 3. Spotlight (`components/overlays/spotlight-overlay.tsx`)

- Spring-interpolated hole position (GPU: `top/left/width/height` + box-shadow mask)
- Optional blur scrim layer

### 4. Tooltip engine (`components/tooltips/tooltip-card.tsx`)

- Floating UI: `flip`, `shift`, `offset`, `autoUpdate`
- Virtual reference from measured DOM rect
- Mobile: bottom-sheet layout
- Focus trap + screen reader announcements

### 5. Universal FAB (`components/tour/universal-tour-button.tsx`)

- Framer hover/tap + subtle pulse
- Optional drag mode (Zustand-persisted offset)
- Menu: tours, workflows, What’s New, assistant, shortcuts

### 6. AI assistant (`components/tour/tour-ai-panel.tsx`)

- Animated drawer
- Route suggestions API + feature discovery hints
- Question history in `assistant-store`

### 7. Zustand stores

| Store | Role |
|-------|------|
| `tour-ui-store` | FAB position, drag mode (persisted) |
| `tour-progress-store` | Engine mirror, session analytics, skip counts |
| `assistant-store` | Recent questions, pathname memory |

### 8. Analytics

- `trackTourEvent` → batch queue → `POST` events
- `useTourAnalytics()` — track, flush, drop-off, skip histogram

### 9. Keyboard

- `Alt+Shift+H` — learning menu
- `Alt+Shift+A` — assistant
- `Enter` / `→` — next step (when tour active)
- `Esc` — dismiss tour / close panels

## Integration

`TourRoot` wraps the app with `OnboardingProvider` (motion + tour engine + bridge). No route changes required.

## Extending

1. Add tour: `src/config/tours/*.ts` + register in `lib/tour/registry.ts`
2. Add anchors: `data-tour="your-id"` on shell elements
3. Optional step field: `animation: "tooltip"` | `route: "/path"`

## Performance

- Portal rendering for overlay/FAB only after mount
- `LazyMotion` reduces Framer bundle
- Transform-only animations; spotlight uses `will-change`
- Reduced motion disables springs and pulse loops
- **Code splitting:** only `onboard.core` in main bundle; other tours via `preloadTour()` / idle callback
- **Route prefetch:** `<link rel="prefetch">` on tour `navigate` steps
- **Menu hover:** `preloadTour(id)` on compass menu items

## UX v2 (premium polish)

| Surface | Component |
|---------|-----------|
| Step card | `components/onboarding/onboarding-step-card.tsx` |
| Progress rail | `onboarding-progress-rail.tsx` |
| Calm scrim | `onboarding-scrim.tsx` (28% tint + blur, click to pause) |
| Learning hub menu | `learning-hub-panel.tsx` |
| Help entry | `help-fab.tsx` (BookOpen + “Learn” on hover) |
| Resume | `continue-banner.tsx` |
| Success | `success-celebration.tsx` |
| Motion | `lib/motion/onboarding-variants.ts` |
| CSS | `globals.css` — `onboarding-glass`, `onboarding-mesh`, gradient border |

**Principles:** lower visual noise, text-link secondary actions, persona chip, timeline progress, softer spotlight ring pulse, non-blocking scrim.

## Public API

```ts
import {
  OnboardingProvider,
  TourEngine,
  useTourAnalytics,
  useFeatureDiscovery,
  useTourReplay,
  onboardingService,
} from "@/features/onboarding";
```

## Analytics events

`tour_started` · `tour_replayed` · `step_viewed` · `step_completed` · `step_skipped` · `tour_completed` · `tour_dismissed` · `feature_adoption` · `target_missing`
