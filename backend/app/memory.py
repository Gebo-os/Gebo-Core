import re

from app import db

AUTO_KEYWORDS = [
    "remember",
    "my goal",
    "my plan",
    "i want",
    "i need",
    "gebo",
    "owner node",
    "presence",
    "memory",
    "career",
    "business",
    "app",
    "model",
    "system",
    "architecture",
]

LONG_MESSAGE_THRESHOLD = 180
RECALL_LIMIT = 8
PROMPT_MEMORY_MAX = 500


def _sanitize_for_prompt(text: str, limit: int = PROMPT_MEMORY_MAX) -> str:
    cleaned = text.replace("\r", " ").replace("\n", " ").strip()
    if len(cleaned) > limit:
        return cleaned[:limit] + "..."
    return cleaned


def _normalize(text: str) -> str:
    return text.lower().strip()


def should_auto_capture(content: str, consent: bool) -> bool:
    if not consent:
        return False
    normalized = _normalize(content)
    if len(content) > LONG_MESSAGE_THRESHOLD:
        return True
    return any(kw in normalized for kw in AUTO_KEYWORDS)


def auto_capture(content: str) -> int | None:
    if not should_auto_capture(content, db.get_consent()):
        return None
    return db.insert_memory("auto", content, "chat")


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", _normalize(text))
    return {w for w in words if len(w) > 2}


def score_memory(memory_content: str, query: str) -> int:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0
    memory_tokens = _tokenize(memory_content)
    score = len(query_tokens & memory_tokens)
    normalized_memory = _normalize(memory_content)
    for token in query_tokens:
        if token in normalized_memory:
            score += 1
    return score


def get_relevant_memories(query: str, limit: int = RECALL_LIMIT) -> list[dict]:
    all_memories = db.get_all_memories()
    if not all_memories:
        return []
    scored = [(score_memory(m["content"], query), m) for m in all_memories]
    scored.sort(key=lambda x: (-x[0], -x[1]["id"]))
    relevant = [m for s, m in scored if s > 0]
    if not relevant:
        return list(reversed(all_memories[-limit:]))
    return relevant[:limit]


def build_system_prompt(
    recalled: list[dict],
    recent_messages: list[dict],
    user_message: str,
) -> str:
    memory_block = "\n".join(
        f"- [{m['memory_type']}] {_sanitize_for_prompt(m['content'])}"
        for m in recalled
    ) or "- No relevant memories recalled."

    history_block = "\n".join(
        f"{m['role'].upper()}: {_sanitize_for_prompt(m['content'], 300)}"
        for m in recent_messages[-10:]
    ) or "No prior conversation."

    return f"""You are Gebo Core, Bb's private intelligence layer.

IDENTITY:
- Calm, direct, strategic, useful, project-focused, memory-aware, private, approval-based.
- Memory owns identity. You generate responses. You do not execute actions without approval.
- You help build: Gebo OS, Owner Node, Memory Continuity API, Presence Architecture, Dream, Mya, LockIn, Slatt Tool, Sleep, Future Presences.

RULES:
- Be concise and actionable.
- Reference recalled memory when relevant.
- If the user asks to remember, plan, summarize, or export — acknowledge and note that an action may be proposed for approval.
- Never claim you executed an action. Actions require Bb's approval.

RECALLED MEMORIES:
{memory_block}

RECENT CONVERSATION:
{history_block}

CURRENT USER MESSAGE:
{user_message}
"""
