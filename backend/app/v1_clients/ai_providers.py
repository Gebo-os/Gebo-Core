"""AI providers — OpenAI official SDK; Anthropic/Gemini env stubs."""
from __future__ import annotations

import logging
import os
from typing import Any

from app import ollama_client

logger = logging.getLogger(__name__)


def openai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


def anthropic_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())


def gemini_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def ping_openai() -> bool:
    if not openai_configured():
        return False
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "").strip())
        client.models.list(limit=1)
        return True
    except Exception as exc:
        logger.debug("openai ping failed: %s", exc)
        return False


async def ping_ollama() -> bool:
    try:
        await ollama_client.chat("ping", "ping")
        return True
    except RuntimeError:
        return False


def provider_status() -> dict[str, Any]:
    return {
        "openai": {"configured": openai_configured(), "live": ping_openai()},
        "anthropic": {"configured": anthropic_configured(), "live": False},
        "gemini": {"configured": gemini_configured(), "live": False},
        "ollama": {"configured": bool(ollama_client.get_model()), "model": ollama_client.get_model()},
    }


async def route_chat(system_prompt: str, user_message: str) -> dict[str, Any]:
    """Route chat to OpenAI when configured, else Ollama."""
    if openai_configured():
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "").strip())
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            reply = (completion.choices[0].message.content or "").strip()
            return {"reply": reply, "provider": "openai", "model": model}
        except Exception as exc:
            logger.warning("openai route failed, falling back to ollama: %s", exc)

    reply = await ollama_client.chat(system_prompt, user_message)
    return {
        "reply": reply,
        "provider": "ollama",
        "model": ollama_client.get_model(),
    }
