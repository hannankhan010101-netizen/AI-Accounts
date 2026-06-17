# Universal Tour System — Architecture

Living spec for guided onboarding in AI-Accounts / Fast Accounts frontend.

## Status (P0–P11 shipped)

| Piece | Location |
|-------|----------|
| Tour provider + FSM | `src/lib/tour/tour-context.tsx` |
| Definitions | `src/config/tours/*.ts` |
| Registry | `src/lib/tour/registry.ts` |
| Progress (local + server) | `progress-store.ts`, `api/tour.ts`, P48 |
| Module tours | `onboard.sell`, `.money`, `.buy`, `.admin` |
| Target resolver | `src/lib/tour/target-resolver.ts` |
| UI | `src/components/tour/*` |
| Shell mount | `src/app/(app)/layout.tsx` → `TourRoot` |
| Anchors | `data-tour` on sidebar, top bar, `#main-content` |

## Principles

- **KISS:** one engine, declarative steps, opt-in `data-tour` anchors
- **Non-blocking:** Escape dismisses; never prevents save/submit
- **Motion:** `--motion-fast/base`, `prefers-reduced-motion`, `--z-tour: 70`
- **Interruptible:** session checkpoint in `sessionStorage` (30 min)

## Tour types

`onboard` · `module` · `spotlight` · `workflow` · `task` · `release` · `ai`

## Adding a tour

1. Create `src/config/tours/my-tour.ts` exporting `TourDefinition`
2. Register in `src/lib/tour/registry.ts`
3. Add `data-tour="…"` to UI targets
4. Optional: map route in `src/lib/tour/route-tours.ts`

## Universal Tour Button

- Fixed bottom-right; menu: Continue, Tour this page, Welcome tour, Search, Shortcuts
- Shortcut: **Alt+Shift+H**
- States: idle, expanded menu, active tour (step badge), attention pulse (first visit)

## Progress keys

- `localStorage`: `fa-tour:v1:{userKey}:{companyId}`
- `sessionStorage`: `fa-tour:active`
- `userKey` from JWT `sub` / `userId` (`lib/auth/jwt.ts`)

## Server API (P48)

- `GET /me/onboarding` — progress + `roleName` + `permissions`
- `PUT /me/onboarding` — save progress (preserves `eventLog`)
- `POST /me/onboarding/events` — batched analytics (204)

## P2 (shipped)

- `EnterpriseGrid` `tourTarget` + row anchors `{id}-row-{n}`
- `TourResumeBanner` — session restore within 30 min
- `FeatureDiscoveryPanel` on dashboard What's New tab
- `lib/tour/feature-hints.ts` rule engine

## P3 (shipped)

- Server `releases[]` on GET `/me/onboarding`
- Release tours + What's New unread badges
- `GET /onboarding/insights` + `/settings/learning-insights`

## P4 (shipped)

- `GET /me/onboarding/suggestions` — contextual ranked actions
- `TourAiPanel` — learning assistant drawer
- `hint-ranker.ts` — smarter hint ordering on dashboard
- Tenant release CMS — `/settings/onboarding-releases`

## P5 (shipped)

- Optional LLM suggestions (`engine`: `rules` | `llm`) + `POST /me/onboarding/assistant` chat
- Platform release CMS — `platform_onboarding_releases`, `/settings/platform-releases`
- Merge: platform DB → catalog → tenant override

See `Backend/docs/P52-FOUNDATION.md` for env vars and migration.

## P6 (shipped)

- Module tours: `onboard.stock`, `onboard.reports` + page anchors
- Dashboard **welcome banner** for new users (`TourWelcomeBanner`)
- Command palette: welcome tour, learning assistant, insights link
- Settings mega-menu: learning / release admin links
- `GET /onboarding/insights/export` — CSV download on learning insights page

See `Backend/docs/P53-FOUNDATION.md`.

## P7 (shipped)

- **Workflow tours:** `workflow.sales-invoice`, `workflow.supplier-bill`
- Cross-route **navigate** step action (list → new form)
- `DocumentWorkspace` / `GstLineGrid` tour anchors

See `Backend/docs/P54-FOUNDATION.md`.

## P8 (shipped)

- **Workflow tours:** `workflow.journal`, `workflow.bank-receipt`
- **Workflows** section in compass menu
- **Email digest:** `POST /me/onboarding/digest-email`, `preferences.emailDigestEnabled`

See `Backend/docs/P55-FOUNDATION.md`.

## P9 (shipped)

- **`workflow.bank-payment`** — payments out workflow tour
- **Maturity badge** on dashboard (`TourMaturityBadge`)
- **Auto What's New digest** — once per day when opted in (`digest-scheduler.ts`)

See `Backend/docs/P56-FOUNDATION.md`.

## P10 (shipped)

- **`workflow.sales-receipt`** — customer receipt list → new form (FIFO / manual allocation)
- **`TourCompletionToast`** — brief confirmation when a tour finishes
- **`/settings/learning`** — personal progress, digest toggle, replay tours
- **Server digest on sync** — `GET /me/onboarding?attemptDigest=true` tries once-per-day email when due
- Command palette + settings menu: Learning preferences; workflow: customer receipt

See `Backend/docs/P57-FOUNDATION.md`.

## P11 (shipped)

- **`workflow.supplier-payment`** — bill payments list → new form (FIFO / manual bill allocation)
- Buy-side feature hints: supplier bill workflow, then payment workflow
- Command palette: **Workflow: supplier bill payment**
- Compass menu shows up to 6 workflow tours

See `Backend/docs/P58-FOUNDATION.md`.

## P12 — Enterprise motion layer (shipped)

| Piece | Location |
|-------|----------|
| Onboarding provider | `src/features/onboarding/providers/onboarding-provider.tsx` |
| Motion system | `src/lib/motion/*`, `src/components/motion/motion-provider.tsx` |
| Floating tooltip | `src/components/tooltips/tooltip-card.tsx` |
| Animated spotlight | `src/components/overlays/spotlight-overlay.tsx` |
| AI drawer | `src/components/assistant/assistant-drawer.tsx` |
| Zustand stores | `src/stores/onboarding/*` |
| Lazy tour chunks | `src/lib/tour/lazy-registry.ts`, `preloadTour()` |
| Route prefetch | `src/lib/tour/route-prefetch.ts` |
| Service facade | `src/services/onboarding-service.ts` |
| Error boundary | `src/features/onboarding/components/onboarding-error-boundary.tsx` |
| Full spec | `docs/ENTERPRISE-ONBOARDING-ARCHITECTURE.md` |

**Shortcuts:** `Alt+Shift+H` menu · `Alt+Shift+A` assistant · `Enter` next step · `Esc` dismiss

See prior product architecture brief in team docs / chat for full UX, analytics, and persona matrices.
