# Olive Enterprise Design System

Premium muted olive/moss/sage theme for the AI-Accounts ERP frontend. Built on the existing **FADS** token layer (CSS variables + Tailwind semantic aliases).

## Source of truth

| Layer | Path |
|-------|------|
| Runtime tokens | [`src/app/globals.css`](../src/app/globals.css) |
| Tailwind mapping | [`tailwind.config.ts`](../tailwind.config.ts) |
| Programmatic palette | [`src/lib/design-tokens/palette.ts`](../src/lib/design-tokens/palette.ts) |
| Theme runtime | [`src/components/providers/theme-provider.tsx`](../src/components/providers/theme-provider.tsx) |

## Palette (light mode)

| Token | Role | Hex |
|-------|------|-----|
| `--bg-canvas` | App background | `#f4f6f0` |
| `--bg-surface` | Cards, panels | `#fafbf7` |
| `--bg-surface-elevated` | Modals, sticky headers | `#ffffff` |
| `--fg-default` | Primary text | `#1a1f16` |
| `--fg-muted` | Secondary text | `#5c6654` |
| `--brand-600` | Primary / moss | `#556b47` |
| `--brand-700` | Primary hover | `#465a3b` |
| `--accent-sage` | Accent | `#7d8f6e` |
| `--fg-on-brand` | Text on solid brand buttons/tabs | `#ffffff` (light), `#1a1f16` (dark) |

Solid brand controls: use `Button variant="primary"`, `.btn-brand`, or `brandSolidClasses` from `lib/design-tokens/brand-surfaces.ts`. Never pair `bg-brand` with `text-fg`.

Dark mode inverts surfaces to deep olive-charcoal (`#101410` canvas) and lifts brand to `#8fa67a`. Dark `--fg-muted` is `#a8b0a0` for ≥4.5:1 on `--bg-surface`. In dark theme, **do not** use `dark:text-brand-900` for labels on brand fills — step 900 is a light tint in the inverted scale; use `text-on-brand` or `brandSolidClasses` instead.

**Dark elevation (borderless panels)**

Prefer shadow + surface tier over visible outlines in dark mode:

| Utility | Use |
|---------|-----|
| `.surface-elevated` | Cards — no hard border in dark; soft glow shadow |
| `.card-bento` | Nested metric cells inside dashboard cards |
| `.divider-soft` | Section breaks instead of `border-t` |
| `.surface-glass` | Shell chrome (top bar, sidebar) — hairline bottom only |

Canvas uses a fixed mesh gradient (`--gradient-surface-mesh`) so panels float above the background.

| Helper | Use |
|--------|-----|
| `brandSolidClasses` / `.btn-brand` / `text-on-brand` | Primary buttons, active tabs, FABs |
| `brandSoftClasses` / `.surface-brand-soft` | Selected filters, summary cards, badges |
| `brandLinkClasses` | Text links and drill-down anchors |
| `.alert-warning-surface` | Draft/warning banners (replaces raw amber boxes) |
| `brandFocusedRowClasses` | Keyboard-focused grid rows |
| `brandRowHighlightClasses` | Deep-linked / highlighted rows |

## Semantic usage

**Do**

- Use Tailwind semantic classes: `bg-canvas`, `bg-surface`, `text-fg`, `text-fg-muted`, `border-border`
- For solid brand actions: `Button variant="primary"`, `text-on-brand`, or `PillTab` — not raw `bg-brand` + `text-fg`
- Use status tokens for feedback: `text-status-danger`, `bg-status-success/10`
- Use utilities: `surface-glass`, `surface-elevated`, `brand-glow`, `focus-ring`, `motion-safe-transition`
- Use chart tokens: `bg-chart-1` … `bg-chart-5` or `var(--chart-N)` in inline styles

**Don't**

- Hardcode hex colors in components (except print layouts)
- Use raw `text-red-*` — use `status-danger`
- Bypass tokens for one-off navy/slate palettes

## UI primitives

| Component | Path |
|-----------|------|
| Button | `src/components/ui/button.tsx` |
| Card | `src/components/ui/card.tsx` |
| KpiCard | `src/components/ui/kpi-card.tsx` |
| EmptyState | `src/components/ui/empty-state.tsx` |
| Skeleton | `src/components/ui/skeleton.tsx` |
| StickyActionBar | `src/components/ui/sticky-action-bar.tsx` |
| AnimatedNumber | `src/components/ui/animated-number.tsx` |
| Badge | `src/components/ui/badge.tsx` |
| InlineAlert | `src/components/ui/inline-alert.tsx` |
| Input / Select / Checkbox | `src/components/ui/` |

`StatusBadge` delegates to `Badge`. Grids use `EmptyState` when empty.

## Surface hierarchy

| Tier | Token / utility | Use |
|------|-----------------|-----|
| Canvas | `bg-canvas` | Page background |
| Surface | `bg-surface` | Cards, panels |
| Elevated | `surface-elevated`, `bg-surface-elevated` | Modals, sticky headers, KPI tiles |
| Accent wash | `bg-surface-accent` | Active nav, selected rows |
| Glass | `surface-glass` | Shell chrome, overlays only |

## Typography & spacing

| Token | Utility class |
|-------|---------------|
| `--text-display` | `.text-display` |
| `--text-section` | `.text-section` |
| `--text-caption` | `.text-caption` |
| `--space-section` | `gap-section`, `p-section` |

## Motion

App presets in `src/lib/motion/app-presets.ts`: `pageEnter`, `staggerList`, `metricEnter`, `modalEnter`, `barGrow`. Global `MotionProvider` in `src/app/providers.tsx`. Import barrel: `src/components/ui/index.ts`. All animations respect `useReducedMotion`.

## Elevation & glass

```css
.surface-glass     /* frosted panel — sidebar, top bar, drawers */
.surface-elevated  /* card elevation with shadow-md */
.brand-glow        /* soft olive halo — FAB, active nav */
.gradient-border-brand  /* premium card border */
.onboarding-mesh   /* auth / marketing background */
```

## Accessibility (WCAG 2.2 targets)

| Pair | Target | Notes |
|------|--------|-------|
| `--fg-default` on `--bg-canvas` | ≥ 4.5:1 | Primary body text |
| `--fg-muted` on `--bg-surface` | ≥ 4.5:1 | Labels, captions |
| `--brand-foreground` on `--brand-600` | ≥ 4.5:1 | Primary buttons |
| Focus ring | Visible 3:1 | `.focus-ring` uses `--focus-ring` |

**Reduced motion:** `--motion-*` durations zeroed under `prefers-reduced-motion: reduce`. Tour pulse animations fall back to static focus ring.

## Charts

Series colors `--chart-1` … `--chart-5` adapt in `.dark`. Use in CSS gradients:

```ts
const CHART_SERIES = ["var(--chart-1)", "var(--chart-2)", ...];
```

## Theme toggle

Stored in `localStorage` key `theme:mode` (`light` | `dark` | `system`). Applied as `light` or `dark` class on `<html>`.

See also: [UX-ARCHITECTURE.md](./UX-ARCHITECTURE.md)
