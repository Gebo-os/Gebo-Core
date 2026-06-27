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
    agent_runtime_healthy: bool = True


class StatusResponse(BaseModel):
    app: str
    model: str
    consent: bool
    memory_count: int
    message_count: int
    proposed_action_count: int
    approved_action_count: int
    completed_action_count: int
    ollama_runtime: dict[str, Any] | None = None


class ConsentRequest(BaseModel):
    allowed: bool


class NetworkSettingsResponse(BaseModel):
    internet_access: bool
    cors_mode: str
    backend_url: str
    frontend_url: str
    bind_host: str
    allowed_origins: list[str]


class NetworkSettingsRequest(BaseModel):
    internet_access: bool


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


class ScoreActionRequest(BaseModel):
    action_id: int
    mission_value: int = Field(ge=1, le=10)
    speed_score: int = Field(ge=1, le=10)
    risk_score: int = Field(ge=1, le=10)
    approval_score: int = Field(ge=1, le=10)
    memory_impact: int = Field(ge=1, le=10)
    product_impact: int = Field(ge=1, le=10)
    money_impact: int = Field(ge=1, le=10)
    notes: str = Field(default="", max_length=MAX_ACTION_DESC)


class SuggestUpgradeRequest(BaseModel):
    upgrade_type: str = Field(max_length=64)
    title: str = Field(min_length=1, max_length=MAX_ACTION_TITLE)
    description: str = Field(max_length=MAX_ACTION_DESC)
    reason: str = Field(max_length=MAX_ACTION_DESC)


class EvolutionEventItem(BaseModel):
    id: int
    created_at: str
    source_type: str
    source_id: Optional[int]
    lesson: str
    score: int
    recommended_upgrade: Optional[str]
    status: str


class AutonomyScoreItem(BaseModel):
    id: int
    created_at: str
    action_id: Optional[int]
    mission_value: int
    speed_score: int
    risk_score: int
    approval_score: int
    memory_impact: int
    product_impact: int
    money_impact: int
    total_score: int
    notes: Optional[str]


class UpgradeSuggestionItem(BaseModel):
    id: int
    created_at: str
    upgrade_type: str
    title: str
    description: str
    reason: str
    status: str
    proposed_action_id: Optional[int]


class EvolutionStatusResponse(BaseModel):
    average_autonomy_score: Optional[float]
    total_evolution_events: int
    proposed_upgrades: int
    approved_upgrades: int
    completed_upgrades: int
    rejected_upgrades: int
    latest_lesson: Optional[str]
    top_recommended_upgrade: Optional[UpgradeSuggestionItem] = None


class AgentRuntimeAgentItem(BaseModel):
    agent_id: str
    name: str
    category: str
    status: str
    message: str
    cycles: int
    last_tick: Optional[str]
    tier: str
    registry_status: str


class CodexLaneStatus(BaseModel):
    available: bool
    enabled: bool
    version: Optional[str]
    status: str
    message: str
    cycles: int
    last_tick: Optional[str]
    parallel_with_agents: bool
    last_audit_ok: Optional[bool] = None


class AgentRuntimeStatusResponse(BaseModel):
    running: bool
    started_at: Optional[str]
    tick_interval_sec: int
    active_agents: int
    total_registry: int
    healthy: bool
    parallel_workers: int = 12
    cycle_count: int = 0
    codex_lane: Optional[CodexLaneStatus] = None
    agents: list[AgentRuntimeAgentItem]


class IntegrateBootstrapResponse(BaseModel):
    """Single-call payload for Living Console and future consumer apps."""

    version: str
    app: str
    health: HealthResponse
    status: StatusResponse
    network: NetworkSettingsResponse
    codex: dict[str, Any]
    wiki: dict[str, Any]
    agent_runtime: AgentRuntimeStatusResponse
    capabilities: dict[str, Any]
