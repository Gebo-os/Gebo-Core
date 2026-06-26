"""Pytest fixtures — isolated temp SQLite DB per test session."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_gebo.db"
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_DIR", tmp_path)

    from app import db

    db.init_db()

    async def fake_chat(_system_prompt: str, _user_message: str) -> str:
        return "Test reply from Gebo."

    monkeypatch.setattr("app.main.ollama_client.chat", fake_chat)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
