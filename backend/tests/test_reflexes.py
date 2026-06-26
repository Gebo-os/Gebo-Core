"""Tests for Gebo Reflex Engine."""
from __future__ import annotations


def test_reflexes_seeded(client):
    r = client.get("/reflexes")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 6
    names = {reflex["name"] for reflex in data}
    assert "Build Log Reflex" in names
    assert "Memory Capture Reflex" in names
    assert all(reflex["approval_required"] for reflex in data)


def test_reflex_toggle(client):
    reflexes = client.get("/reflexes").json()
    reflex_id = reflexes[0]["id"]
    was_enabled = reflexes[0]["enabled"]

    toggled = client.post(f"/reflexes/{reflex_id}/toggle").json()
    assert toggled["enabled"] is not was_enabled

    restored = client.post(f"/reflexes/{reflex_id}/toggle").json()
    assert restored["enabled"] is was_enabled


def test_reflex_create(client):
    r = client.post(
        "/reflexes",
        json={
            "name": "Test Reflex",
            "description": "Custom test reflex",
            "trigger_type": "keyword",
            "trigger_pattern": r"test pattern",
            "action_type": "save_memory",
            "approval_required": True,
            "enabled": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Test Reflex"


def test_reflex_events_empty_initially(client):
    r = client.get("/reflex-events")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_chat_triggers_build_reflex(client):
    r = client.post(
        "/chat",
        json={
            "message": (
                "I fixed the frontend today but the memory page still looks weak."
            )
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "detected_reflexes" in data
    assert len(data["detected_reflexes"]) >= 1
    assert any("Build Log" in d["name"] for d in data["detected_reflexes"])
    assert len(data["proposed_actions"]) >= 1

    events = client.get("/reflex-events").json()
    assert len(events) >= 1
