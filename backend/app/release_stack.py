"""Official Gebo V1 release stack — Supabase + Vercel production controls."""
from __future__ import annotations

import os
from typing import Any

from app import auth_middleware, model_armor, production_security

# release_tier: required | recommended | later
# surface: frontend | backend | infra
V1_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "supabase_postgres",
        "name": "Supabase Postgres",
        "category": "persistence",
        "surface": "backend",
        "release_tier": "required",
        "env": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "DATABASE_URL"],
        "docs": "https://supabase.com/docs/guides/database",
        "gebo_role": "Production Postgres replacing local SQLite",
    },
    {
        "id": "pgvector",
        "name": "pgvector extension",
        "category": "persistence",
        "surface": "backend",
        "release_tier": "required",
        "env": ["DATABASE_URL"],
        "docs": "https://github.com/pgvector/pgvector",
        "gebo_role": "Vector embeddings for document recall",
    },
    {
        "id": "supabase_auth",
        "name": "Supabase Auth",
        "category": "auth",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET"],
        "docs": "https://supabase.com/docs/guides/auth",
        "gebo_role": "Consumer sign-in, JWT for API",
    },
    {
        "id": "supabase_storage",
        "name": "Supabase Storage",
        "category": "documents",
        "surface": "backend",
        "release_tier": "required",
        "env": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
        "docs": "https://supabase.com/docs/guides/storage",
        "gebo_role": "User uploads, document bundles",
    },
    {
        "id": "vercel_deploy",
        "name": "Vercel (Next.js frontend)",
        "category": "hosting",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["VERCEL_URL", "NEXT_PUBLIC_SUPABASE_URL"],
        "docs": "https://vercel.com/docs",
        "gebo_role": "App Router shell on Vercel",
    },
    {
        "id": "cloudflare_turnstile",
        "name": "Cloudflare Turnstile",
        "category": "web_defense",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["TURNSTILE_SITE_KEY", "TURNSTILE_SECRET_KEY"],
        "docs": "https://developers.cloudflare.com/turnstile/",
        "gebo_role": "Bot protection on login/register",
    },
    {
        "id": "upstash_redis",
        "name": "Upstash Redis",
        "category": "web_defense",
        "surface": "backend",
        "release_tier": "required",
        "env": ["UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN"],
        "docs": "https://upstash.com/docs/redis",
        "gebo_role": "Rate limits and abuse throttling",
    },
    {
        "id": "stripe",
        "name": "Stripe",
        "category": "billing",
        "surface": "backend",
        "release_tier": "required",
        "env": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
        "docs": "https://stripe.com/docs",
        "gebo_role": "Plans, subscriptions, usage billing",
    },
    {
        "id": "resend",
        "name": "Resend",
        "category": "email",
        "surface": "backend",
        "release_tier": "recommended",
        "env": ["RESEND_API_KEY"],
        "docs": "https://resend.com/docs",
        "gebo_role": "Transactional email",
    },
    {
        "id": "sentry",
        "name": "Sentry",
        "category": "observability",
        "surface": "backend",
        "release_tier": "recommended",
        "env": ["SENTRY_DSN"],
        "docs": "https://docs.sentry.io/",
        "gebo_role": "Error tracking frontend + backend",
    },
    {
        "id": "vercel_ai_gateway",
        "name": "Vercel AI SDK / Gateway",
        "category": "ai",
        "surface": "backend",
        "release_tier": "required",
        "env": ["OPENAI_API_KEY"],
        "docs": "https://sdk.vercel.ai/docs",
        "gebo_role": "Backend-only model routing via Gebo AI Gateway",
    },
    {
        "id": "langfuse",
        "name": "Langfuse",
        "category": "observability",
        "surface": "backend",
        "release_tier": "recommended",
        "env": ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"],
        "docs": "https://langfuse.com/docs",
        "gebo_role": "LLM trace observability",
    },
    {
        "id": "posthog",
        "name": "PostHog",
        "category": "observability",
        "surface": "frontend",
        "release_tier": "recommended",
        "env": ["NEXT_PUBLIC_POSTHOG_KEY"],
        "docs": "https://posthog.com/docs",
        "gebo_role": "Product analytics",
    },
    {
        "id": "supabase_rls",
        "name": "Supabase Row Level Security",
        "category": "security",
        "surface": "backend",
        "release_tier": "required",
        "env": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
        "docs": "https://supabase.com/docs/guides/auth/row-level-security",
        "gebo_role": "Tenant isolation on all user tables",
    },
    {
        "id": "auth0",
        "name": "Auth0 (enterprise SSO)",
        "category": "auth",
        "surface": "frontend",
        "release_tier": "later",
        "env": ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID"],
        "docs": "https://auth0.com/docs",
        "gebo_role": "Enterprise SSO — post V1",
    },
    {
        "id": "workos",
        "name": "WorkOS (enterprise SSO)",
        "category": "auth",
        "surface": "frontend",
        "release_tier": "later",
        "env": ["WORKOS_API_KEY", "WORKOS_CLIENT_ID"],
        "docs": "https://workos.com/docs",
        "gebo_role": "Enterprise directory sync — post V1",
    },
]


