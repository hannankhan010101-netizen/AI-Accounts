# P49 — Tour P2: grid targets, resume banner, feature hints (frontend)

Builds on [P48-FOUNDATION.md](./P48-FOUNDATION.md).

## Shipped (frontend)

| ID | Capability | Code |
|----|------------|------|
| P49.1 | **Virtualized grid tours** | `EnterpriseGrid` `tourTarget` + `{id}-row-{n}` anchors |
| P49.2 | **Grid scroll bridge** | `lib/tour/grid-tour-bridge.ts` |
| P49.3 | **Resume after refresh** | `TourResumeBanner` + session checkpoint |
| P49.4 | **Feature discovery** | Dashboard **What's New** → `FeatureDiscoveryPanel` |
| P49.5 | **Hint dismiss sync** | `dismissedHints` via existing PUT onboarding |

## Grid tour usage

```tsx
<EnterpriseGrid tourTarget="sales-invoices-grid" ... />
```

Tour step target:

```ts
{ kind: "grid", id: "sales-invoices-grid", rowIndex: 0 }
```

## Next (P50)

- Release tours from server feed
- AI hint ranking
- Admin onboarding analytics dashboard
