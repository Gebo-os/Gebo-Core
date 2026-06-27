export interface Status {
  app: string;
  model: string;
  consent: boolean;
  memory_count: number;
  message_count: number;
  proposed_action_count: number;
  approved_action_count: number;
  completed_action_count: number;
  ollama_runtime?: {
    loaded?: boolean;
    model?: string;
    size_vram?: number;
    size?: number;
  } | null;
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
  detectedReflexes?: DetectedReflex[];
  wikiSources?: string[];
  timestamp: string;
}

export interface DetectedReflex {
  reflex_id: number;
  name: string;
  description: string;
  trigger_pattern: string;
  action_type: string;
  approval_required: boolean;
  proposals_created: number;
}

export interface Reflex {
  id: number;
  name: string;
  description: string;
  trigger_type: string;
  trigger_pattern: string;
  action_type: string;
  approval_required: boolean;
  enabled: boolean;
  created_at: string;
  last_used: string | null;
}

export interface ReflexEvent {
  id: number;
  reflex_id: number | null;
  reflex_name: string | null;
  detected_at: string;
  input_text: string;
  proposed_action_id: number | null;
  result: string | null;
}

export interface ReflexCreatePayload {
  name: string;
  description: string;
  trigger_type: string;
  trigger_pattern: string;
  action_type: string;
  approval_required: boolean;
  enabled: boolean;
}

export interface EvolutionStatus {
  average_autonomy_score: number | null;
  total_evolution_events: number;
  proposed_upgrades: number;
  approved_upgrades: number;
  completed_upgrades: number;
  rejected_upgrades: number;
  latest_lesson: string | null;
  top_recommended_upgrade: UpgradeSuggestion | null;
}

export interface EvolutionEvent {
  id: number;
  created_at: string;
  source_type: string;
  source_id: number | null;
  lesson: string;
  score: number;
  recommended_upgrade: string | null;
  status: string;
}

export interface AutonomyScore {
  id: number;
  created_at: string;
  action_id: number | null;
  mission_value: number;
  speed_score: number;
  risk_score: number;
  approval_score: number;
  memory_impact: number;
  product_impact: number;
  money_impact: number;
  total_score: number;
  notes: string | null;
}

export interface UpgradeSuggestion {
  id: number;
  created_at: string;
  upgrade_type: string;
  title: string;
  description: string;
  reason: string;
  status: string;
  proposed_action_id: number | null;
}

export interface ScoreActionPayload {
  action_id: number;
  mission_value: number;
  speed_score: number;
  risk_score: number;
  approval_score: number;
  memory_impact: number;
  product_impact: number;
  money_impact: number;
  notes?: string;
}

export interface SuggestUpgradePayload {
  upgrade_type: string;
  title: string;
  description: string;
  reason: string;
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
  detected_reflexes?: DetectedReflex[];
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

export interface AgentRuntimeAgent {
  agent_id: string;
  name: string;
  category: string;
  status: string;
  message: string;
  cycles: number;
  last_tick: string | null;
  tier: string;
  registry_status: string;
}

export interface CodexLaneStatus {
  available: boolean;
  enabled: boolean;
  version: string | null;
  status: string;
  message: string;
  cycles: number;
  last_tick: string | null;
  parallel_with_agents: boolean;
  last_audit_ok?: boolean | null;
}

export interface AgentRuntimeStatus {
  running: boolean;
  started_at: string | null;
  tick_interval_sec: number;
  active_agents: number;
  total_registry: number;
  healthy: boolean;
  parallel_workers?: number;
  cycle_count?: number;
  codex_lane?: CodexLaneStatus | null;
  agents: AgentRuntimeAgent[];
}

export interface NetworkSettings {
  internet_access: boolean;
  cors_mode: string;
  backend_url: string;
  frontend_url: string;
  bind_host: string;
  allowed_origins: string[];
}

/** Single-call bootstrap for Living Console and consumer apps. */
export interface GeboBootstrap {
  version: string;
  app: string;
  health: { ok: boolean; agent_runtime_healthy: boolean };
  status: Status;
  network: NetworkSettings;
  codex: CodexStatus;
  wiki: WikiStatus;
  agent_runtime: AgentRuntimeStatus;
  capabilities: Record<string, boolean | number>;
}

export interface IntegrationItem {
  id: string;
  name: string;
  category: string;
  mode: "learnable" | "connector";
  provider: string;
  configured: boolean;
  status: string;
  docs?: string;
  env?: string[];
}

export interface IntegrationsStatus {
  total: number;
  learnable: number;
  connectors: number;
  ready: number;
  items: IntegrationItem[];
}

export interface CliItem {
  id: string;
  name: string;
  role: string;
  available: boolean;
  path: string | null;
  version: string | null;
  install_hint: string;
}

export interface CliStatus {
  total: number;
  available: number;
  items: CliItem[];
}

export interface KnowledgeStatus {
  catalog_path: string;
  private_docs_dir: string;
  private_doc_count: number;
  private_doc_files: string[];
  catalog_oss_count: number;
  catalog_docs_count: number;
  catalog_models_count: number;
  knowledge_memory_count: number;
  web_knowledge_memory_count: number;
  internet_access: boolean;
  web_fetch_ready: boolean;
}

export interface LearningCycleResult {
  ok: boolean;
  lesson?: string;
  collection?: Record<string, unknown>;
  knowledge?: KnowledgeStatus;
}

export interface NavItem {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
}
