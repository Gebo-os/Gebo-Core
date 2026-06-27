"""Load secrets from GCP Secret Manager into os.environ (production only)."""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_loaded = False
_loaded_count = 0
_skip_reason: str | None = None


def release_mode() -> str:
    return os.getenv("GEBO_RELEASE_MODE", "owner").lower()


def secrets_loader_active() -> bool:
    return _loaded and _loaded_count > 0


def last_skip_reason() -> str | None:
    return _skip_reason


def load_secrets_from_gcp() -> dict[str, Any]:
    """Optionally hydrate os.environ from Secret Manager on startup."""
    global _loaded, _loaded_count, _skip_reason

    if release_mode() != "production":
        _skip_reason = "owner_mode"
        return {"loaded": False, "count": 0, "reason": _skip_reason}

    project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        _skip_reason = "no_project"
        return {"loaded": False, "count": 0, "reason": _skip_reason}

    if os.getenv("GEBO_SECRET_MANAGER_ENABLED", "true").lower() in (
        "0",
        "false",
        "no",
    ):
        _skip_reason = "disabled"
        return {"loaded": False, "count": 0, "reason": _skip_reason}

    names_raw = os.getenv("GEBO_SECRET_NAMES", "").strip()
    secret_names = (
        [n.strip() for n in names_raw.split(",") if n.strip()]
        if names_raw
        else []
    )

    try:
        from google.cloud import secretmanager  # type: ignore[import-untyped]
    except ImportError:
        _skip_reason = "google_cloud_secret_manager_not_installed"
        logger.info(
            "Secret Manager skip: google-cloud-secret-manager not installed"
        )
        return {"loaded": False, "count": 0, "reason": _skip_reason}

    if not secret_names:
        _skip_reason = "no_secret_names"
        logger.info("Secret Manager skip: GEBO_SECRET_NAMES not set")
        return {"loaded": False, "count": 0, "reason": _skip_reason}

    client = secretmanager.SecretManagerServiceClient()
    count = 0
    for name in secret_names:
        try:
            resource = f"projects/{project}/secrets/{name}/versions/latest"
            response = client.access_secret_version(request={"name": resource})
            value = response.payload.data.decode("utf-8")
            env_key = name.upper().replace("-", "_")
            os.environ[env_key] = value
            count += 1
        except Exception as exc:
            logger.warning("Failed to load secret %s: %s", name, exc)

    _loaded = True
    _loaded_count = count
    _skip_reason = None if count else "load_failed"
    return {"loaded": count > 0, "count": count, "reason": _skip_reason}
