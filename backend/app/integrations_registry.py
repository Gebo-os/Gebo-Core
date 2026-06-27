"""Integration catalog: learnable knowledge vs connector APIs Gebo must wire."""
from __future__ import annotations

import os
from typing import Any

# learnable = Gebo ingests public docs into memory
# connector = requires OAuth/API keys; stub until configured
INTEGRATIONS: list[dict[str, Any]] = [
    {"id": "gmail", "name": "Gmail", "category": "workspace", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"], "docs": "https://developers.google.com/gmail/api"},
    {"id": "google_drive", "name": "Google Drive", "category": "workspace", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLIENT_ID"], "docs": "https://developers.google.com/drive/api"},
    {"id": "google_docs", "name": "Google Docs", "category": "workspace", "mode": "learnable", "provider": "google", "docs": "https://developers.google.com/docs/api"},
    {"id": "google_calendar", "name": "Google Calendar", "category": "workspace", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLIENT_ID"], "docs": "https://developers.google.com/calendar/api"},
    {"id": "google_meet", "name": "Google Meet", "category": "workspace", "mode": "learnable", "provider": "google", "docs": "https://developers.google.com/meet"},
    {"id": "google_chat", "name": "Google Chat", "category": "workspace", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLIENT_ID"], "docs": "https://developers.google.com/chat"},
    {"id": "google_keep", "name": "Google Keep", "category": "workspace", "mode": "learnable", "provider": "google", "docs": "https://developers.google.com/keep"},
    {"id": "gemini", "name": "Gemini", "category": "ai", "mode": "connector", "provider": "google", "env": ["GEMINI_API_KEY"], "docs": "https://ai.google.dev/gemini-api/docs"},
    {"id": "notebooklm", "name": "NotebookLM", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://notebooklm.google.com/"},
    {"id": "google_ai_studio", "name": "Google AI Studio", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://aistudio.google.com/"},
    {"id": "vertex_ai", "name": "Vertex AI", "category": "ai", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/vertex-ai/docs"},
    {"id": "jax", "name": "JAX", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://jax.readthedocs.io/en/latest/"},
    {"id": "mediapipe", "name": "MediaPipe", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://developers.google.com/mediapipe"},
    {"id": "gemma", "name": "Gemma Models", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://ai.google.dev/gemma/docs"},
    {"id": "flutter", "name": "Flutter", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://docs.flutter.dev/"},
    {"id": "dart", "name": "Dart", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://dart.dev/guides"},
    {"id": "golang", "name": "Go (Golang)", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://go.dev/doc/"},
    {"id": "bazel", "name": "Bazel", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://bazel.build/start"},
    {"id": "protobuf", "name": "Protocol Buffers", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://protobuf.dev/overview/"},
    {"id": "flatbuffers", "name": "FlatBuffers", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://google.github.io/flatbuffers/"},
    {"id": "kotlin_multiplatform", "name": "Kotlin Multiplatform", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://kotlinlang.org/docs/multiplatform.html"},
    {"id": "chrome_devtools", "name": "Chrome DevTools", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://developer.chrome.com/docs/devtools/"},
    {"id": "cloud_code", "name": "Cloud Code", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://cloud.google.com/code/docs"},
    {"id": "cloud_shell", "name": "Cloud Shell", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://cloud.google.com/shell/docs"},
    {"id": "gerrit", "name": "Gerrit", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://www.gerritcodereview.com/documentation/"},
    {"id": "firestore", "name": "Cloud Firestore", "category": "firebase", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://firebase.google.com/docs/firestore"},
    {"id": "firebase_rtdb", "name": "Firebase Realtime Database", "category": "firebase", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://firebase.google.com/docs/database"},
    {"id": "firebase_sql", "name": "Firebase SQL / Data Connect", "category": "firebase", "mode": "learnable", "provider": "google", "docs": "https://firebase.google.com/docs/data-connect"},
    {"id": "firebase_hosting", "name": "Firebase Hosting", "category": "firebase", "mode": "learnable", "provider": "google", "docs": "https://firebase.google.com/docs/hosting"},
    {"id": "crashlytics", "name": "Firebase Crashlytics", "category": "firebase", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://firebase.google.com/docs/crashlytics"},
    {"id": "fcm", "name": "Firebase Cloud Messaging", "category": "firebase", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://firebase.google.com/docs/cloud-messaging"},
    {"id": "gke", "name": "Google Kubernetes Engine", "category": "gcp", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/kubernetes-engine/docs"},
    {"id": "compute_engine", "name": "Compute Engine", "category": "gcp", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/compute/docs"},
    {"id": "cloud_run", "name": "Cloud Run", "category": "gcp", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/run/docs"},
    {"id": "cloud_functions", "name": "Cloud Functions", "category": "gcp", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/functions/docs"},
    {"id": "bigquery", "name": "BigQuery", "category": "gcp", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/bigquery/docs"},
    {"id": "artifact_registry", "name": "Artifact Registry", "category": "gcp", "mode": "learnable", "provider": "google", "docs": "https://cloud.google.com/artifact-registry/docs"},
    {"id": "lighthouse", "name": "Lighthouse", "category": "diagnostics", "mode": "learnable", "provider": "google", "docs": "https://developer.chrome.com/docs/lighthouse/overview/"},
    {"id": "search_console", "name": "Google Search Console", "category": "diagnostics", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLIENT_ID"], "docs": "https://developers.google.com/search/docs"},
    {"id": "recaptcha_enterprise", "name": "reCAPTCHA Enterprise", "category": "production", "mode": "connector", "provider": "google", "env": ["RECAPTCHA_SITE_KEY"], "docs": "https://cloud.google.com/recaptcha-enterprise/docs"},
    {"id": "identity_platform", "name": "Identity Platform", "category": "production", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://cloud.google.com/identity-platform/docs"},
    {"id": "secret_manager", "name": "Secret Manager", "category": "production", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/secret-manager/docs"},
    {"id": "model_armor", "name": "Model Armor", "category": "production", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/security/products/model-armor"},
    {"id": "cloud_armor", "name": "Cloud Armor", "category": "production", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/armor/docs"},
    {"id": "cloud_sql", "name": "Cloud SQL", "category": "production", "mode": "connector", "provider": "google", "env": ["DATABASE_URL"], "docs": "https://cloud.google.com/sql/docs"},
    {"id": "cloud_spanner", "name": "Cloud Spanner", "category": "production", "mode": "connector", "provider": "google", "env": ["SPANNER_INSTANCE"], "docs": "https://cloud.google.com/spanner/docs"},
    {"id": "cloud_storage", "name": "Cloud Storage", "category": "production", "mode": "connector", "provider": "google", "env": ["GCS_BUCKET"], "docs": "https://cloud.google.com/storage/docs"},
    {"id": "cloud_dlp", "name": "Sensitive Data Protection", "category": "production", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/dlp/docs"},
    {"id": "iap", "name": "Identity-Aware Proxy", "category": "production", "mode": "connector", "provider": "google", "env": ["GOOGLE_CLOUD_PROJECT"], "docs": "https://cloud.google.com/iap/docs"},
    {"id": "firebase", "name": "Firebase", "category": "developer", "mode": "connector", "provider": "google", "env": ["FIREBASE_PROJECT_ID"], "docs": "https://firebase.google.com/docs"},
    {"id": "tensorflow", "name": "TensorFlow", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://www.tensorflow.org/api_docs"},
    {"id": "android_studio", "name": "Android Studio", "category": "developer", "mode": "learnable", "provider": "google", "docs": "https://developer.android.com/studio/intro"},
    {"id": "google_maps", "name": "Google Maps", "category": "discovery", "mode": "connector", "provider": "google", "env": ["GOOGLE_MAPS_API_KEY"], "docs": "https://developers.google.com/maps/documentation"},
    {"id": "google_analytics", "name": "Google Analytics", "category": "business", "mode": "connector", "provider": "google", "env": ["GA_MEASUREMENT_ID"], "docs": "https://developers.google.com/analytics"},
    {"id": "ollama", "name": "Ollama (local)", "category": "ai", "mode": "connector", "provider": "local", "env": ["OLLAMA_MODEL"], "docs": "https://github.com/ollama/ollama/blob/main/docs/api.md"},
    {"id": "codex", "name": "Codex CLI", "category": "developer", "mode": "connector", "provider": "openai", "env": ["CODEX_ENABLED"], "docs": "https://github.com/openai/codex"},
    {"id": "xai_cli", "name": "xAI CLI", "category": "ai", "mode": "connector", "provider": "xai", "env": ["XAI_API_KEY"], "docs": "https://x.ai/"},
    {"id": "huggingface", "name": "Hugging Face", "category": "ai", "mode": "learnable", "provider": "oss", "docs": "https://huggingface.co/docs"},
    {"id": "langchain", "name": "LangChain", "category": "developer", "mode": "learnable", "provider": "oss", "docs": "https://python.langchain.com/docs/"},
    {"id": "llama_cpp", "name": "llama.cpp", "category": "ai", "mode": "learnable", "provider": "oss", "docs": "https://github.com/ggerganov/llama.cpp"},
    {"id": "vllm", "name": "vLLM", "category": "ai", "mode": "learnable", "provider": "oss", "docs": "https://docs.vllm.ai/"},
    {"id": "supabase", "name": "Supabase", "category": "production", "mode": "learnable", "provider": "supabase", "docs": "https://supabase.com/docs"},
    {"id": "vercel", "name": "Vercel", "category": "hosting", "mode": "learnable", "provider": "vercel", "docs": "https://vercel.com/docs"},
    {"id": "stripe", "name": "Stripe", "category": "billing", "mode": "learnable", "provider": "stripe", "docs": "https://stripe.com/docs"},
    {"id": "resend", "name": "Resend", "category": "email", "mode": "learnable", "provider": "resend", "docs": "https://resend.com/docs"},
    {"id": "sentry", "name": "Sentry", "category": "observability", "mode": "learnable", "provider": "sentry", "docs": "https://docs.sentry.io/"},
    {"id": "upstash", "name": "Upstash Redis", "category": "production", "mode": "learnable", "provider": "upstash", "docs": "https://upstash.com/docs/redis"},
    {"id": "cloudflare_turnstile", "name": "Cloudflare Turnstile", "category": "production", "mode": "learnable", "provider": "cloudflare", "docs": "https://developers.cloudflare.com/turnstile/"},
    {"id": "langfuse", "name": "Langfuse", "category": "observability", "mode": "learnable", "provider": "langfuse", "docs": "https://langfuse.com/docs"},
    {"id": "posthog", "name": "PostHog", "category": "observability", "mode": "learnable", "provider": "posthog", "docs": "https://posthog.com/docs"},
    {"id": "openai", "name": "OpenAI", "category": "ai", "mode": "learnable", "provider": "openai", "docs": "https://platform.openai.com/docs"},
    {"id": "anthropic", "name": "Anthropic", "category": "ai", "mode": "learnable", "provider": "anthropic", "docs": "https://docs.anthropic.com/"},
    {"id": "google_gemini", "name": "Google Gemini", "category": "ai", "mode": "learnable", "provider": "google", "docs": "https://ai.google.dev/gemini-api/docs"},
    {"id": "xai_grok", "name": "xAI Grok", "category": "ai", "mode": "learnable", "provider": "xai", "docs": "https://docs.x.ai/"},
    {"id": "llamaindex", "name": "LlamaIndex", "category": "ai", "mode": "learnable", "provider": "oss", "docs": "https://docs.llamaindex.ai/"},
    {"id": "unstructured", "name": "Unstructured", "category": "ai", "mode": "learnable", "provider": "oss", "docs": "https://docs.unstructured.io/"},
]


def _configured(integration: dict[str, Any]) -> bool:
    for key in integration.get("env") or []:
        if os.getenv(key, "").strip():
            return True
    return integration.get("mode") == "learnable"


def status() -> dict[str, Any]:
    items = []
    for row in INTEGRATIONS:
        items.append(
            {
                **row,
                "configured": _configured(row),
                "status": "ready" if _configured(row) else ("learnable" if row["mode"] == "learnable" else "needs_credentials"),
            }
        )
    learnable = sum(1 for i in items if i["mode"] == "learnable")
    connectors = sum(1 for i in items if i["mode"] == "connector")
    ready = sum(1 for i in items if i["configured"])
    return {
        "total": len(items),
        "learnable": learnable,
        "connectors": connectors,
        "ready": ready,
        "items": items,
    }
