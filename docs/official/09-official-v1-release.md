# Official Gebo V1 Release Architecture

Bb's official production stack for Gebo OS public V1. **Supabase + Vercel** is the default path; GCP/Firebase remains an optional enterprise tier (see [08-production-release.md](./08-production-release.md)).

## Owner Node vs Production

| Mode | `GEBO_RELEASE_MODE` | Stack |
|------|---------------------|--------|
| **Owner Node** (now) | `owner` | SQLite, Ollama, local memory, approval gate |
| **Official V1** | `production` | Supabase Postgres + pgvector, Supabase Auth, Vercel frontend |

Owner Node keeps working unchanged. Production adds the wrapper below without removing local-first option for private installs.

Check readiness:

- `GET /system/v1-readiness` — official V1 stack score
- `GET /system/modules` — eight native backend modules
- `GET /system/production-readiness` — optional GCP/Firebase path

## Full V1 Stack

| Layer | Service | Role | Tier |
|-------|---------|------|------|
| Frontend | Next.js App Router on Vercel | Light UX shell — auth, upload, dashboard | required |
| Backend | FastAPI (+ future Next.js API routes) | Core API, module orchestration | required |
| Database | Supabase Postgres + pgvector | Production persistence, vector recall | required |
| Auth | Supabase Auth | JWT for API; Clerk/Auth0 later | required |
| Documents | Supabase Storage + parser | Upload → parse → chunk → embed | required |
| AI | Vercel AI SDK + Gebo AI Router | Backend-only model keys | required |
| Security | Cloudflare Turnstile, Upstash, RLS, Sentry | Bot defense, rate limits, tenant isolation | required |
| Billing | Stripe | Plans, subscriptions, usage | required |
| Email | Resend | Transactional email | recommended |
| Observability | Langfuse, PostHog | LLM traces, product analytics | recommended |
| Enterprise SSO | Auth0, WorkOS | Directory sync, SAML | later |

## Request Flow

```
User
  │
  ▼
Gebo Frontend (Next.js / Vercel)
  │  Supabase Auth session
  │  Cloudflare Turnstile on forms
  ▼
Auth + Security (JWT verify, Upstash rate limits, RLS context)
  │
  ▼
Memory Continuity API (recall nodes, relevance, source trail)
  │
  ▼
Presence Router (Gebo | Dream | LockIn | Mya | Hunter | Slatt Tool)
  │
  ▼
AI Gateway (OpenAI / Claude / Gemini / Grok / Ollama by task)
  │
  ▼
Documents / DB / Tools (Storage, pgvector, tool_runs)
  │
  ▼
Output → Reflection → Memory Update
```

## Eight Native Backend Modules

Scaffolded under `backend/app/modules/` — thin stubs, no external API calls yet.

| Module | File | Responsibility |
|--------|------|----------------|
| Identity Core | `identity_core.py` | Users, roles, permissions, plans, device sessions |
| Memory Continuity | `memory_continuity.py` | Memory nodes, recall events, relevance (wraps `memory.py`) |
| Presence Router | `presence_router.py` | Route to Gebo, Dream, LockIn, Mya, Hunter, Slatt Tool |
| AI Gateway | `ai_gateway.py` | Model routing by task/price/speed/privacy |
| Document Intelligence | `document_intelligence.py` | Upload → parse → chunk → embed → store → retrieve |
| Security Command | `security_command.py` | Rate limits, abuse, audit logs |
| Billing & Usage | `billing_usage.py` | Plans, tokens, storage, usage events |
| Admin Console | `admin_console.py` | Users, logs, failed AI, document jobs |

Each module exposes `MODULE_META` and `status()`. Wire real implementations incrementally.

## Schema

Apply `backend/data/schema/official-v1.sql` to Supabase Postgres:

- **Identity:** users, profiles, organizations, memberships, sessions, api_keys
- **Presences:** presences, presence_memory, memory_nodes
- **Documents:** documents, document_chunks, embeddings (pgvector)
- **AI:** conversations, messages, ai_requests, tool_runs
- **Ops:** audit_logs, rate_limit_events, billing_customers, subscriptions, usage_events, integrations, webhooks, admin_flags

Enable `pgvector` extension before using the `embeddings` table vector column.

## What NOT to Add Yet

- Heavy frontend component libraries (shadcn bulk install, complex auth UI pages)
- Auth0 / WorkOS enterprise SSO (V1 uses Supabase Auth only)
- Full document parser integrations (LlamaIndex/Unstructured wired later)
- Next.js API routes replacing FastAPI (scaffold in Python first)
- Replacing Owner Node SQLite — keep for local private mode
- GCP-only dependencies as V1 blockers

## Frontend Constraint

Frontend stays a **clean UX shell**. Only minimal env stubs (`frontend/.env.example`). No new auth pages or heavy components in V1 scaffold.

## Related Docs

- [08-production-release.md](./08-production-release.md) — optional GCP/Firebase enterprise path
- [02-architecture.md](./02-architecture.md) — current Owner Node architecture
- [04-integrations.md](./04-integrations.md) — integration catalog
