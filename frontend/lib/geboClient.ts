/**
 * Gebo consumer SDK — single import surface for Living Console and future apps.
 *
 * Usage:
 *   import { geboClient } from "@/lib/geboClient";
 *   const boot = await geboClient.bootstrap();
 *   console.log(boot.status.model);
 */
export {
  getApiUrl,
  getBootstrap,
  getHealth,
  getStatus,
  getNetworkSettings,
  setNetworkSettings,
  getMemories,
  saveMemory,
  sendChat,
  getActions,
  approveAction,
  rejectAction,
  runAction,
  getCodexStatus,
  getWikiStatus,
  getAgentRuntimeStatus,
  getReflexes,
  createReflex,
  toggleReflex,
  getReflexEvents,
  getEvolutionStatus,
  getEvolutionEvents,
  getEvolutionScores,
  getEvolutionUpgrades,
  scoreAction,
  suggestUpgrade,
  approveUpgrade,
  rejectUpgrade,
  getExportUrl,
  checkBackendOnline,
  setConsent,
} from "./api";

export type {
  GeboBootstrap,
  Status,
  Memory,
  NetworkSettings,
  CodexStatus,
  WikiStatus,
  AgentRuntimeStatus,
  Action,
  ChatResponse,
} from "./types";

import { checkBackendOnline, getBootstrap, getMemories } from "./api";
import type { GeboBootstrap, Memory } from "./types";

export interface GeboSession {
  online: boolean;
  bootstrap: GeboBootstrap | null;
  memories: Memory[];
}

/** Load everything a consumer shell needs in two parallel calls. */
export async function loadSession(): Promise<GeboSession> {
  const online = await checkBackendOnline();
  if (!online) {
    return { online: false, bootstrap: null, memories: [] };
  }
  const [bootstrap, memories] = await Promise.all([
    getBootstrap(),
    getMemories().catch(() => [] as Memory[]),
  ]);
  return { online: true, bootstrap, memories };
}

export const geboClient = {
  bootstrap: getBootstrap,
  loadSession,
  isOnline: checkBackendOnline,
};
