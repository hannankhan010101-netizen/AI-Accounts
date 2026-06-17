# Interactive onboarding & product demos

## Experience modes

| Mode | Behavior |
|------|----------|
| `guided` | Classic tooltips; user clicks Next |
| `interactive` | Auto sidebar/route navigation, demo cursor, sample data cards, AI assistant lines |
| `practice` | Same as interactive + click-to-advance on spotlight targets (toggle in Learn menu) |

## Architecture

- **Engine:** `src/lib/tour/tour-context.tsx` — `enterAction`, validation wait, auto-advance, practice override
- **Demo runtime:** `src/lib/tour/demo-engine.ts` — action execution, route polling
- **Shell:** `src/lib/tour/shell-actions.ts` + `sidebar.tsx` — expand nav, click `[data-tour="nav-…"]`
- **UI:** `InteractiveTourLayer`, `DemoCursor`, `FloatingTourAssistant`, `DemoPreviewPanel`
- **Tours:** `src/config/tours/demo-workflows.ts` (8 interactive demos, lazy-loaded)

## Adding a demo tour

1. Add steps with `enterAction: { type: "sidebarNavigate", href, groupLabel }` or `navigate`
2. Set `validation: { type: "routeMatch", pathname }` where needed
3. Add `data-tour` on sidebar links via `tourNavTargetId(href)` (automatic on nav items)
4. Register id in `lazy-registry.ts`
5. Optional: `demoPreviewId`, `cursor`, `autoAdvanceMs`, `content.assistantLine`

## Sample data

Preview payloads live in `src/lib/tour/demo-sample-data.ts` — display only, no API writes.

## Ghost form fill

- Recipes: `src/lib/tour/ghost-fill-recipes.ts`
- Hook: `useTourGhostFill({ form, context })` on react-hook-form pages
- Hook: `useTourGhostDomFill({ setters, context })` on useState forms (e.g. bank reconciliation start)
- Set `ghostFill: "sales-invoice-header"` (etc.) on demo steps
- `isDemoSandbox` disables Save and shows `DemoSandboxBanner`

### Wired form pages

| Page | Recipe ids |
|------|------------|
| Sales invoice new | `sales-invoice-header`, `sales-invoice-lines` |
| Sales receipt new | `sales-receipt-header` |
| Purchase bill new | `purchase-bill-header`, `purchase-bill-lines` |
| Supplier payment new | `supplier-payment-header` |
| Bank receipt / payment new | `bank-receipt-header`, `bank-payment-header` |
| Bank reconciliation | `bank-recon-start` (DOM) |

### Interactive demos (Learn menu)

`demo.sales-invoice`, `demo.bank-recon`, `demo.bank-receipt`, `demo.bank-payment`, `demo.purchase-bill`, `demo.supplier-payment`, `demo.customer-payment`, `demo.inventory-adjust`, `demo.dashboard`, `demo.reports`, `demo.assembly`

## Per-step AI coach

- `useStepAssistant` calls `POST …/onboarding/assistant` with step context
- `StepAssistantInsight` renders above the step card (rules or LLM fallback)
- Optional `assistantPrompt` on `TourStep` for custom queries
