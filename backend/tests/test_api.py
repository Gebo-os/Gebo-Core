"""API integration tests for Gebo Core Private."""
from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Gebo" in data["app"]
    assert "agent_runtime_healthy" in data


def test_agent_runtime_status(client):
    r = client.get("/agents/runtime/status")
    assert r.status_code == 200
    data = r.json()
    assert data["running"] is True
    assert data["active_agents"] >= 8
    assert data["healthy"] is True
    assert data.get("parallel_workers", 0) >= 8
    assert "codex_lane" in data
    assert data["codex_lane"]["parallel_with_agents"] is True
    assert len(data["agents"]) >= 8
    for agent in data["agents"]:
        assert "agent_id" in agent
        assert "status" in agent
        assert "cycles" in agent


def test_status_keys(client):
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    for key in (
        "app",
        "model",
        "consent",
        "memory_count",
        "message_count",
        "proposed_action_count",
        "approved_action_count",
        "completed_action_count",
    ):
        assert key in data


def test_consent_toggle(client):
    r = client.post("/settings/consent", json={"allowed": True})
    assert r.status_code == 200
    assert r.json()["consent"] is True
    assert client.get("/status").json()["consent"] is True

    client.post("/settings/consent", json={"allowed": False})
    assert client.get("/status").json()["consent"] is False


def test_memory_create_and_list(client):
    r = client.post(
        "/memory",
        json={"memory_type": "core", "content": "Gebo remembers this."},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    memories = client.get("/memory").json()
    assert len(memories) >= 1
    assert memories[0]["content"] == "Gebo remembers this."


def test_memory_export(client):
    client.post("/memory", json={"memory_type": "core", "content": "export me"})
    r = client.get("/memory/export")
    assert r.status_code == 200
    data = r.json()
    assert "memories" in data
    assert "messages" in data
    assert "settings" in data
    assert "actions" in data


def test_memory_validation_empty(client):
    r = client.post("/memory", json={"memory_type": "core", "content": ""})
    assert r.status_code == 422


def test_memory_validation_too_long(client):
    r = client.post(
        "/memory",
        json={"memory_type": "core", "content": "x" * 12001},
    )
    assert r.status_code == 422


def test_actions_propose_approve_reject(client):
    r = client.post(
        "/actions/propose",
        json={
            "action_type": "save_memory",
            "title": "Save test memory",
            "description": "Test action",
            "payload_json": {"content": "from action"},
        },
    )
    assert r.status_code == 200
    action_id = r.json()["id"]

    actions = client.get("/actions").json()
    proposed = [a for a in actions if a["id"] == action_id][0]
    assert proposed["status"] == "proposed"

    client.post(f"/actions/{action_id}/approve")
    assert (
        client.get("/actions").json()[0]["status"] == "approved"
        or any(
            a["id"] == action_id and a["status"] == "approved"
            for a in client.get("/actions").json()
        )
    )

    r2 = client.post(
        "/actions/propose",
        json={
            "action_type": "create_plan",
            "title": "Plan B",
            "description": "To reject",
            "payload_json": {},
        },
    )
    reject_id = r2.json()["id"]
    client.post(f"/actions/{reject_id}/reject")
    rejected = next(a for a in client.get("/actions").json() if a["id"] == reject_id)
    assert rejected["status"] == "rejected"


def test_run_unapproved_action_fails(client):
    r = client.post(
        "/actions/propose",
        json={
            "action_type": "export_memory",
            "title": "Export",
            "description": "Export memory",
            "payload_json": {},
        },
    )
    action_id = r.json()["id"]
    run = client.post(f"/actions/{action_id}/run")
    assert run.status_code == 400


def test_chat_mocked(client):
    r = client.post("/chat", json={"message": "hello gebo"})
    assert r.status_code == 200
    data = r.json()
    assert data["reply"] == "Test reply from Gebo."
    assert "recalled_memories" in data
    assert "proposed_actions" in data
    assert "detected_reflexes" in data
    assert "wiki_sources" in data


def test_chat_stream_mocked(client):
    with client.stream("POST", "/chat/stream", json={"message": "hello gebo"}) as r:
        assert r.status_code == 200
        events = []
        for line in r.iter_lines():
            if line.startswith("data: "):
                events.append(line[6:])
        assert events
        import json

        done = json.loads(events[-1])
        assert done["type"] == "done"
        assert done["reply"] == "Test reply from Gebo."


def test_codex_status(client):
    r = client.get("/codex/status")
    assert r.status_code == 200
    data = r.json()
    assert "available" in data
    assert "enabled" in data


def test_wiki_status(client):
    r = client.get("/wiki/status")
    assert r.status_code == 200
    data = r.json()
    assert data["enabled"] is True
    assert data["available"] is False
    assert "auto_mode" in data


def test_wiki_search_empty_query(client):
    r = client.get("/wiki/search", params={"q": "  "})
    assert r.status_code == 400
