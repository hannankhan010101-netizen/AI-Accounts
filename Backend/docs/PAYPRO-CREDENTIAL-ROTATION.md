# PayPro credential rotation runbook

Use when rotating merchant API keys or webhook signing secrets in production.

## Prerequisites

- PayPro merchant portal access
- AWS Secrets Manager / Vault / `SECRETS_VAULT_FILE` path used by the API
- Maintenance window (webhooks may fail briefly if secret mismatch)

## Rotation steps

1. **Generate new credentials** in PayPro (API key + webhook secret). Keep the old secret active until step 5 completes.
2. **Update secret store** with JSON keys (existing env names):
   ```json
   {
     "PAYPRO_API_KEY": "new-api-key",
     "PAYPRO_WEBHOOK_SECRET": "new-whsec",
     "PAYPRO_MERCHANT_ID": "unchanged-or-new"
   }
   ```
3. **Deploy or restart** API pods so `bootstrap_secrets()` reloads values (env vars already set are not overwritten — unset old keys first if needed).
4. **Configure PayPro webhook URL** to remain `POST /api/v1/companies/{companyId}/paypro/webhook` with the new signing secret.
5. **Smoke test**
   - Initiate a small payment from Settings → Online payments
   - Confirm webhook settles → sales receipt + allocation
   - Check security audit log for `security.paypro.webhook.settled`
6. **Revoke old API key** in PayPro after 24h with zero webhook 401s.

## Rollback

Restore previous JSON in the secret store and restart. Re-enable old PayPro webhook secret until traffic stabilizes.

## Kuickpay

Mirror the same process with `KUICKPAY_API_KEY`, `KUICKPAY_WEBHOOK_SECRET`, and `KUICKPAY_WEBHOOK_ALLOWED_IPS`.

## Monitoring

- Webhook 401 → signature mismatch (secret drift)
- Webhook 403 → IP allowlist or rate limit
- FBR unrelated; use `GET /fbr/submissions/errors` separately
