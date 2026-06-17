# Frontend UX Architecture — AI-Accounts

Living reference for shell, motion, performance, and reliability. Implementation status noted inline.

## Stack

- Next.js 14 App Router, TypeScript, Tailwind (FADS tokens)
- TanStack Query / Table / Virtual
- React Hook Form + Zod
- Radix (dialogs/menus)

## Shell (`src/app/(app)/layout.tsx`)

| Piece | File | Status |
|-------|------|--------|
| Sidebar expand/compact | `components/app/sidebar.tsx` | Done |
| Mobile drawer | TopBar `Menu` + Sidebar overlay | Done |
| Command palette | `Ctrl+K` | Done |
| Offline banner | `components/app/offline-banner.tsx` | Done |
| Route fade | `components/ui/motion-fade.tsx` | Done |
| Theme (light/dark/system) | `components/providers/theme-provider.tsx` | Done |
| Error boundary | `app/(app)/error.tsx` | Done |

Persistence keys: `layout:sidebar-mode`, `layout:nav-open-groups`, `theme:mode`.

## Branding

Olive enterprise design system — see [DESIGN-SYSTEM.md](./DESIGN-SYSTEM.md) for palette, tokens, and usage.

| Asset | Path | Use |
|-------|------|-----|
| Symbol | `/brand/symbol.png` | Sidebar, auth, mobile top bar (`BrandMark`) |
| Favicon | `/brand/favicon.png` | Tab icon (64×64, symbol-derived) |
| Full lockup | `/brand/logo.png` | Print layouts only |

Components: `components/brand/brand-mark.tsx`, `brand-logo.tsx` (`sidebar` \| `sidebarCompact` \| `auth`).

## Motion tokens (`src/app/globals.css`)

| Token | Value | Use |
|-------|-------|-----|
| `--motion-fast` | 150ms | Hover, focus |
| `--motion-base` | 200ms | Panels |
| `--motion-slow` | 280ms | Max duration |
| `prefers-reduced-motion` | 0ms | Accessibility |

Rules: animate `transform` and `opacity` only; never block navigation on animation end.

## React Query

| Class | Helper | staleTime | gcTime |
|-------|--------|-----------|--------|
| Reference (COA, menu, permissions) | `useTenantReferenceQuery` / `referenceQueryOptions()` | 5 min | 30 min |
| Lists | `useTenantListQuery` / `listQueryOptions()` | 30s | 10 min |
| Detail | `useTenantDetailQuery` / `detailQueryOptions()` | 0 (refetch on mount) | 5 min |
| Reports (P&amp;L, TB, GL) | `useTenantReportQuery` / `reportQueryOptions()` | 2 min | 15 min |

All tenant API queries use keys prefixed `["tenant", companyId, …]` via `useTenantQuery` helpers in `src/lib/api/tenant-query.ts`.

Global defaults: `src/app/providers.tsx`, constants: `src/lib/query/defaults.ts`.

### Shell warmup

After company bootstrap (and on company switch), `warmupShellCache()` prefetches in parallel:

- `content-menu`, `my-permissions`, `coa-tree`, `report-definitions` catalog, `dashboard-settings`

Implementation: `src/lib/query/shell-warmup.ts`, triggered from `src/lib/auth/company-context.tsx`.

### HTTP / browser disk cache

Reference GETs (`/coa/tree`, `/reports/definitions`, `/content-settings/menu`) use `apiFetchCached()` with `If-None-Match` / ETag 304 support. Backend sends `Cache-Control: private, max-age=300`.

### sessionStorage persist

Reference and report tiers are persisted to `sessionStorage` under key `fa-rq-v1` via `@tanstack/react-query-persist-client` (tab-scoped; cleared on close). Detail and list tiers are excluded.

### Manual verification (Step 5)

