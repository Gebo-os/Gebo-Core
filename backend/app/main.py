import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from app import autonomy, db, memory, ollama_client
from app.schemas import (
    ActionItem,
    ActionPropose,
    ChatRequest,
    ChatResponse,
    ConsentRequest,
    HealthResponse,
    MemoryCreate,
    MemoryItem,
    ProposedAction,
    StatusResponse,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Gebo Core Private", lifespan=lifespan)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(ok=True, app="Gebo Core Private")


@app.get("/status", response_model=StatusResponse)
def status():
    return StatusResponse(
        app="Gebo Core Private",
        model=ollama_client.get_model(),
        consent=db.get_consent(),
        memory_count=db.count_memories(),
        message_count=db.count_messages(),
        proposed_action_count=db.count_actions_by_status("proposed"),
        approved_action_count=db.count_actions_by_status("approved"),
        completed_action_count=db.count_actions_by_status("completed"),
    )


@app.post("/settings/consent")
def set_consent(body: ConsentRequest):
    db.set_setting("consent", "true" if body.allowed else "false")
    return {"consent": db.get_consent()}


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
    }
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="gebo-export.json"'
        },
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    user_message = body.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    db.insert_message("user", user_message)
    consent = db.get_consent()

    memory.auto_capture(user_message)
    autonomy.handle_remember_direct(user_message, consent)

    recalled = memory.get_relevant_memories(user_message)
    recent = db.get_recent_messages(20)
    system_prompt = memory.build_system_prompt(recalled, recent, user_message)

    try:
        reply = await ollama_client.chat(system_prompt, user_message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    db.insert_message("assistant", reply)

    proposed_actions: list[ProposedAction] = []
    intents = autonomy.detect_action_intents(user_message, consent)
    for intent in intents:
        action_id = db.insert_action(
            intent["action_type"],
            intent["title"],
            intent["description"],
            intent["payload_json"],
            "proposed",
        )
        proposed_actions.append(
            ProposedAction(
                id=action_id,
                action_type=intent["action_type"],
                title=intent["title"],
                description=intent["description"],
                status="proposed",
            )
        )

    return ChatResponse(
        reply=reply,
        recalled_memories=[MemoryItem(**m) for m in recalled],
        proposed_actions=proposed_actions,
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
        return {"id": action_id, "status": "completed", "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
