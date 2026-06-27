import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.responses import Response

load_dotenv()

from app import (
    agent_runtime,
    auth_middleware,
    autonomy,
    cli_registry,
    codex_client,
    db,
    evolution,
    gebo_system,
    integrate,
    integrations_registry,
    knowledge_collector,
    learning_pipeline,
    memory,
    model_armor,
    ollama_client,
    production_security,
    reflexes,
    release_stack,
    secrets_loader,
    wiki_client,
)
from app.modules import all_module_statuses
from app.modules import billing_usage, identity_core, security_command
from app.v1_clients import health as v1_health
from app.v1_clients import upstash_client
from app.network_utils import get_lan_ip
from app.schemas import (
    ActionItem,
    ActionPropose,
    AgentRuntimeStatusResponse,
    AutonomyScoreItem,
    ChatRequest,
    ChatResponse,
    ConsentRequest,
    DetectedReflex,
    EvolutionEventItem,
    EvolutionStatusResponse,
    HealthResponse,
    IntegrateBootstrapResponse,
    MemoryCreate,
    MemoryItem,
    NetworkSettingsRequest,
    NetworkSettingsResponse,
    ProposedAction,
    ReflexCreate,
    ReflexEventItem,
    ReflexItem,
    ScoreActionRequest,
    StatusResponse,
    SuggestUpgradeRequest,
    UpgradeSuggestionItem,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    secrets_loader.load_secrets_from_gcp()
    db.init_db()
    try:
        v1_health.warmup()
    except Exception:
        pass
    agent_runtime.start()
    yield
    agent_runtime.stop()


app = FastAPI(title="Gebo Core Private", lifespan=lifespan)

DEFAULT_LOCALHOST_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

BIND_HOST = os.getenv("GEBO_BIND_HOST", "0.0.0.0")
BACKEND_PORT = os.getenv("GEBO_BACKEND_PORT", "8000")
FRONTEND_PORT = os.getenv("GEBO_FRONTEND_PORT", "3000")


def _env_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw == "*":
        return ["*"]
    items = [o.strip() for o in raw.split(",") if o.strip()]
    return items or DEFAULT_LOCALHOST_ORIGINS


def _network_settings_payload() -> dict:
    internet = db.get_internet_access()
    env_origins = _env_cors_origins()
    if internet:
        cors_mode = "open"
        allowed = ["*"]
    else:
        cors_mode = "localhost"
        allowed = (
            env_origins
            if env_origins != ["*"]
            else DEFAULT_LOCALHOST_ORIGINS
        )
    env_backend = os.getenv("GEBO_BACKEND_URL")
    env_frontend = os.getenv("GEBO_FRONTEND_URL")
    bind_all = BIND_HOST in ("0.0.0.0", "::")

    def _is_localhost_url(url: str | None) -> bool:
        if not url:
            return True
        lowered = url.lower()
        return "127.0.0.1" in lowered or "localhost" in lowered

    use_lan_urls = (bind_all or internet) and (
        (not env_backend and not env_frontend)
        or (_is_localhost_url(env_backend) and _is_localhost_url(env_frontend))
    )
    if use_lan_urls:
        lan_ip = get_lan_ip()
        if lan_ip:
            backend_url = f"http://{lan_ip}:{BACKEND_PORT}"
            frontend_url = f"http://{lan_ip}:{FRONTEND_PORT}"
        else:
            backend_url = f"http://127.0.0.1:{BACKEND_PORT}"
            frontend_url = f"http://localhost:{FRONTEND_PORT}"
    else:
        backend_url = env_backend or f"http://127.0.0.1:{BACKEND_PORT}"
        frontend_url = env_frontend or f"http://localhost:{FRONTEND_PORT}"
    return {
        "internet_access": internet,
        "cors_mode": cors_mode,
        "backend_url": backend_url,
        "frontend_url": frontend_url,
        "bind_host": BIND_HOST,
        "allowed_origins": allowed,
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=_env_cors_origins() if _env_cors_origins() != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def firebase_auth_gate(request: Request, call_next):
    return await auth_middleware.auth_middleware(request, call_next)


@app.middleware("http")
async def upstash_rate_limit_gate(request: Request, call_next):
    """Lightweight rate limit on protected routes when Upstash is configured."""
    if not upstash_client.is_configured():
        return await call_next(request)
    if not auth_middleware.is_protected_route(request.url.path, request.method):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    identifier = f"{client_ip}:{request.url.path}"
    result = upstash_client.check_rate_limit(identifier, limit=120, window_sec=60)
    if not result.get("allowed", True):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )
    return await call_next(request)


@app.middleware("http")
async def dynamic_open_network_cors(request: Request, call_next):
    """When internet access is on, allow any origin (full network access)."""
    if request.method == "OPTIONS" and db.get_internet_access():
        origin = request.headers.get("origin", "*")
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400",
            },
        )
    response = await call_next(request)
    if db.get_internet_access():
        origin = request.headers.get("origin")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.get("/health", response_model=HealthResponse)
