"""Production release controls — auth, persistence, encryption, web defense (private backend)."""
from __future__ import annotations

import os
from typing import Any

from app import auth_middleware, model_armor, recaptcha, secrets_loader

# release_tier: required | recommended | enterprise
# surface: frontend | backend | infra
PRODUCTION_CONTROLS: list[dict[str, Any]] = [
    {
        "id": "identity_platform",
        "name": "Identity Platform (Firebase Auth / CIAM)",
        "category": "auth",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["FIREBASE_PROJECT_ID", "FIREBASE_API_KEY"],
        "docs": "https://cloud.google.com/identity-platform/docs",
        "gebo_role": "Consumer sign-in, JWT for API",
    },
    {
        "id": "google_passkeys",
        "name": "Sign In with Google & Passkeys",
        "category": "auth",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["GOOGLE_CLIENT_ID"],
        "docs": "https://developers.google.com/identity/authentication",
        "gebo_role": "Biometric / passkey login on web and mobile",
    },
    {
        "id": "iap",
        "name": "Identity-Aware Proxy",
        "category": "auth",
        "surface": "backend",
        "release_tier": "enterprise",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/iap/docs",
        "gebo_role": "Zero-trust gate before Cloud Run / admin routes",
    },
    {
        "id": "cloud_sql",
        "name": "Cloud SQL",
        "category": "persistence",
        "surface": "backend",
        "release_tier": "required",
        "env": ["DATABASE_URL"],
        "docs": "https://cloud.google.com/sql/docs",
        "gebo_role": "Production Postgres replacing local SQLite",
    },
    {
        "id": "cloud_spanner",
        "name": "Cloud Spanner",
        "category": "persistence",
        "surface": "backend",
        "release_tier": "enterprise",
        "env": ["SPANNER_INSTANCE"],
        "docs": "https://cloud.google.com/spanner/docs",
        "gebo_role": "Global ACID scale — later tier",
    },
    {
        "id": "firestore_prod",
        "name": "Cloud Firestore (production)",
        "category": "persistence",
        "surface": "frontend",
        "release_tier": "recommended",
        "env": ["FIREBASE_PROJECT_ID"],
        "docs": "https://firebase.google.com/docs/firestore",
        "gebo_role": "Realtime client state, offline sync",
    },
    {
        "id": "recaptcha_enterprise",
        "name": "reCAPTCHA Enterprise",
        "category": "web_defense",
        "surface": "frontend",
        "release_tier": "required",
        "env": ["RECAPTCHA_SITE_KEY", "RECAPTCHA_PROJECT_ID"],
        "docs": "https://cloud.google.com/recaptcha-enterprise/docs",
        "gebo_role": "Bot protection on login/register",
    },
    {
        "id": "cloud_armor",
        "name": "Cloud Armor",
        "category": "web_defense",
        "surface": "infra",
        "release_tier": "recommended",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/armor/docs",
        "gebo_role": "DDoS + WAF at load balancer",
    },
    {
        "id": "secret_manager",
        "name": "Secret Manager",
        "category": "encryption",
        "surface": "backend",
        "release_tier": "required",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/secret-manager/docs",
        "gebo_role": "No secrets in .env in production",
    },
    {
        "id": "model_armor",
        "name": "Model Armor",
        "category": "web_defense",
        "surface": "backend",
        "release_tier": "required",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/security/products/model-armor",
        "gebo_role": "Prompt/response firewall for /chat and agents",
    },
    {
        "id": "cloud_storage",
        "name": "Cloud Storage",
        "category": "documents",
        "surface": "backend",
        "release_tier": "recommended",
        "env": ["GCS_BUCKET"],
        "docs": "https://cloud.google.com/storage/docs",
        "gebo_role": "User uploads, exports, doc bundles",
    },
    {
        "id": "cloud_dlp",
        "name": "Sensitive Data Protection (DLP)",
        "category": "documents",
        "surface": "backend",
        "release_tier": "recommended",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/dlp/docs",
        "gebo_role": "Scan/redact PII in private-docs and exports",
    },
    {
        "id": "artifact_analysis",
        "name": "Artifact Analysis",
        "category": "audit",
        "surface": "infra",
        "release_tier": "recommended",
        "env": ["GOOGLE_CLOUD_PROJECT"],
        "docs": "https://cloud.google.com/artifact-analysis/docs",
        "gebo_role": "CVE scan on container images in CI/CD",
    },
]

LOCAL_OWNER_CONTROLS: list[dict[str, str]] = [
    {"id": "local_sqlite", "name": "SQLite (Owner Node)", "status": "active"},
    {"id": "local_ollama", "name": "Ollama local model", "status": "active"},
    {"id": "approval_gate", "name": "Action approval gate", "status": "active"},
    {"id": "internet_toggle", "name": "Internet access toggle", "status": "active"},
]


def _control_configured(control: dict[str, Any]) -> bool:
    keys = control.get("env") or []
    if not keys:
        return False
    return all(os.getenv(k, "").strip() for k in keys)


def wired_modules() -> dict[str, Any]:
    return {
        "auth_middleware_active": auth_middleware.auth_enabled(),
        "auth_providers": auth_middleware.auth_providers(),
        "secrets_loader_active": secrets_loader.secrets_loader_active(),
        "secrets_loader_skip_reason": secrets_loader.last_skip_reason(),
        "model_armor_active": model_armor.model_armor_active(),
        "recaptcha_helper_available": True,
        "recaptcha_configured": recaptcha.recaptcha_configured(),
        "v1_readiness_endpoint": "/system/v1-readiness",
    }


def readiness() -> dict[str, Any]:
    items = []
    for ctrl in PRODUCTION_CONTROLS:
        configured = _control_configured(ctrl)
        items.append({**ctrl, "configured": configured, "ready": configured})

    required = [c for c in PRODUCTION_CONTROLS if c["release_tier"] == "required"]
    required_ready = sum(1 for c in required if _control_configured(c))
    score = round(100 * required_ready / len(required)) if required else 0

    mode = os.getenv("GEBO_RELEASE_MODE", "owner").lower()
    return {
        "release_mode": mode,
        "owner_node": mode == "owner",
        "production_ready": required_ready == len(required) and mode == "production",
        "readiness_score": score,
        "required_total": len(required),
        "required_ready": required_ready,
        "controls": items,
        "local_controls": LOCAL_OWNER_CONTROLS,
        "wired": wired_modules(),
        "next_steps": _next_steps(required_ready, len(required), mode),
    }


def _next_steps(ready: int, total: int, mode: str) -> list[str]:
    if mode == "owner":
        return [
            "Owner Node: local SQLite + Ollama is correct for private use.",
            "Set GEBO_RELEASE_MODE=production when deploying to GCP.",
            "Configure Firebase Auth + Secret Manager before public URL.",
        ]
    steps = []
    if ready < total:
        steps.append(f"Configure {total - ready} required production control(s) via env / Secret Manager.")
    steps.extend([
        "Enable GEBO_AUTH_ENABLED=true with Firebase or Supabase JWT secrets.",
        "Set GEBO_MODEL_ARMOR_ENABLED=true and configure GCP Model Armor.",
        "Load secrets via GEBO_SECRET_NAMES + Secret Manager on Cloud Run.",
        "Run Artifact Analysis in CI on backend Docker image.",
    ])
    return steps
