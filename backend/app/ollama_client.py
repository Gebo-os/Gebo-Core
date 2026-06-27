import json
import os
from collections.abc import AsyncIterator

import httpx

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

OLLAMA_ERROR = (
    "Gebo cannot reach Ollama. Start Ollama and make sure llama3.2:3b is installed."
)


def get_model() -> str:
    return OLLAMA_MODEL


async def get_runtime_info() -> dict:
    """Query Ollama for loaded-model info (GPU layers, etc.)."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/ps"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            models = response.json().get("models", [])
            if not models:
                return {"loaded": False, "model": OLLAMA_MODEL}
            active = models[0]
            return {
                "loaded": True,
                "model": active.get("name", OLLAMA_MODEL),
                "size_vram": active.get("size_vram"),
                "size": active.get("size"),
            }
    except Exception:
        return {"loaded": False, "model": OLLAMA_MODEL}


async def chat(system_prompt: str, user_message: str) -> str:
    parts: list[str] = []
    async for token in chat_stream(system_prompt, user_message):
        parts.append(token)
    return "".join(parts).strip()


async def chat_stream(system_prompt: str, user_message: str) -> AsyncIterator[str]:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
    except (httpx.ConnectError, httpx.TimeoutException):
        raise RuntimeError(OLLAMA_ERROR)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise RuntimeError(OLLAMA_ERROR)
        raise RuntimeError(f"Ollama error: {exc.response.status_code}")
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError(OLLAMA_ERROR)
