"""Gebo internal Agent Registry.

Agents are expert roles Gebo references when planning, building, or proposing
actions. They are NOT autonomous chatbots. Presences are the beings; agents are
the silent expert workers that serve a Presence.

This module is the registry layer only.
"""
from __future__ import annotations

AGENT_REGISTRY: list[dict] = [
    {
        "id": "sleep_project_manager",
        "name": "Sleep Project Manager",
        "category": "Executive",
        "mark": "PM",
        "purpose": "Keeps everything organized and moving without chaos.",
        "responsibilities": [
            "Plan the next steps and sequence work",
            "Prevent scope chaos and half-finished systems",
            "Hold a clean execution order",
        ],
        "outputs": ["Plans", "Next steps", "Priority order"],
        "activation_trigger": "When work needs planning or feels scattered.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "product_architect",
        "name": "Product Architect Agent",
        "category": "Product",
        "mark": "PA",
        "purpose": "Turns ideas into real product features and structure.",
        "responsibilities": [
            "Decide system structure: frontend, backend, DB, model, memory, autonomy",
            "Define feature specs and user flows",
            "Set build order",
        ],
        "outputs": ["Architecture maps", "Feature specs", "File structure"],
        "activation_trigger": "At the start of a new feature or system.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "fullstack_builder",
        "name": "Full-Stack Builder Agent",
        "category": "Engineering",
        "mark": "FB",
        "purpose": "Builds the actual application.",
        "responsibilities": [
            "Build FastAPI routes and SQLite layer",
            "Build Next.js pages and components",
            "Wire frontend and backend together",
        ],
        "outputs": ["Working code", "API routes", "UI pages"],
        "activation_trigger": "When a spec is ready to be built.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "ux_ui_designer",
        "name": "UX/UI Product Designer Agent",
        "category": "Product",
        "mark": "UX",
        "purpose": "Makes Gebo look professional, usable, and alive.",
        "responsibilities": [
            "Design pages, components, and layouts",
            "Define interaction rules and empty/loading/error states",
            "Keep visual consistency, avoid AI-slop look",
        ],
        "outputs": ["Pages", "Components", "Layout and interaction rules"],
        "activation_trigger": "When UI is being created or refined.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "memory_engineer",
        "name": "Memory Engineer Agent",
        "category": "Intelligence",
        "mark": "ME",
        "purpose": "Owns Gebo's memory.",
        "responsibilities": [
            "Save, recall, rank, and organize memory",
            "Define memory types and recall rules",
            "Handle export and continuity",
        ],
        "outputs": ["Memory system", "Memory types", "Recall rules"],
        "activation_trigger": "When memory storage or recall needs work.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "autonomy_engineer",
        "name": "Autonomy Engineer Agent",
        "category": "Autonomy",
        "mark": "AE",
        "purpose": "Owns the approval-based action system.",
        "responsibilities": [
            "Build the action queue and propose/approve/run loop",
            "Maintain safe tools in the registry",
            "Keep execution gated behind approval",
        ],
        "outputs": ["Autonomy backend", "Action UI", "Safe tools"],
        "activation_trigger": "When actions or autonomy need changes.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "qa_bug_hunter",
        "name": "QA / Bug Hunter Agent",
        "category": "Engineering",
        "mark": "QA",
        "purpose": "Finds what is broken.",
        "responsibilities": [
            "Find broken routes, missing imports, API errors",
            "Catch bad UX and edge cases",
            "Produce a clear bug list with fixes",
        ],
        "outputs": ["Bug list", "Fixes", "Test notes"],
        "activation_trigger": "Before release or after big changes.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "security_privacy",
        "name": "Security & Privacy Agent",
        "category": "Safety",
        "mark": "SP",
        "purpose": "Keeps the app local and the data private.",
        "responsibilities": [
            "Keep processing local-only",
            "Protect memory and enforce consent",
            "Block unsafe actions: shell, outside writes, hidden internet, deletes",
        ],
        "outputs": ["Safety rules", "Consent rules", "Private-data checks"],
        "activation_trigger": "On any change touching data or execution.",
        "status": "active",
        "tier": "v0",
    },
    {
        "id": "presence_designer",
        "name": "Presence Designer Agent",
        "category": "Creative",
        "mark": "PD",
        "purpose": "Creates new Presences properly.",
        "responsibilities": [
            "Define role, voice, and behavior",
            "Set memory scope and access level",
            "Map the Presence evolution path",
        ],
        "outputs": ["Presence definitions", "Voice and behavior", "Evolution path"],
        "activation_trigger": "When adding or shaping a Presence.",
        "status": "planned",
        "tier": "v1",
    },
    {
        "id": "local_model_engineer",
        "name": "Local Model Engineer Agent",
        "category": "Intelligence",
        "mark": "LM",
        "purpose": "Owns Ollama and model behavior.",
        "responsibilities": [
            "Choose model and prompt format",
            "Define response style and context limits",
            "Wire model config",
        ],
        "outputs": ["Model config", "Prompt wiring", "Context rules"],
        "activation_trigger": "When tuning model behavior or routing.",
        "status": "planned",
        "tier": "v1",
    },
    {
        "id": "content_agent",
        "name": "Content Agent",
        "category": "Business",
        "mark": "CO",
        "purpose": "Turns build progress into social content.",
        "responsibilities": [
            "Write captions, posts, and demo scripts",
            "Frame the founder story",
            "Turn milestones into shareable content",
        ],
        "outputs": ["Captions", "Reels/demo posts", "Founder story"],
        "activation_trigger": "When there is progress worth sharing.",
        "status": "planned",
        "tier": "v1",
    },
    {
        "id": "launch_agent",
        "name": "Launch Agent",
        "category": "Launch",
        "mark": "LN",
        "purpose": "Owns the private release.",
        "responsibilities": [
            "Ensure the app runs and can be backed up",
            "Prepare a private demo flow",
            "Hold the launch checklist",
        ],
        "outputs": ["Launch checklist", "Demo flow", "Backup plan"],
        "activation_trigger": "When preparing to show or release Gebo.",
        "status": "planned",
        "tier": "v1",
    },
]


def get_agents() -> list[dict]:
    return AGENT_REGISTRY


def get_categories() -> list[str]:
    seen: list[str] = []
    for a in AGENT_REGISTRY:
        if a["category"] not in seen:
            seen.append(a["category"])
    return seen
