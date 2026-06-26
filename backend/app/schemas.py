from typing import Any, Optional

from pydantic import BaseModel, Field

MAX_MESSAGE = 8000
MAX_MEMORY = 12000
MAX_ACTION_TITLE = 200
MAX_ACTION_DESC = 2000
MAX_MEMORY_TYPE = 64


class HealthResponse(BaseModel):
    ok: bool
    app: str


class StatusResponse(BaseModel):
    app: str
    model: str
    consent: bool
    memory_count: int
    message_count: int
    proposed_action_count: int
    approved_action_count: int
    completed_action_count: int


class ConsentRequest(BaseModel):
    allowed: bool


class MemoryCreate(BaseModel):
    memory_type: str = Field(default="manual", max_length=MAX_MEMORY_TYPE)
    content: str = Field(min_length=1, max_length=MAX_MEMORY)


class MemoryItem(BaseModel):
    id: int
    created_at: str
    memory_type: str
    content: str
    source: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE)


class ProposedAction(BaseModel):
    id: int
    action_type: str
    title: str
    description: str
    status: str


class ChatResponse(BaseModel):
    reply: str
    recalled_memories: list[MemoryItem]
    proposed_actions: list[ProposedAction] = Field(default_factory=list)


class ActionPropose(BaseModel):
    action_type: str = Field(max_length=64)
    title: str = Field(min_length=1, max_length=MAX_ACTION_TITLE)
    description: str = Field(max_length=MAX_ACTION_DESC)
    payload_json: dict[str, Any] = Field(default_factory=dict)


class ActionItem(BaseModel):
    id: int
    created_at: str
    action_type: str
    title: str
    description: str
    payload_json: str
    status: str
    result_json: Optional[str] = None
