"""Document intelligence — upload, parse, chunk, embed, store, retrieve."""
from __future__ import annotations

import os
import uuid
from typing import Any

from app.modules.common import resolve_status
from app.v1_clients import supabase_client

MODULE_META = {
    "id": "document_intelligence",
    "name": "Document Intelligence",
    "surface": "backend",
}

PIPELINE_STAGES = [
    "upload",
    "parse",
    "chunk",
    "embed",
    "store",
    "retrieve",
]

BUCKET_NAME = "gebo-documents"


def _owner_live() -> bool:
    return False


def _production_live() -> bool:
    return supabase_client.storage_ping()


def status() -> dict[str, Any]:
    return {
        **MODULE_META,
        "status": resolve_status(
            "document_intelligence",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
        "pipeline": PIPELINE_STAGES,
        "storage_backend": "supabase" if supabase_client.is_configured() else "unavailable",
        "bucket": BUCKET_NAME,
        "parsers": ["llamaindex", "unstructured"],
        "env_required": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "DATABASE_URL"],
        "env_optional": ["OPENAI_API_KEY"],
        "notes": "Uploads to Supabase Storage when configured.",
    }


def handle_upload_stub(
    filename: str,
    content_type: str,
    content: bytes | None = None,
) -> dict[str, Any]:
    document_id = str(uuid.uuid4())
    uploaded = False
    storage_path = None

    if supabase_client.is_configured() and content is not None:
        try:
            client = supabase_client.get_client()
            storage_path = f"{document_id}/{filename}"
            client.storage.from_(BUCKET_NAME).upload(
                storage_path,
                content,
                {"content-type": content_type},
            )
            uploaded = True
        except Exception:
            uploaded = False

    return {
        "filename": filename,
        "content_type": content_type,
        "stage": "upload",
        "document_id": document_id if uploaded else None,
        "storage_path": storage_path,
        "uploaded": uploaded,
        "status": resolve_status(
            "document_intelligence",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_parse_stub(document_id: str) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "stage": "parse",
        "status": resolve_status(
            "document_intelligence",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }


def handle_retrieve_stub(query: str, limit: int = 5) -> dict[str, Any]:
    return {
        "query": query,
        "limit": limit,
        "chunks": [],
        "stage": "retrieve",
        "status": resolve_status(
            "document_intelligence",
            production_live=_production_live(),
            owner_live=_owner_live(),
        ),
    }
