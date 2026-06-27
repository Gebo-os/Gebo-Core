"""AI Gateway — model routing by task, price, speed, privacy."""
from __future__ import annotations

import os
from typing import Any

from app import ollama_client
from app.modules.common import resolve_status
from app.v1_clients import ai_providers

MODULE_META = {
    "id": "ai_gateway",
    "name": "AI Gateway",
    "surface": "backend",
}

PROVIDERS: list[dict[str, Any]] = [
    {"id": "openai", "env": ["OPENAI_API_KEY"], "tier": "cloud"},
    {"id": "anthropic", "env": ["ANTHROPIC_API_KEY"], "tier": "cloud"},
    {"id": "gemini", "env": ["GEMINI_API_KEY"], "tier": "cloud"},
    {"id": "grok", "env": ["XAI_API_KEY"], "tier": "cloud"},
    {"id": "ollama", "env": ["OLLAMA_MODEL"], "tier": "local"},
]


def _provider_configured(provider: dict[str, Any]) -> bool:
    keys = provider.get("env") or []
    return any(os.getenv(k, "").strip() for k in keys)


def _owner_live() -> bool:
    return bool(ollama_client.get_model())


def _production_live() -> bool:
    return ai_providers.ping_openai() or _owner_live()


def status() -> dict[str, Any]:
    configured = [p["id"] for p in PROVIDERS if _provider_configured(p)]
    return {
        **MODULE_META,
        "status": resolve_status(
            "ai_gateway",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "providers": PROVIDERS,
        "configured_providers": configured,
        "local_model": ollama_client.get_model(),
        "default_route": "ollama" if ollama_client.get_model() else "none",
        "openai_live": ai_providers.ping_openai(),
        "env_required": ["OPENAI_API_KEY"],
        "notes": "Backend-only keys; routes via official OpenAI SDK or Ollama.",
    }


def select_model(
    *,
    task: str = "chat",
    prefer_privacy: bool = False,
    prefer_speed: bool = False,
) -> dict[str, Any]:
    active = resolve_status(
        "ai_gateway",
        production_live=_production_live(),
        owner_live=_owner_live(),
    )
    if prefer_privacy or os.getenv("GEBO_RELEASE_MODE", "owner") == "owner":
        return {
            "provider": "ollama",
            "model": ollama_client.get_model(),
            "reason": "local_privacy",
            "status": active,
        }
    if ai_providers.openai_configured():
        return {
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "task": task,
            "prefer_speed": prefer_speed,
            "status": active,
        }
    for provider in PROVIDERS:
        if provider["id"] != "ollama" and _provider_configured(provider):
            return {
                "provider": provider["id"],
                "model": None,
                "task": task,
                "prefer_speed": prefer_speed,
                "status": active,
            }
    return {
        "provider": "ollama",
        "model": ollama_client.get_model(),
        "reason": "fallback",
        "status": active,
    }


async def route_chat(system_prompt: str, user_message: str) -> dict[str, Any]:
    result = await ai_providers.route_chat(system_prompt, user_message)
    route = select_model(task="chat")
    return {
        "reply": result.get("reply"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "route": route,
        "status": resolve_status(
            "ai_gateway",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


async def handle_chat_stub(system_prompt: str, user_message: str) -> dict[str, Any]:
    return await route_chat(system_prompt, user_message)
