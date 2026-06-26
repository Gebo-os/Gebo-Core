import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "gebo.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                action_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT
            );

            CREATE TABLE IF NOT EXISTS reflexes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                trigger_pattern TEXT NOT NULL,
                action_type TEXT NOT NULL,
                approval_required INTEGER NOT NULL DEFAULT 1,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reflex_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reflex_id INTEGER,
                detected_at TEXT NOT NULL,
                input_text TEXT NOT NULL,
                proposed_action_id INTEGER,
                result TEXT
            );
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("consent", "false"),
        )
        conn.commit()
    from app.reflexes import seed_default_reflexes

    seed_default_reflexes()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()


def get_consent() -> bool:
    return get_setting("consent", "false").lower() == "true"


def insert_memory(memory_type: str, content: str, source: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO memories (created_at, memory_type, content, source)
            VALUES (?, ?, ?, ?)
            """,
            (utc_now(), memory_type, content, source),
        )
        conn.commit()
        return cur.lastrowid


def update_memory(memory_id: int, content: str, source: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE memories
            SET content = ?, source = ?, created_at = ?
            WHERE id = ?
            """,
            (content, source, utc_now(), memory_id),
        )
        conn.commit()


def find_project_memory_id(repo_key: str) -> int | None:
    """Find existing project memory by repo URL or local path marker."""
    key = repo_key.rstrip("/").rstrip(".git")
    if not key:
        return None
    markers = (f"URL: {key}", f"Local path: {key}")
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, content FROM memories
            WHERE memory_type = 'project'
            ORDER BY id DESC
            """
        ).fetchall()
        for row in rows:
            content = row["content"] or ""
            if any(m in content for m in markers):
                return row["id"]
            if key in content:
                return row["id"]
    return None


def upsert_project_memory(content: str, source: str, repo_key: str) -> tuple[int, bool]:
    """Return (memory_id, created). created=False means updated in place."""
    existing = find_project_memory_id(repo_key)
    if existing is not None:
        update_memory(existing, content, source)
        return existing, False
    return insert_memory("project", content, source), True


def get_memories(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, memory_type, content, source
            FROM memories
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_memories() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, memory_type, content, source
            FROM memories
            ORDER BY id ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def count_memories() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM memories").fetchone()
        return row["c"]


def insert_message(role: str, content: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO messages (created_at, role, content)
            VALUES (?, ?, ?)
            """,
            (utc_now(), role, content),
        )
        conn.commit()
        return cur.lastrowid


def get_recent_messages(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, role, content
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


def get_all_messages() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, role, content
            FROM messages
            ORDER BY id ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def count_messages() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()
        return row["c"]


def insert_action(
    action_type: str,
    title: str,
    description: str,
    payload: dict,
    status: str = "proposed",
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO actions
            (created_at, action_type, title, description, payload_json, status, result_json)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                utc_now(),
                action_type,
                title,
                description,
                json.dumps(payload),
                status,
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_action(action_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM actions WHERE id = ?", (action_id,)
        ).fetchone()
        return dict(row) if row else None


def get_actions() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM actions ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def update_action_status(action_id: int, status: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE actions SET status = ? WHERE id = ?",
            (status, action_id),
        )
        conn.commit()
        return cur.rowcount > 0


def claim_approved_action(action_id: int) -> dict | None:
    """Atomically move approved -> running claim; returns action or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM actions WHERE id = ? AND status = 'approved'",
            (action_id,),
        ).fetchone()
        if not row:
            return None
        cur = conn.execute(
            "UPDATE actions SET status = 'running' WHERE id = ? AND status = 'approved'",
            (action_id,),
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
        return dict(row)


def update_action_result(action_id: int, status: str, result: dict) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE actions SET status = ?, result_json = ? WHERE id = ?",
            (status, json.dumps(result), action_id),
        )
        conn.commit()
        return cur.rowcount > 0


def count_actions_by_status(status: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM actions WHERE status = ?", (status,)
        ).fetchone()
        return row["c"]


def get_all_settings() -> dict[str, str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}


def count_reflexes() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM reflexes").fetchone()
        return row["c"]


def insert_reflex(
    name: str,
    description: str,
    trigger_type: str,
    trigger_pattern: str,
    action_type: str,
    approval_required: bool = True,
    enabled: bool = True,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO reflexes
            (name, description, trigger_type, trigger_pattern, action_type,
             approval_required, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                trigger_type,
                trigger_pattern,
                action_type,
                1 if approval_required else 0,
                1 if enabled else 0,
                utc_now(),
            ),
        )
        conn.commit()
        return cur.lastrowid


def get_reflex(reflex_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM reflexes WHERE id = ?", (reflex_id,)
        ).fetchone()
        return dict(row) if row else None


def get_reflexes(enabled_only: bool = False) -> list[dict]:
    with get_connection() as conn:
        if enabled_only:
            rows = conn.execute(
                "SELECT * FROM reflexes WHERE enabled = 1 ORDER BY id ASC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM reflexes ORDER BY id ASC"
            ).fetchall()
        return [dict(r) for r in rows]


def toggle_reflex(reflex_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM reflexes WHERE id = ?", (reflex_id,)
        ).fetchone()
        if not row:
            return None
        new_enabled = 0 if row["enabled"] else 1
        conn.execute(
            "UPDATE reflexes SET enabled = ? WHERE id = ?",
            (new_enabled, reflex_id),
        )
        conn.commit()
        return get_reflex(reflex_id)


def get_reflex_last_used(reflex_id: int) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT MAX(detected_at) AS last_used
            FROM reflex_events WHERE reflex_id = ?
            """,
            (reflex_id,),
        ).fetchone()
        return row["last_used"] if row and row["last_used"] else None


def insert_reflex_event(
    reflex_id: int,
    input_text: str,
    proposed_action_id: int | None,
    result: str,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO reflex_events
            (reflex_id, detected_at, input_text, proposed_action_id, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (reflex_id, utc_now(), input_text, proposed_action_id, result),
        )
        conn.commit()
        return cur.lastrowid


def get_reflex_events(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT e.*, r.name AS reflex_name
            FROM reflex_events e
            LEFT JOIN reflexes r ON r.id = e.reflex_id
            ORDER BY e.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
