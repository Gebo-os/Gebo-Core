"""Stripe — official Python SDK."""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY", "").strip())


def ping() -> bool:
    if not is_configured():
        return False
    try:
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        stripe.Account.retrieve()
        return True
    except Exception as exc:
        logger.debug("stripe ping failed: %s", exc)
        return False
