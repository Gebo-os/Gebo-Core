"""Test all Gebo V1 + local connections — run from backend/: python scripts/test_all_connections.py"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))
load_dotenv(BACKEND / ".env")

# Required V1 env keys per control
CONTROL_ENV: dict[str, list[str]] = {
    "supabase_postgres": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "DATABASE_URL"],
    "pgvector": ["DATABASE_URL"],
    "supabase_auth": ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET"],
    "supabase_storage": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
    "vercel_deploy": ["VERCEL_URL", "NEXT_PUBLIC_SUPABASE_URL"],
    "cloudflare_turnstile": ["TURNSTILE_SITE_KEY", "TURNSTILE_SECRET_KEY"],
    "upstash_redis": ["UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN"],
    "stripe": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
    "vercel_ai_gateway": ["OPENAI_API_KEY"],
    "supabase_rls": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
}

LOCAL_CHECKS = [
    ("ollama", "OLLAMA_BASE_URL", "ollama"),
    ("backend_health", "GEBO_BACKEND_URL", "http"),
    ("sqlite_db", None, "local"),
]


def env_set(key: str) -> bool:
    return bool(os.getenv(key, "").strip())


def env_status(keys: list[str]) -> dict[str, bool]:
    return {k: env_set(k) for k in keys}


def test_ollama() -> dict:
    import httpx

    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{base}/api/tags")
            if r.status_code != 200:
                return {"live": False, "detail": f"HTTP {r.status_code}"}
            models = [m.get("name") for m in r.json().get("models", [])]
            configured = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
            return {
                "live": True,
                "detail": f"{len(models)} model(s)",
                "default_model": configured,
                "model_available": configured in models or any(configured in m for m in models),
            }
    except Exception as exc:
        return {"live": False, "detail": str(exc)[:120]}


def test_backend() -> dict:
    import httpx

    url = os.getenv("GEBO_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{url}/health")
            return {"live": r.status_code == 200, "detail": r.json() if r.status_code == 200 else r.status_code}
    except Exception as exc:
        return {"live": False, "detail": str(exc)[:120]}


def test_sqlite() -> dict:
    try:
        from app import db

        db.init_db()
        return {"live": True, "detail": {"memories": db.count_memories(), "messages": db.count_messages()}}
    except Exception as exc:
        return {"live": False, "detail": str(exc)[:120]}


def main() -> int:
    from app.modules import all_module_statuses
    from app.release_stack import v1_readiness
    from app.v1_clients import health as v1_health

    mode = os.getenv("GEBO_RELEASE_MODE", "owner")
    v1_health.clear_cache()

    report: dict = {
        "release_mode": mode,
        "local": {},
        "v1_controls": [],
        "modules": all_module_statuses(),
        "readiness": {},
    }

    report["local"]["ollama"] = test_ollama()
    report["local"]["backend"] = test_backend()
    report["local"]["sqlite"] = test_sqlite()

    for cid, keys in CONTROL_ENV.items():
        envs = env_status(keys)
        all_env = all(envs.values())
        live = v1_health.check_control(cid) if mode == "production" else False
        report["v1_controls"].append({
            "id": cid,
            "env_configured": all_env,
            "env_keys": envs,
            "live_ping": live,
            "ready": live if mode == "production" else all_env,
        })

    # Also test in owner mode what env is set (informational)
    report["env_configured_count"] = sum(1 for c in report["v1_controls"] if c["env_configured"])
    report["readiness"] = {
        "score": v1_readiness()["readiness_score"],
        "required_ready": v1_readiness()["required_ready"],
        "required_total": v1_readiness()["required_total"],
        "modules_ready": v1_readiness().get("modules_ready"),
        "modules_total": v1_readiness().get("modules_total"),
    }

    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
