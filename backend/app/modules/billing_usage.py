"""Billing usage — plans, tokens, storage, usage events."""
from __future__ import annotations

import os
from typing import Any

from app.modules.common import resolve_status
from app.v1_clients import stripe_client

MODULE_META = {
    "id": "billing_usage",
    "name": "Billing & Usage",
    "surface": "backend",
}

PLANS: list[dict[str, Any]] = [
    {"id": "free", "name": "Free", "tokens_monthly": 10_000},
    {"id": "pro", "name": "Pro", "tokens_monthly": 500_000},
    {"id": "team", "name": "Team", "tokens_monthly": 2_000_000},
]


def _owner_live() -> bool:
    return False


def _production_live() -> bool:
    return stripe_client.ping()


def status() -> dict[str, Any]:
    return {
        **MODULE_META,
        "status": resolve_status(
            "billing_usage",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "plans": PLANS,
        "stripe_configured": stripe_client.is_configured(),
        "stripe_live": stripe_client.ping(),
        "env_required": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
        "notes": "Plans from PLANS constant; Stripe for subscriptions in production.",
    }


def list_plans() -> dict[str, Any]:
    return {
        "plans": PLANS,
        "stripe_live": stripe_client.ping(),
        "status": resolve_status(
            "billing_usage",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_usage_event_stub(
    user_id: str,
    event_type: str,
    quantity: int = 1,
) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "event_type": event_type,
        "quantity": quantity,
        "recorded": stripe_client.is_configured(),
        "status": resolve_status(
            "billing_usage",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_plan_stub(user_id: str) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "plan_id": "free",
        "status": resolve_status(
            "billing_usage",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }
