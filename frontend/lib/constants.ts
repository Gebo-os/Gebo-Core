import type { ChatMode, NavItem, Presence } from "./types";

export const APP_NAME = "Gebo Living Console";

export const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Pulse",
    shortLabel: "Pulse",
    description: "Current state at a glance",
  },
  {
    href: "/chat",
    label: "Chat",
    shortLabel: "Chat",
    description: "Conversation with memory awareness",
  },
  {
    href: "/memory",
    label: "Memory",
    shortLabel: "Memory",
    description: "View and manage continuity",
  },
  {
    href: "/presences",
    label: "Presences",
    shortLabel: "Presences",
    description: "Ecosystem beings and focus",
  },
  {
    href: "/actions",
    label: "Actions",
    shortLabel: "Actions",
    description: "Safe autonomy queue",
  },
  {
    href: "/reflexes",
    label: "Reflexes",
    shortLabel: "Reflex",
    description: "Memory-aware pattern automation",
  },
  {
    href: "/build-log",
    label: "Build Log",
    shortLabel: "Log",
    description: "Project progress journal",
  },
  {
    href: "/settings",
    label: "Settings",
    shortLabel: "Settings",
    description: "Privacy, model, and system",
  },
];

export const MEMORY_TYPES = [
  { value: "core", label: "Core" },
  { value: "project", label: "Project" },
  { value: "career", label: "Career" },
  { value: "presence", label: "Presence" },
  { value: "build_log", label: "Build Log" },
  { value: "preference", label: "Preference" },
  { value: "system", label: "System" },
] as const;

export const MEMORY_TYPE_FILTERS = [
  { value: "all", label: "All types" },
  ...MEMORY_TYPES.map((t) => ({ value: t.value, label: t.label })),
];

export const CHAT_MODES: { value: ChatMode; label: string; prefix: string }[] = [
  { value: "ask", label: "Ask", prefix: "" },
  { value: "remember", label: "Remember", prefix: "Remember: " },
  { value: "plan", label: "Plan", prefix: "Make a plan for: " },
  { value: "build", label: "Build", prefix: "Help me build: " },
  { value: "search", label: "Search Memory", prefix: "Search my memory for: " },
];

export const DEFAULT_MISSION =
  "Build Gebo OS continuity — memory, presence, and safe autonomy.";

export const PRESENCE_DEFINITIONS: Omit<
  Presence,
  "status" | "lastContribution"
>[] = [
  {
    id: "gebo",
    name: "Gebo",
    role: "Private intelligence layer",
    focus: "Memory, strategy, and continuity",
    memoryAccess: "Full",
    suggestedUse: "Chat, planning, and system direction",
    mark: "G",
    primary: true,
  },
  {
    id: "lockin",
    name: "LockIn",
    role: "Focus and execution",
    focus: "Commitments and follow-through",
    memoryAccess: "Project",
    suggestedUse: "Lock in goals and track completion",
    mark: "L",
  },
  {
    id: "dream",
    name: "Dream",
    role: "Vision and exploration",
    focus: "Long-range ideas and possibilities",
    memoryAccess: "Presence",
    suggestedUse: "Explore future directions",
    mark: "D",
  },
  {
    id: "mya",
    name: "Mya",
    role: "Creative presence",
    focus: "Expression and creative output",
    memoryAccess: "Project",
    suggestedUse: "Creative projects and voice",
    mark: "M",
  },
  {
    id: "slatt",
    name: "Slatt Tool",
    role: "Utility and tooling",
    focus: "Practical tools and workflows",
    memoryAccess: "System",
    suggestedUse: "Build and automate internal tools",
    mark: "S",
  },
  {
    id: "sleep",
    name: "Sleep",
    role: "Rest and recovery",
    focus: "Offline processing and pause",
    memoryAccess: "Read-only",
    suggestedUse: "When Gebo should rest",
    mark: "Z",
  },
  {
    id: "dark",
    name: "Dark",
    role: "Private depth",
    focus: "Sensitive context and protected notes",
    memoryAccess: "Restricted",
    suggestedUse: "High-privacy memory only",
    mark: "—",
  },
];

export const SAFETY_RULES = [
  "Gebo proposes actions. Bb approves before anything runs.",
  "No system commands or shell execution from chat.",
  "No file writes outside the project folder.",
  "No internet access after setup.",
  "No automatic GitHub pushes.",
  "No data deletion without explicit backend support.",
  "All processing stays local on your machine.",
];

export const BUILD_LOG_STORAGE_KEY = "gebo-build-log";
export const MISSION_STORAGE_KEY = "gebo-current-mission";
export const MOTION_STORAGE_KEY = "gebo-motion";
export const CHAT_DRAFT_KEY = "gebo-chat-draft";
export const COMMAND_DRAFT_KEY = "gebo-command-draft";
