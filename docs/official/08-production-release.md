# Production Release Security

> **Note:** GCP/Firebase path is optional enterprise tier. **Official V1 is Supabase + Vercel** — see [09-official-v1-release.md](./09-official-v1-release.md).

Official Google / Firebase controls for Gebo OS public ship.

## Owner Node vs Production

| Mode | `GEBO_RELEASE_MODE` | Stack |
|------|---------------------|--------|
| **Owner Node** (now) | `owner` | SQLite, Ollama, local memory, approval gate |
| **Production** | `production` | + Firebase Auth, Secret Manager, Model Armor, etc. |

Check readiness: `GET /system/production-readiness`

## Required controls (score toward 100%)

1. **Identity Platform / Firebase Auth** — frontend sign-in, backend JWT
2. **Sign In with Google / Passkeys** — `GOOGLE_CLIENT_ID`
3. **Cloud SQL** — `DATABASE_URL` (Postgres)
4. **reCAPTCHA Enterprise** — login/register forms
5. **Secret Manager** — no secrets in `.env` on GCP
6. **Model Armor** — `/chat` prompt/response screening

## Recommended

- Cloud Firestore (client sync)
- Cloud Armor (DDoS/WAF)
- Cloud Storage (uploads)
- DLP (PII scan on exports)
- Artifact Analysis (CI CVE scan)

## Enterprise

- Identity-Aware Proxy (IAP)
- Cloud Spanner

## Architecture

```
[Flutter / Next.js]
  Firebase Auth, Passkeys, reCAPTCHA
        │
[Cloud Run — FastAPI]
  JWT verify, Model Armor on /chat, Secret Manager
        │
[Cloud SQL + Firestore]     [GCS + DLP]
```

Local Owner Node keeps SQLite + Ollama; production adds the wrapper above without removing local-first option for private installs.

See also: [07-google-developer-ecosystem.md](./07-google-developer-ecosystem.md)
