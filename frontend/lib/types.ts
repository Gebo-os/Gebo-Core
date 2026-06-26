export interface Status {
  app: string;
  model: string;
  consent: boolean;
  memory_count: number;
  message_count: number;
  proposed_action_count: number;
  approved_action_count: number;
  completed_action_count: number;
}

export interface Memory {
  id: number;
  created_at: string;
  memory_type: string;
  content: string;
  source: string;
}

export interface RecalledMemory {
  id: number;
  created_at: string;
  memory_type: string;
  content: string;
  source: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  recalled?: RecalledMemory[];
  proposedActionIds?: number[];
  wikiSources?: string[];
  timestamp: string;
}

export interface ProposedActionSummary {
  id: number;
  action_type: string;
  title: string;
  description: string;
  status: string;
}

export interface ChatResponse {
  reply: string;
  recalled_memories: RecalledMemory[];
  proposed_actions: ProposedActionSummary[];
  wiki_sources?: string[];
}

export interface Action {
  id: number;
  created_at: string;
  action_type: string;
  title: string;
  description: string;
  payload_json: string;
  status:
    | "proposed"
    | "approved"
    | "rejected"
    | "running"
    | "completed"
    | "failed";
  result_json: string | null;
}

export interface CodexStatus {
  available: boolean;
  enabled: boolean;
  version: string | null;
  workdir: string;
  timeout_sec: number;
}

export interface WikiStatus {
  enabled: boolean;
  available: boolean;
  auto_mode: string;
  zim_path: string | null;
  error: string | null;
  title: string | null;
  article_count: number | null;
  has_fulltext_index: boolean | null;
}

export type PresenceStatus = "Awake" | "Quiet" | "Resting" | "Needs Memory";

export interface Presence {
  id: string;
  name: string;
  role: string;
  status: PresenceStatus;
  focus: string;
  memoryAccess: string;
  lastContribution: string;
  suggestedUse: string;
  mark: string;
  primary?: boolean;
}

export type GeboSystemStatus = "Awake" | "Resting" | "Needs Setup";

export type ChatMode = "ask" | "remember" | "plan" | "build" | "search";

export interface BuildLogEntry {
  id: string;
  created_at: string;
  built: string;
  broke: string;
  learned: string;
  next_mission: string;
}

export interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
}
