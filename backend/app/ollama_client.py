import os

import httpx

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

OLLAMA_ERROR = (
    "Gebo cannot reach Ollama. Start Ollama and make sure llama3.2:3b is installed."
)


def get_model() -> str:
    return OLLAMA_MODEL


async def chat(system_prompt: str, user_message: str) -> str:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise RuntimeError(OLLAMA_ERROR)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise RuntimeError(OLLAMA_ERROR)
        raise RuntimeError(f"Ollama error: {exc.response.status_code}")
    except Exception:
        raise RuntimeError(OLLAMA_ERROR)
