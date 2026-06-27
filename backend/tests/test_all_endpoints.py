"""Smoke test every API route — one function per endpoint group."""
from __future__ import annotations

import pytest


def test_all_get_endpoints(client):
    """Every GET route returns 200 with expected shape."""
    checks = [
        ("/health", lambda d: d["ok"] is True),
        ("/status", lambda d: "model" in d),
        ("/memory", lambda d: isinstance(d, list)),
        ("/actions", lambda d: isinstance(d, list)),
        ("/codex/status", lambda d: "available" in d),
        ("/wiki/status", lambda d: "enabled" in d),
        ("/reflexes", lambda d: len(d) >= 1),
        ("/reflex-events", lambda d: isinstance(d, list)),
        ("/agents/runtime/status", lambda d: d["running"] is True),
        ("/evolution/status", lambda d: "total_evolution_events" in d),
        ("/evolution/events", lambda d: isinstance(d, list)),
        ("/evolution/scores", lambda d: isinstance(d, list)),
        ("/evolution/upgrades", lambda d: isinstance(d, list)),
        ("/settings/network", lambda d: "internet_access" in d),
        ("/integrate/bootstrap", lambda d: "status" in d and "capabilities" in d),
        ("/integrations/status", lambda d: "items" in d and d["total"] >= 1),
        ("/cli/status", lambda d: "items" in d),
        ("/knowledge/status", lambda d: "catalog_oss_count" in d),
        ("/system/private", lambda d: d.get("system") == "Gebo OS Private"),
        ("/system/production-readiness", lambda d: "readiness_score" in d),
        ("/system/v1-readiness", lambda d: d.get("official_stack") == "supabase_vercel_v1"),
        ("/system/modules", lambda d: d.get("count") == 8),
        ("/v1/billing/plans", lambda d: "plans" in d and len(d["plans"]) >= 1),
        ("/v1/identity/owner-status", lambda d: d.get("owner_mode") is True),
    ]
    for path, validator in checks:
        r = client.get(path)
        assert r.status_code == 200, f"GET {path} failed: {r.text}"
        assert validator(r.json()), f"GET {path} shape invalid: {r.json()}"


def test_memory_export_endpoint(client):
    client.post("/memory", json={"memory_type": "core", "content": "smoke test memory"})
    r = client.get("/memory/export")
    assert r.status_code == 200
    data = r.json()
    for key in (
        "memories",
        "messages",
        "settings",
        "actions",
        "reflexes",
        "reflex_events",
        "evolution_events",
    ):
        assert key in data


def test_settings_consent_endpoint(client):
    r = client.post("/settings/consent", json={"allowed": True})
    assert r.status_code == 200
    assert r.json()["consent"] is True


def test_settings_network_endpoint(client):
    r = client.get("/settings/network")
    assert r.status_code == 200
    assert r.json()["internet_access"] is True

    r2 = client.post("/settings/network", json={"internet_access": False})
    assert r2.status_code == 200
    assert r2.json()["internet_access"] is False
    assert r2.json()["cors_mode"] == "localhost"

    r3 = client.post("/settings/network", json={"internet_access": True})
    assert r3.status_code == 200
    assert r3.json()["internet_access"] is True
    assert r3.json()["cors_mode"] == "open"


def test_memory_post_endpoint(client):
    r = client.post(
        "/memory",
        json={"memory_type": "project", "content": "Endpoint smoke test entry."},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_chat_endpoint(client):
    r = client.post("/chat", json={"message": "ping gebo smoke test"})
    assert r.status_code == 200
    data = r.json()
    assert data["reply"]
    assert isinstance(data["recalled_memories"], list)
    assert isinstance(data["proposed_actions"], list)
    assert isinstance(data["detected_reflexes"], list)
    assert isinstance(data["wiki_sources"], list)


def test_actions_full_lifecycle(client):
    proposed = client.post(
        "/actions/propose",
        json={
            "action_type": "export_memory",
            "title": "Smoke export",
            "description": "Full lifecycle test",
            "payload_json": {},
        },
    )
    assert proposed.status_code == 200
    action_id = proposed.json()["id"]

    assert client.post(f"/actions/{action_id}/approve").status_code == 200
    run = client.post(f"/actions/{action_id}/run")
    assert run.status_code == 200

    actions = client.get("/actions").json()
    completed = next(a for a in actions if a["id"] == action_id)
    assert completed["status"] == "completed"


def test_reflex_create_toggle_endpoint(client):
    created = client.post(
        "/reflexes",
        json={
            "name": "Smoke Reflex",
            "description": "All-endpoints test",
            "trigger_type": "keyword",
            "trigger_pattern": r"smoke test reflex",
            "action_type": "save_memory",
            "approval_required": True,
            "enabled": True,
        },
    )
    assert created.status_code == 200
    reflex_id = created.json()["id"]
    toggled = client.post(f"/reflexes/{reflex_id}/toggle")
    assert toggled.status_code == 200


def test_evolution_full_flow(client):
    action_id = client.post(
        "/actions/propose",
        json={
            "action_type": "create_plan",
            "title": "Evolution smoke",
            "description": "Score target",
            "payload_json": {},
        },
    ).json()["id"]

    score = client.post(
        "/evolution/score-action",
        json={
            "action_id": action_id,
            "mission_value": 7,
            "speed_score": 7,
            "risk_score": 8,
            "approval_score": 9,
            "memory_impact": 6,
            "product_impact": 7,
            "money_impact": 5,
            "notes": "Smoke test scoring.",
        },
    )
    assert score.status_code == 200

    upgrade_id = client.post(
        "/evolution/suggest-upgrade",
        json={
            "upgrade_type": "agent",
            "title": "Smoke Upgrade",
            "description": "Test upgrade",
            "reason": "Smoke test",
        },
    ).json()["id"]

    assert client.post(f"/evolution/upgrades/{upgrade_id}/approve").status_code == 200
    assert client.post(
        "/evolution/suggest-upgrade",
        json={
            "upgrade_type": "tool",
            "title": "Reject smoke",
            "description": "Reject path",
            "reason": "Smoke",
        },
    ).status_code == 200


def test_wiki_search_endpoint(client):
    r = client.get("/wiki/search", params={"q": "geography"})
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        data = r.json()
        assert "results" in data or isinstance(data, list)


def test_open_cors_when_internet_access(client):
    client.post("/settings/network", json={"internet_access": True})
    r = client.get(
        "/health",
        headers={"Origin": "https://example.com"},
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") in (
        "https://example.com",
        "*",
    )


@pytest.mark.parametrize(
    "method,path,body,params",
    [
        ("post", "/chat", {"message": ""}, None),
        ("post", "/memory", {"memory_type": "core", "content": ""}, None),
        ("get", "/wiki/search", None, {"q": "  "}),
    ],
)
def test_validation_errors(client, method, path, body, params):
    if method == "get":
        r = client.get(path, params=params)
    else:
        r = client.post(path, json=body)
    assert r.status_code in (400, 422)


def test_learning_cycle_endpoint(client):
    r = client.post("/learning/cycle")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "collection" in data
    assert "knowledge" in data


def test_system_build_endpoint(client):
    r = client.post("/system/build")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "manifest" in data
    assert data["manifest"]["version"] >= 1


def test_v1_turnstile_endpoint(client):
    r = client.post("/v1/security/verify-turnstile", json={"token": ""})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert "error" in data or "error_codes" in data


def test_knowledge_collect_endpoint(client):
    r = client.post("/knowledge/collect")
    assert r.status_code == 200
    data = r.json()
    assert "catalog" in data
    assert isinstance(data["catalog"], dict)