def health():
    runtime = agent_runtime.get_runtime_status()
    return HealthResponse(
        ok=True,
        app="Gebo Core Private",
        agent_runtime_healthy=runtime["healthy"],
    )


@app.get("/status", response_model=StatusResponse)
async def status():
    ollama_runtime = await ollama_client.get_runtime_info()
    return StatusResponse(
        app="Gebo Core Private",
        model=ollama_client.get_model(),
        consent=db.get_consent(),
        memory_count=db.count_memories(),
        message_count=db.count_messages(),
        proposed_action_count=db.count_actions_by_status("proposed"),
        approved_action_count=db.count_actions_by_status("approved"),
        completed_action_count=db.count_actions_by_status("completed"),
        ollama_runtime=ollama_runtime,
    )


@app.get("/integrate/bootstrap", response_model=IntegrateBootstrapResponse)
def integrate_bootstrap():
    """One-call system snapshot for the Living Console and consumer apps."""
    payload = integrate.build_bootstrap()
    payload["network"] = _network_settings_payload()
    return IntegrateBootstrapResponse(**payload)


@app.post("/settings/consent")
def set_consent(body: ConsentRequest):
    db.set_setting("consent", "true" if body.allowed else "false")
    return {"consent": db.get_consent()}


@app.get("/settings/network", response_model=NetworkSettingsResponse)
def get_network_settings():
    return NetworkSettingsResponse(**_network_settings_payload())


@app.post("/settings/network", response_model=NetworkSettingsResponse)
def set_network_settings(body: NetworkSettingsRequest):
    db.set_internet_access(body.internet_access)
    return NetworkSettingsResponse(**_network_settings_payload())


@app.post("/memory")
def create_memory(body: MemoryCreate):
    memory_id = db.insert_memory(body.memory_type, body.content, "manual_api")
    return {"id": memory_id, "ok": True}


@app.get("/memory", response_model=list[MemoryItem])
def list_memories():
    return db.get_memories(100)