def _control_env_ready(control: dict[str, Any]) -> bool:
    keys = control.get("env") or []
    if not keys:
        return False
    return all(os.getenv(k, "").strip() for k in keys)


def _control_ping(control: dict[str, Any]) -> bool:
    try:
        from app.v1_clients import health as v1_health

        return v1_health.check_control(control["id"])
    except Exception:
        return False


def _control_ready(control: dict[str, Any]) -> bool:
    mode = os.getenv("GEBO_RELEASE_MODE", "owner").lower()
    tier = control.get("release_tier", "required")

    if mode == "owner" and tier == "required":
        return False

    if mode == "production":
        try:
            from app.v1_clients import health as v1_health

            return v1_health.check_control(control["id"])
        except Exception:
            pass
        return _control_env_ready(control) and _control_ping(control)

    return _control_env_ready(control)


def wired_modules() -> dict[str, Any]:
    prod = production_security.wired_modules()
    return {
        **prod,
        "v1_stack": "supabase_vercel",
        "auth_providers": auth_middleware.auth_providers(),
        "supabase_auth_configured": auth_middleware.supabase_auth_configured(),
        "firebase_auth_configured": auth_middleware.firebase_auth_configured(),
    }


def _modules_ready_count() -> int:
    try:
        from app.modules import all_module_statuses

        return sum(1 for m in all_module_statuses() if m.get("status") == "active")
    except Exception:
        return 0


def v1_readiness() -> dict[str, Any]:
    items = []
    for ctrl in V1_CONTROLS:
        configured = _control_env_ready(ctrl)
        ready = _control_ready(ctrl)
        items.append({**ctrl, "configured": configured, "ready": ready})

    required = [c for c in V1_CONTROLS if c["release_tier"] == "required"]
    recommended = [c for c in V1_CONTROLS if c["release_tier"] == "recommended"]
    later = [c for c in V1_CONTROLS if c["release_tier"] == "later"]

    required_ready = sum(1 for c in required if _control_ready(c))
    score = round(100 * required_ready / len(required)) if required else 0

    mode = os.getenv("GEBO_RELEASE_MODE", "owner").lower()
    modules_ready = _modules_ready_count()
    return {
        "release_mode": mode,
        "owner_node": mode == "owner",
        "official_stack": "supabase_vercel_v1",
        "v1_ready": required_ready == len(required) and mode == "production",
        "readiness_score": score,
        "required_total": len(required),
        "required_ready": required_ready,
        "modules_ready": modules_ready,
        "modules_total": 8,
        "recommended_total": len(recommended),
        "later_total": len(later),
        "controls": items,
        "local_controls": production_security.LOCAL_OWNER_CONTROLS,
        "wired": wired_modules(),
        "next_steps": _next_steps(required_ready, len(required), mode),
    }


def _next_steps(ready: int, total: int, mode: str) -> list[str]:
    if mode == "owner":
        return [
            "Owner Node: local SQLite + Ollama is correct for private use.",
            "Set GEBO_RELEASE_MODE=production when deploying V1 to Supabase + Vercel.",
            "Configure Supabase Auth + Postgres before public URL.",
            "See docs/official/09-official-v1-release.md for full stack.",
        ]
    steps = []
    if ready < total:
        steps.append(
            f"Configure {total - ready} required V1 control(s) via env / Supabase dashboard."
        )
    steps.extend([
        "Apply backend/data/schema/official-v1.sql to Supabase Postgres.",
        "Enable Supabase RLS policies on all user tables.",
        "Wire Cloudflare Turnstile on auth forms and Upstash rate limits on API.",
        "Enable Sentry + Langfuse before public beta.",
    ])
    return steps
