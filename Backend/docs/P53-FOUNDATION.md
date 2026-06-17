# P53 — Tour discoverability & insights export

## Shipped

| ID | Capability |
|----|------------|
| P53.1 | **Stock module tour** | `onboard.stock` + `/inventory/products` anchors |
| P53.2 | **Reports module tour** | `onboard.reports` + `/reports` anchors |
| P53.3 | **Welcome banner** | Dashboard prompt before `onboard.core` completes |
| P53.4 | **Command palette** | `tour://` actions — welcome tour, assistant |
| P53.5 | **Settings menu links** | Learning insights, tenant/platform releases |
| P53.6 | **Insights CSV** | `GET /onboarding/insights/export` |

## Tests

`Backend/src/tests/test_p53_onboarding.py` (`SKIP_PRISMA=1`, `PYTHONPATH=src`)