| Check | How |
|-------|-----|
| Tenant isolation | Switch company → old company data not shown without refetch |
| Memory hit | Navigate away/back within staleTime → no network (DevTools Network tab) |
| ETag 304 | Second COA tree load sends `If-None-Match`, receives 304 |
| Report tier | Re-open P&amp;L within 2 min → served from RAM |
| Warmup | Fresh login → menu + permissions available before first navigation click |

## Route loading

- `app/(app)/reports/loading.tsx` — report skeleton
- `app/(app)/settings/loading.tsx` — settings skeleton
- Components: `workspace-loading.tsx`, `document-workspace-loading.tsx`, `detail-page-loading.tsx`
- Document **detail** (`[id]`): route `loading.tsx` + in-page `DetailPageLoading` while refetching
- **Edit** routes: `…/[id]/edit/loading.tsx` uses `DocumentWorkspaceLoading`
- Settings forms, dashboard, P&amp;L, balance sheet: in-page `WorkspaceLoading` (replaces plain “Loading…” text)
- Bank reconciliation detail: `WorkspaceLoading` + `[id]/loading.tsx`

## Form drafts

- Storage: `sessionStorage` via `src/lib/draft/form-draft.ts`
- Hook: `src/lib/hooks/use-form-draft.ts`
- UI: `components/ui/draft-recovery-banner.tsx`
- Example: `settings/business-information/page.tsx`

Pattern for new forms: pass `companyId`, `scope`, `form`, `serverValues`; call `clearDraftOnSave()` on mutation success.

## Data grid (`EnterpriseGrid`)

- Virtualize when rows > 80
- Keyboard: focus grid, ↑/↓, Home/End, Enter to open row
- `aria-sort` on sortable headers

## Paginated lists

- `paginatedListQueryOptions()` — `placeholderData: keepPreviousData`
- `EnterpriseGrid` `fetching` prop — progress bar + dim while page changes
- Example: `settings/users/page.tsx`

## Route loading (documents)

- `sales/loading.tsx`, `purchases/loading.tsx`, `bank/loading.tsx`, `inventory/loading.tsx`
- Skeleton: `components/ui/document-workspace-loading.tsx`

## Keyboard shortcuts

- Config: `config/keyboard-shortcuts.ts`
- Dialog: `components/app/keyboard-shortcuts-dialog.tsx`
- Press `?` (outside inputs) or TopBar **?** button

## Form drafts (settings)

| Page | Scope key |
|------|-----------|
| Business information | `business-information` |
| Smart settings | `smart-settings` |
| Taxes & year end | `taxes-year-end` |

## URL-synced list state

- Params: `q` (search), `page`, `status` (server lists only)
- Helpers: `lib/navigation/list-search-params.ts`
- Client lists: `useClientList({ syncUrl: true })` — invoices, bills, import jobs, audit log find
- Server lists: `useUrlServerList()` — users page

## Route focus

- `PageHeader` — `#page-title` receives focus on `pathname` change (screen reader + keyboard)

## Document form drafts

- Low-level: `useDocumentDraft` — `localStorage` key `fa-draft:{scope}`
- Bundled: `useDocumentWorkspaceDraft` — autosave, `DocumentDraftBanner`, `useDocumentFormGuard`
- Helpers: `hasMeaningfulLineGridDraft`, `hasMeaningfulMasterDraft` in `lib/hooks/document-draft-helpers.ts`
- **DocumentWorkspace** new routes: invoices, bills, bank vouchers, receipts/payments (with allocations), journals, GRN, delivery notes, stock transfer/adjustment, `LineGridForm` (quotations, orders, credits)
- **PageHeader** new routes: customer, supplier, product, PDC received/issued
- Loading skeletons: `DocumentWorkspaceLoading` on invoice/bill/receipt/payment/journal/bank `new` segments

## URL-synced lists (complete)

All `(app)` list pages and report grids use `useClientList({ syncUrl: true })` except embedded sub-grids (`coa-nominal-grid`, `bank-reconciliation-workspace`, `dynamic-report-grid`) to avoid clobbering parent URL state.

