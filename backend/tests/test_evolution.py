"""Tests for Gebo Evolution Loop."""
from __future__ import annotations


def test_evolution_status(client):
    r = client.get("/evolution/status")
    assert r.status_code == 200
    data = r.json()
    assert "average_autonomy_score" in data
    assert "total_evolution_events" in data
    assert "proposed_upgrades" in data
    assert data["total_evolution_events"] == 0


def test_score_action_creates_event(client):
    action = client.post(
        "/actions/propose",
        json={
            "action_type": "export_memory",
            "title": "Score me",
            "description": "For evolution test",
            "payload_json": {},
        },
    ).json()
    action_id = action["id"]

    r = client.post(
        "/evolution/score-action",
        json={
            "action_id": action_id,
            "mission_value": 8,
            "speed_score": 7,
            "risk_score": 9,
            "approval_score": 10,
            "memory_impact": 7,
            "product_impact": 8,
            "money_impact": 6,
            "notes": "UI improved, search still weak.",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_score"] == 8
    assert "lesson" in data

    events = client.get("/evolution/events").json()
    assert len(events) >= 1
    assert events[0]["score"] == 8

    scores = client.get("/evolution/scores").json()
    assert len(scores) >= 1
    assert scores[0]["action_id"] == action_id

    status = client.get("/evolution/status").json()
    assert status["average_autonomy_score"] == 8.0
    assert status["total_evolution_events"] >= 1


def test_suggest_and_approve_upgrade(client):
    created = client.post(
        "/evolution/suggest-upgrade",
        json={
            "upgrade_type": "reflex",
            "title": "Test Reflex Upgrade",
            "description": "Auto-format build logs",
            "reason": "Manual build logs repeat often",
        },
    )
    assert created.status_code == 200
    upgrade_id = created.json()["id"]

    upgrades = client.get("/evolution/upgrades").json()
    assert any(u["id"] == upgrade_id for u in upgrades)

    approved = client.post(f"/evolution/upgrades/{upgrade_id}/approve")
    assert approved.status_code == 200
    data = approved.json()
    assert data["status"] == "approved"
    assert data["proposed_action_id"] is not None

    actions = client.get("/actions").json()
    assert any(a["id"] == data["proposed_action_id"] for a in actions)


def test_reject_upgrade(client):
    upgrade_id = client.post(
        "/evolution/suggest-upgrade",
        json={
            "upgrade_type": "tool",
            "title": "Reject Me Upgrade",
            "description": "Test reject flow",
            "reason": "Testing",
        },
    ).json()["id"]

    r = client.post(f"/evolution/upgrades/{upgrade_id}/reject")
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"


def test_action_completion_records_evolution_event(client):
    action_id = client.post(
        "/actions/propose",
        json={
            "action_type": "export_memory",
            "title": "Complete for evolution",
            "description": "Test",
            "payload_json": {},
        },
    ).json()["id"]
    client.post(f"/actions/{action_id}/approve")
    client.post(f"/actions/{action_id}/run")

    events = client.get("/evolution/events").json()
    assert any(e["source_id"] == action_id for e in events)
