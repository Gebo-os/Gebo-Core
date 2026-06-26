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
    detected_reflexes: list["DetectedReflex"] = Field(default_factory=list)
    wiki_sources: list[str] = Field(default_factory=list)


class DetectedReflex(BaseModel):
    reflex_id: int
    name: str
    description: str
    trigger_pattern: str
    action_type: str
    approval_required: bool
    proposals_created: int = 0


class ReflexItem(BaseModel):
    id: int
    name: str
    description: str
    trigger_type: str
    trigger_pattern: str
    action_type: str
    approval_required: bool
    enabled: bool
    created_at: str
    last_used: Optional[str] = None


class ReflexCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_ACTION_TITLE)
    description: str = Field(max_length=MAX_ACTION_DESC)
    trigger_type: str = Field(default="keyword", max_length=32)
    trigger_pattern: str = Field(min_length=1, max_length=500)
    action_type: str = Field(max_length=64)
    approval_required: bool = True
    enabled: bool = True


class ReflexEventItem(BaseModel):
    id: int
    reflex_id: Optional[int]
    reflex_name: Optional[str] = None
    detected_at: str
    input_text: str
    proposed_action_id: Optional[int]
    result: Optional[str]


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


class AgentItem(BaseModel):
    id: str
    name: str
    category: str
    mark: str
    purpose: str
    responsibilities: list[str]
    outputs: list[str]
    activation_trigger: str
    status: str
    tier: str