## Document detail pages

- Primary fetch: `detailQueryOptions()` (`staleTime: 0`, refetch on mount)
- Loading: `DetailPageLoading` (skeleton) — invoices, bills, bank vouchers, journals, GRN, delivery notes, stock transfer/adjustment
- **Draft edit:** `PATCH /sales-invoices/{id}`, `PATCH /supplier-bills/{id}` — UI at `…/[id]/edit` with `useDocumentWorkspaceDraft` scoped per document id
- **Draft approve:** invoice and bill detail pages — **Approve & post to GL** when `status === "draft"`

## Dashboard (§10.9 Business Overview)

| Endpoint | Client | Widgets |
|----------|--------|---------|
| `GET /dashboard/overview` | `dashboardApi.overview()` | Bank balances, 12‑month cash flow, FY P&amp;L + expense donut, sales by month, inventory stock counts, AR/AP top 10 |
| `GET /dashboard/summary` | `dashboardApi.summary()` | Legacy count cards (optional) |
| `GET /reports/ar-aging` / `ap-aging` | `reportsApi` | AR/AP summary cards + bucket tables |
| `GET /reports/bank-account-balances` | `reportsApi.bankAccountBalances()` | Standalone bank list |
| `GET /reports/bank-cash-flow-monthly` | `reportsApi.bankCashFlowMonthly()` | Standalone cash flow series |
| `GET /reports/profit-and-loss` | `reportsApi.profitAndLoss()` | Full P&amp;L report page |

Home: `src/app/(app)/dashboard/page.tsx` → `BusinessOverviewDashboard` with tabs **What's New** (placeholder) and **Business Overview** (live). Charts are CSS/SVG (no chart library). Symbol-only header via `BrandMark`.

**What's New** tab: live feature-discovery hints (`FeatureDiscoveryPanel`). **AR watchlist** still placeholder.

## Posted document void (§5.4 / §6.3)

| Document | Void API | Detail UI |
|----------|----------|-----------|
| Sales invoice | `POST /sales-invoices/{id}/void` | Void + **Create replacement** → `/sales/invoices/new` |
| Supplier bill | `POST /supplier-bills/{id}/void` | Void + **Create replacement** → `/purchases/bills/new` |

Also on `reportsApi`: credits, GRN, delivery notes, goods-issue partial voids (existing P16–P24).

Re-issue is manual copy via new document form (no server-side duplicate endpoint yet).

## Universal tours (P0–P4)

| Piece | File | Status |
|-------|------|--------|
| Provider + overlay | `components/tour/tour-root.tsx` | Done |
| Module tours | `config/tours/onboard.*.ts` | Done |
| Floating help button | `components/tour/universal-tour-button.tsx` | Done |
| Progress sync | `lib/tour/use-tour-sync.ts`, P48 API | Done |
| Grid targets | `EnterpriseGrid` `tourTarget` | Done |
| Resume banner | `components/tour/tour-resume-banner.tsx` | Done |
| Dashboard hints + releases | `feature-discovery-panel.tsx` | Done |
| Admin insights | `/settings/learning-insights` | Done |
| Release CMS | `/settings/onboarding-releases` | Done |
| AI assistant | `TourAiPanel` + `/me/onboarding/suggestions` | Done |
| Spec | `docs/UNIVERSAL-TOUR-ARCHITECTURE.md` | Done |

Anchors: `data-tour="sidebar-nav"`, `company-switcher`, `command-palette`, `main-content`, `tour-button`, `{gridId}-row-{n}`.

Shortcuts: **Alt+Shift+H** learning menu; **Escape** dismisses active tour.

## Roadmap (next)

- [ ] AR/AP watchlist rules (overdue thresholds, credit limit)
- [ ] Server-side duplicate invoice/bill from voided source
- [ ] Dashboard Management widget personalization (`/dashboard/layout`)

## Conventions

See `Frontend/.cursorrules_frontend` for code structure and catalog parity rules.