@app.get("/memory/export")
def export_memory():
    export_data = {
        "memories": db.get_all_memories(),
        "messages": db.get_all_messages(),
        "settings": db.get_all_settings(),
        "actions": db.get_actions(),
        "reflexes": db.get_reflexes(),
        "reflex_events": db.get_reflex_events(500),
        "evolution_events": db.get_evolution_events(500),
        "autonomy_scores": db.get_autonomy_scores(500),
        "upgrade_suggestions": db.get_upgrade_suggestions(limit=500),
    }
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="gebo-export.json"'
        },
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    user_message, consent, recalled, wiki_results, system_prompt = await _prepare_chat(
        body
    )
    try:
        reply = await _generate_chat_reply(system_prompt, user_message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return await _finalize_chat(
        user_message, consent, recalled, wiki_results, reply
    )


@app.post("/chat/stream")
async def chat_stream_endpoint(body: ChatRequest):
    user_message, consent, recalled, wiki_results, system_prompt = await _prepare_chat(
        body
    )

    async def event_generator():
        parts: list[str] = []
        try:
            use_gateway = os.getenv("GEBO_USE_AI_GATEWAY", "false").lower() in (
                "1",
                "true",
                "yes",
            )
            if use_gateway:
                reply = await _generate_chat_reply(system_prompt, user_message)
                parts.append(reply)
                yield f"data: {json.dumps({'type': 'token', 'content': reply})}\n\n"
            else:
                async for token in ollama_client.chat_stream(
                    system_prompt, user_message
                ):
                    parts.append(token)
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"
            return

        reply = "".join(parts).strip()
        response = await _finalize_chat(
            user_message, consent, recalled, wiki_results, reply
        )
        yield f"data: {json.dumps({'type': 'done', **response.model_dump()})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _prepare_chat(body: ChatRequest):
    user_message = body.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    input_screen = await model_armor.screen_input(user_message)
    if input_screen.blocked:
        raise HTTPException(
            status_code=400,
            detail=input_screen.reason or "Input blocked by Model Armor",
        )
    user_message = input_screen.text

    db.insert_message("user", user_message)
    consent = db.get_consent()

    memory.auto_capture(user_message)
    autonomy.handle_remember_direct(user_message, consent)

    recalled, has_match = memory.recall_for_chat(user_message)
    recent = db.get_recent_messages(20)

    wiki_results: list[dict] = []
    if wiki_client.is_enabled() and wiki_client.is_available():
        consult = wiki_client.WIKI_AUTO == "always" or (
            wiki_client.WIKI_AUTO == "nocontext" and not has_match
        )
        if consult:
            wiki_results = await run_in_threadpool(
                wiki_client.search, user_message
            )

    system_prompt = memory.build_system_prompt(
        recalled, recent, user_message, wiki_results
    )
    return user_message, consent, recalled, wiki_results, system_prompt


async def _generate_chat_reply(system_prompt: str, user_message: str) -> str:
    if os.getenv("GEBO_USE_AI_GATEWAY", "false").lower() in ("1", "true", "yes"):
        from app.modules import ai_gateway

        gateway_result = await ai_gateway.route_chat(system_prompt, user_message)
        return gateway_result.get("reply") or ""
    return await ollama_client.chat(system_prompt, user_message)


async def _finalize_chat(
    user_message: str,
    consent: bool,
    recalled: list[dict],
    wiki_results: list[dict],
    reply: str,
) -> ChatResponse:
    output_screen = await model_armor.screen_output(reply)
    if output_screen.blocked:
        reply = "Response withheld by safety screening."
    else:
        reply = output_screen.text

    db.insert_message("assistant", reply)

    proposed_actions: list[ProposedAction] = []
    existing_types: set[str] = set()

    intents = autonomy.detect_action_intents(user_message, consent)
    for intent in intents:
        action_id = db.insert_action(
            intent["action_type"],
            intent["title"],
            intent["description"],
            intent["payload_json"],
            "proposed",
        )
        existing_types.add(intent["action_type"])
        proposed_actions.append(
            ProposedAction(
                id=action_id,
                action_type=intent["action_type"],
                title=intent["title"],
                description=intent["description"],
                status="proposed",
            )
        )

    detected_reflex_raw, reflex_proposals = reflexes.detect_and_propose(
        user_message, existing_types
    )
    for rp in reflex_proposals:
        proposed_actions.append(
            ProposedAction(
                id=rp["id"],
                action_type=rp["action_type"],
                title=rp["title"],
                description=rp["description"],
                status=rp["status"],
            )
        )

    detected_reflexes = [DetectedReflex(**d) for d in detected_reflex_raw]

    return ChatResponse(
        reply=reply,
        recalled_memories=[MemoryItem(**m) for m in recalled],
        proposed_actions=proposed_actions,
        detected_reflexes=detected_reflexes,
        wiki_sources=[r["title"] for r in wiki_results],
    )


@app.get("/actions", response_model=list[ActionItem])
def list_actions():
    return [
        ActionItem(
            id=a["id"],
            created_at=a["created_at"],
            action_type=a["action_type"],
            title=a["title"],
            description=a["description"],
            payload_json=a["payload_json"],
            status=a["status"],
            result_json=a.get("result_json"),
        )
        for a in db.get_actions()
    ]


@app.post("/actions/propose")
def propose_action(body: ActionPropose):
    if not autonomy.is_valid_action_type(body.action_type):
        raise HTTPException(status_code=400, detail="Invalid action type")
    action_id = db.insert_action(
        body.action_type,
        body.title,
        body.description,
        body.payload_json,
        "proposed",
    )
    return {"id": action_id, "status": "proposed"}


@app.post("/actions/{action_id}/approve")
def approve_action(action_id: int):
    action = db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action["status"] != "proposed":
        raise HTTPException(status_code=400, detail="Only proposed actions can be approved")
    db.update_action_status(action_id, "approved")
    return {"id": action_id, "status": "approved"}


@app.post("/actions/{action_id}/reject")
def reject_action(action_id: int):
    action = db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action["status"] not in ("proposed", "approved"):
        raise HTTPException(status_code=400, detail="Action cannot be rejected")
    db.update_action_status(action_id, "rejected")
    return {"id": action_id, "status": "rejected"}


@app.get("/codex/status")
def codex_status():
    return codex_client.status()


@app.get("/wiki/status")
def wiki_status():
    return wiki_client.status()


@app.get("/wiki/search")
def wiki_search(q: str, limit: int = 3):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return {"query": q, "results": wiki_client.search(q, limit)}


@app.get("/reflexes", response_model=list[ReflexItem])
def list_reflexes():
    items: list[ReflexItem] = []
    for r in db.get_reflexes():
        items.append(
            ReflexItem(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                trigger_type=r["trigger_type"],
                trigger_pattern=r["trigger_pattern"],
                action_type=r["action_type"],
                approval_required=bool(r["approval_required"]),
                enabled=bool(r["enabled"]),
                created_at=r["created_at"],
                last_used=db.get_reflex_last_used(r["id"]),
            )
        )
    return items


@app.post("/reflexes", response_model=ReflexItem)
def create_reflex(body: ReflexCreate):
    if not autonomy.is_valid_action_type(body.action_type):
        raise HTTPException(status_code=400, detail="Invalid action type")
    reflex_id = db.insert_reflex(
        name=body.name,
        description=body.description,
        trigger_type=body.trigger_type,
        trigger_pattern=body.trigger_pattern,
        action_type=body.action_type,
        approval_required=body.approval_required,
        enabled=body.enabled,
    )
    r = db.get_reflex(reflex_id)
    assert r is not None
    return ReflexItem(
        id=r["id"],
        name=r["name"],
        description=r["description"],
        trigger_type=r["trigger_type"],
        trigger_pattern=r["trigger_pattern"],
        action_type=r["action_type"],
        approval_required=bool(r["approval_required"]),
        enabled=bool(r["enabled"]),
        created_at=r["created_at"],
        last_used=None,
    )


@app.post("/reflexes/{reflex_id}/toggle", response_model=ReflexItem)
def toggle_reflex_endpoint(reflex_id: int):
    updated = db.toggle_reflex(reflex_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Reflex not found")
    return ReflexItem(
        id=updated["id"],
        name=updated["name"],
        description=updated["description"],
        trigger_type=updated["trigger_type"],
        trigger_pattern=updated["trigger_pattern"],
        action_type=updated["action_type"],
        approval_required=bool(updated["approval_required"]),
        enabled=bool(updated["enabled"]),
        created_at=updated["created_at"],
        last_used=db.get_reflex_last_used(updated["id"]),
    )


@app.get("/reflex-events", response_model=list[ReflexEventItem])
def list_reflex_events(limit: int = 100):
    return [
        ReflexEventItem(
            id=e["id"],
            reflex_id=e.get("reflex_id"),
            reflex_name=e.get("reflex_name"),
            detected_at=e["detected_at"],
            input_text=e["input_text"],
            proposed_action_id=e.get("proposed_action_id"),
            result=e.get("result"),
        )
        for e in db.get_reflex_events(limit)
    ]


@app.get("/agents/runtime/status", response_model=AgentRuntimeStatusResponse)
def agents_runtime_status():
    """Internal ops — agent heartbeat supervisor (not public agent UI)."""
    data = agent_runtime.get_runtime_status()
    return AgentRuntimeStatusResponse(**data)


@app.get("/evolution/status", response_model=EvolutionStatusResponse)
def evolution_status():
    data = evolution.get_status()
    top = data.get("top_recommended_upgrade")
    top_item = UpgradeSuggestionItem(**top) if top else None
    return EvolutionStatusResponse(
        average_autonomy_score=data["average_autonomy_score"],
        total_evolution_events=data["total_evolution_events"],
        proposed_upgrades=data["proposed_upgrades"],
        approved_upgrades=data["approved_upgrades"],
        completed_upgrades=data["completed_upgrades"],
        rejected_upgrades=data["rejected_upgrades"],
        latest_lesson=data["latest_lesson"],
        top_recommended_upgrade=top_item,
    )


@app.get("/evolution/events", response_model=list[EvolutionEventItem])
def list_evolution_events(limit: int = 100):
    return [EvolutionEventItem(**e) for e in db.get_evolution_events(limit)]


@app.get("/evolution/scores", response_model=list[AutonomyScoreItem])
def list_autonomy_scores(limit: int = 100):
    return [AutonomyScoreItem(**s) for s in db.get_autonomy_scores(limit)]


@app.get("/evolution/upgrades", response_model=list[UpgradeSuggestionItem])
def list_upgrade_suggestions(status: str | None = None, limit: int = 100):
    return [
        UpgradeSuggestionItem(**u)
        for u in db.get_upgrade_suggestions(status=status, limit=limit)
    ]


@app.post("/evolution/score-action")
def score_action_endpoint(body: ScoreActionRequest):
    try:
        return evolution.score_action(
            action_id=body.action_id,
            mission_value=body.mission_value,
            speed_score=body.speed_score,
            risk_score=body.risk_score,
            approval_score=body.approval_score,
            memory_impact=body.memory_impact,
            product_impact=body.product_impact,
            money_impact=body.money_impact,
            notes=body.notes or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/evolution/suggest-upgrade")
def suggest_upgrade_endpoint(body: SuggestUpgradeRequest):
    try:
        return evolution.suggest_upgrade(
            upgrade_type=body.upgrade_type,
            title=body.title,
            description=body.description,
            reason=body.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/evolution/upgrades/{upgrade_id}/approve")
def approve_upgrade_endpoint(upgrade_id: int):
    try:
        return evolution.approve_upgrade(upgrade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/evolution/upgrades/{upgrade_id}/reject")
def reject_upgrade_endpoint(upgrade_id: int):
    try:
        return evolution.reject_upgrade(upgrade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/integrations/status")
def integrations_status():
    return integrations_registry.status()


@app.get("/cli/status")
def cli_status():
    return cli_registry.status()


@app.get("/knowledge/status")
def knowledge_status():
    return knowledge_collector.status()


@app.post("/knowledge/collect")
def knowledge_collect():
    return knowledge_collector.run_full_collection()


@app.post("/knowledge/web-collect")
def knowledge_web_collect():
    if not db.get_internet_access():
        raise HTTPException(
            status_code=403,
            detail="Enable internet access in Settings to fetch web knowledge",
        )
    return knowledge_collector.run_web_collection()


@app.post("/learning/cycle")
def learning_cycle():
    return learning_pipeline.run_learning_cycle()


@app.get("/system/private")
def system_private():
    """Backend-only Gebo system snapshot — integrations, knowledge, manifest."""
    return gebo_system.private_status()


@app.post("/system/build")
def system_build():
    """Private full build: collect docs, cache locally, ingest memory, update manifest."""
    return gebo_system.build_system()


@app.get("/system/production-readiness")
def system_production_readiness():
    """Production release checklist — auth, persistence, encryption, web defense."""
    return production_security.readiness()


@app.get("/system/v1-readiness")
def system_v1_readiness():
    """Official V1 release checklist — Supabase + Vercel stack."""
    return release_stack.v1_readiness()


@app.get("/system/modules")
def system_modules():
    """Native Gebo V1 backend module statuses."""
    return {"modules": all_module_statuses(), "count": len(all_module_statuses())}


@app.post("/v1/security/verify-turnstile")
async def v1_verify_turnstile(request: Request):
    body = await request.json()
    token = (body or {}).get("token", "")
    remote_ip = request.client.host if request.client else None
    return security_command.verify_turnstile(token, remote_ip)


@app.get("/v1/billing/plans")
def v1_billing_plans():
    return billing_usage.list_plans()


@app.get("/v1/identity/owner-status")
def v1_identity_owner_status():
    return identity_core.get_owner_status()


@app.post("/actions/{action_id}/run")
def run_action_endpoint(action_id: int):
    action = db.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    if action["status"] != "approved":
        raise HTTPException(
            status_code=400,
            detail="Action must be approved before running",
        )
    try:
        result = autonomy.run_action(action_id)
        if result.get("status") == "running":
            return {"id": action_id, "status": "running", "result": result}
        status = "completed" if result.get("ok", True) else "failed"
        return {"id": action_id, "status": status, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
