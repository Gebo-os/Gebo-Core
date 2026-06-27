"""Production security wiring — auth, model armor, readiness flags."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_auth_disabled_endpoints_work(client):
    """Owner mode / auth off: protected routes remain open."""
    assert client.post("/chat", json={"message": "hello"}).status_code == 200
    assert (
        client.post(
            "/memory",
            json={"memory_type": "core", "content": "auth off test"},
        ).status_code
        == 200
    )
    assert client.get("/health").status_code == 200
    assert client.get("/system/production-readiness").status_code == 200


def test_production_readiness_wired_flags(client):
    r = client.get("/system/production-readiness")
    assert r.status_code == 200
    data = r.json()
    assert "wired" in data
    wired = data["wired"]
    assert "auth_middleware_active" in wired
    assert "secrets_loader_active" in wired
    assert "model_armor_active" in wired
    assert wired["recaptcha_helper_available"] is True
    assert wired["auth_middleware_active"] is False
    assert wired["model_armor_active"] is False


def test_model_armor_passthrough_when_not_configured(client):
    r = client.post("/chat", json={"message": "model armor passthrough"})
    assert r.status_code == 200
    assert r.json()["reply"] == "Test reply from Gebo."


@pytest.fixture()
def auth_enabled_client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_gebo_auth.db"
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_DIR", tmp_path)
    monkeypatch.setenv("GEBO_TESTING", "true")
    monkeypatch.setenv("GEBO_RELEASE_MODE", "production")
    monkeypatch.setenv("GEBO_AUTH_ENABLED", "true")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "test-project")

    from app import db

    db.init_db()

    async def fake_chat(_system_prompt: str, _user_message: str) -> str:
        return "Auth test reply."

    monkeypatch.setattr("app.main.ollama_client.chat", fake_chat)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_auth_enabled_401_without_token(auth_enabled_client):
    r = auth_enabled_client.post("/chat", json={"message": "needs token"})
    assert r.status_code == 401
    assert "token" in r.json()["detail"].lower()


def test_auth_enabled_public_routes_open(auth_enabled_client):
    assert auth_enabled_client.get("/health").status_code == 200
    assert auth_enabled_client.get("/status").status_code == 200
    assert auth_enabled_client.get("/integrate/bootstrap").status_code == 200
    assert (
        auth_enabled_client.get("/system/production-readiness").status_code == 200
    )
    assert auth_enabled_client.get("/system/v1-readiness").status_code == 200


def test_auth_enabled_mock_token_succeeds(auth_enabled_client, monkeypatch):
    monkeypatch.setattr(
        "app.auth_middleware.verify_token",
        lambda _token: ({"sub": "user-123", "email": "test@example.com"}, "firebase"),
    )
    r = auth_enabled_client.post(
        "/chat",
        json={"message": "authenticated"},
        headers={"Authorization": "Bearer fake.jwt.token"},
    )
    assert r.status_code == 200
    assert r.json()["reply"] == "Auth test reply."


def test_auth_enabled_memory_requires_token(auth_enabled_client):
    r = auth_enabled_client.post(
        "/memory",
        json={"memory_type": "core", "content": "blocked"},
    )
    assert r.status_code == 401


def test_model_armor_module_passthrough():
    from app import model_armor
    import asyncio

    async def run():
        inp = await model_armor.screen_input("hello")
        out = await model_armor.screen_output("world")
        return inp, out

    inp, out = asyncio.run(run())
    assert inp.blocked is False
    assert inp.text == "hello"
    assert out.blocked is False
    assert out.text == "world"


def test_secrets_loader_skips_owner_mode(monkeypatch):
    from app import secrets_loader

    monkeypatch.setenv("GEBO_RELEASE_MODE", "owner")
    result = secrets_loader.load_secrets_from_gcp()
    assert result["loaded"] is False
    assert result["reason"] == "owner_mode"


def test_recaptcha_not_configured():
    from app import recaptcha

    result = recaptcha.verify_recaptcha_token("token")
    assert result["ok"] is False
    assert result["reason"] == "not_configured"
