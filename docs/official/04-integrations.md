# Integrations

## Google ecosystem

| Tool | Mode | Setup |
|------|------|-------|
| Gmail, Calendar, Chat, Maps | connector | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Gemini | connector | `GEMINI_API_KEY` |
| Firebase | connector | `FIREBASE_PROJECT_ID` + Firebase CLI |
| Docs, Meet, Keep, AI Studio, TensorFlow | learnable | Auto via knowledge collector |

## OSS & open weight

| Tool | Mode |
|------|------|
| Ollama / gebo-custom | connector (local) |
| Hugging Face, LangChain, llama.cpp, vLLM | learnable |
| Codex CLI | connector (approval-gated) |
| xAI CLI | connector (`XAI_API_KEY`) |

## Status API

```
GET /integrations/status
```

Returns `learnable` vs `connector`, `configured` vs `needs_credentials`.

## Future adapters

Connectors not yet wired to live APIs — credentials + approved actions will gate Gmail send, Calendar read, etc.

See `backend/app/integrations_registry.py` to add entries.
