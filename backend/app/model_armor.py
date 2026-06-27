"""Model Armor screening hook for /chat — pass-through when not configured."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScreenResult:
    text: str
    blocked: bool
    reason: str | None = None


def is_configured() -> bool:
    if os.getenv("GEBO_RELEASE_MODE", "owner").lower() != "production":
        return False
    if os.getenv("GEBO_MODEL_ARMOR_ENABLED", "false").lower() not in (
        "1",
        "true",
        "yes",
    ):
        return False
    return bool(os.getenv("GOOGLE_CLOUD_PROJECT", "").strip())


def model_armor_active() -> bool:
    return is_configured()


async def screen_input(text: str) -> ScreenResult:
    if not is_configured():
        return ScreenResult(text=text, blocked=False)
    logger.info("Model Armor input screening (stub): %d chars", len(text))
    return ScreenResult(text=text, blocked=False)


async def screen_output(text: str) -> ScreenResult:
    if not is_configured():
        return ScreenResult(text=text, blocked=False)
    logger.info("Model Armor output screening (stub): %d chars", len(text))
    return ScreenResult(text=text, blocked=False)
