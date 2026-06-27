"""Official V1 release stack — readiness, modules, auth in owner mode."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_v1_readiness_endpoint(client):
    r = client.get("/system/v1-readiness")
    assert r.status_code == 200
    data = r.json()
    assert data["official_stack"] == "supabase_vercel_v1"
    assert "readiness_score" in data
    assert "controls" in data
    assert "wired" in data
    assert data["owner_node"] is True
    assert data["release_mode"] == "owner"


def test_v1_readiness_wired_flags(client):
    r = client.get("/system/v1-readiness")
    wired = r.json()["wired"]
    assert wired["v1_stack"] == "supabase_vercel"
    assert "auth_providers" in wired
    assert wired["auth_middleware_active"] is False


def test_modules_endpoint(client):
    r = client.get("/system/modules")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 8
    modules = data["modules"]
    assert len(modules) == 8
    ids = {m["id"] for m in modules}
    assert ids == {
        "identity_core",
        "memory_continuity",
        "presence_router",
        "ai_gateway",
        "document_intelligence",
        "security_command",
        "billing_usage",
        "admin_console",
    }
    for mod in modules:
        assert "status" in mod
        assert mod["surface"] == "backend"


def test_system_private_includes_v1_readiness(client):
    r = client.get("/system/private")
    assert r.status_code == 200
    data = r.json()
    assert "v1_readiness" in data
    assert "release_modules" in data
    assert len(data["release_modules"]) == 8
    layer_ids = [layer["id"] for layer in data["layers"]]
    assert "release_plane" in layer_ids


def test_auth_disabled_in_owner_mode(client):
    """Owner mode: protected routes remain open without JWT."""
    assert client.post("/chat", json={"message": "v1 owner mode"}).status_code == 200
    assert (
        client.post(
            "/memory",
            json={"memory_type": "core", "content": "v1 auth off"},
        ).status_code
        == 200
    )
    assert client.get("/system/v1-readiness").status_code == 200
    assert client.get("/system/modules").status_code == 200


def test_release_stack_module():
    from app import release_stack

    result = release_stack.v1_readiness()
    assert result["required_total"] >= 1
    assert isinstance(result["next_steps"], list)
    tiers = {c["release_tier"] for c in release_stack.V1_CONTROLS}
    assert "required" in tiers
    assert "recommended" in tiers
    assert "later" in tiers


def test_module_registry():
    from app.modules import MODULE_REGISTRY, all_module_statuses

    assert len(MODULE_REGISTRY) == 8
    statuses = all_module_statuses()
    assert len(statuses) == 8


def test_owner_mode_modules_active_not_scaffold(client):
    """Owner mode: local modules active; no scaffold status."""
    r = client.get("/system/modules")
    assert r.status_code == 200
    by_id = {m["id"]: m for m in r.json()["modules"]}
    for module_id in ("memory_continuity", "presence_router", "ai_gateway"):
        assert by_id[module_id]["status"] == "active"
        assert by_id[module_id]["status"] != "scaffold"
    assert by_id["identity_core"]["status"] == "active"
    for mod in r.json()["modules"]:
        assert mod["status"] in ("active", "inactive")


def test_production_mode_readiness_with_mocks(monkeypatch):
    from app import release_stack

    monkeypatch.setenv("GEBO_RELEASE_MODE", "production")

    def _all_ready(control_id: str) -> bool:
        return True

    monkeypatch.setattr(
        "app.v1_clients.health.check_control",
        _all_ready,
    )
    result = release_stack.v1_readiness()
    assert result["release_mode"] == "production"
    assert result["readiness_score"] == 100
    assert result["required_ready"] == result["required_total"]
    assert result["v1_ready"] is True


@pytest.fixture()
def auth_enabled_client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_gebo_v1_auth.db"
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_DIR", tmp_path)
    monkeypatch.setenv("GEBO_TESTING", "true")
    monkeypatch.setenv("GEBO_RELEASE_MODE", "production")
    monkeypatch.setenv("GEBO_AUTH_ENABLED", "true")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret-for-jwt")

    from app import db

    db.init_db()

    async def fake_chat(_system_prompt: str, _user_message: str) -> str:
        return "V1 auth test reply."

    monkeypatch.setattr("app.main.ollama_client.chat", fake_chat)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_supabase_auth_public_routes_open(auth_enabled_client):
    assert auth_enabled_client.get("/system/v1-readiness").status_code == 200
    assert auth_enabled_client.get("/system/modules").status_code == 200


def test_supabase_auth_mock_token_succeeds(auth_enabled_client, monkeypatch):
    monkeypatch.setattr(
        "app.auth_middleware.verify_token",
        lambda _token: ({"sub": "user-v1-123", "email": "v1@example.com"}, "supabase"),
    )
    r = auth_enabled_client.post(
        "/chat",
        json={"message": "supabase authenticated"},
        headers={"Authorization": "Bearer fake.supabase.jwt"},
    )
    assert r.status_code == 200
    assert r.json()["reply"] == "V1 auth test reply."
