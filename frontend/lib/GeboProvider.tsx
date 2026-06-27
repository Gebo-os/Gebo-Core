"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  checkBackendOnline,
  getBootstrap,
  getMemories,
  setConsent as apiSetConsent,
  setNetworkSettings as apiSetNetworkSettings,
} from "@/lib/api";
import {
  DEFAULT_MISSION,
  MISSION_STORAGE_KEY,
  MOTION_STORAGE_KEY,
} from "@/lib/constants";
import { deriveGeboStatus, getActivePresence, buildPresences } from "@/lib/presences";
import type {
  AgentRuntimeStatus,
  CodexStatus,
  GeboSystemStatus,
  Memory,
  NetworkSettings,
  Presence,
  Status,
  WikiStatus,
} from "@/lib/types";

interface GeboContextValue {
  online: boolean | null;
  status: Status | null;
  memories: Memory[];
  codex: CodexStatus | null;
  wiki: WikiStatus | null;
  agentRuntime: AgentRuntimeStatus | null;
  network: NetworkSettings | null;
  geboStatus: GeboSystemStatus;
  activePresence: Presence | null;
  presences: Presence[];
  mission: string;
  setMission: (m: string) => void;
  motionEnabled: boolean;
  setMotionEnabled: (v: boolean) => void;
  pulse: number;
  triggerPulse: () => void;
  refresh: () => Promise<void>;
  refreshMemories: () => Promise<void>;
  toggleConsent: () => Promise<void>;
  toggleInternetAccess: () => Promise<void>;
  consentLoading: boolean;
  networkLoading: boolean;
  loading: boolean;
}

const GeboContext = createContext<GeboContextValue | null>(null);

export function GeboProvider({ children }: { children: ReactNode }) {
  const [online, setOnline] = useState<boolean | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [codex, setCodex] = useState<CodexStatus | null>(null);
  const [wiki, setWiki] = useState<WikiStatus | null>(null);
  const [agentRuntime, setAgentRuntime] = useState<AgentRuntimeStatus | null>(null);
  const [network, setNetwork] = useState<NetworkSettings | null>(null);
  const [mission, setMissionState] = useState(DEFAULT_MISSION);
  const [motionEnabled, setMotionEnabledState] = useState(true);
  const [pulse, setPulse] = useState(0);
  const [consentLoading, setConsentLoading] = useState(false);
  const [networkLoading, setNetworkLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(MISSION_STORAGE_KEY);
      if (stored) setMissionState(stored);
      if (localStorage.getItem(MOTION_STORAGE_KEY) === "off") {
        setMotionEnabledState(false);
      }
    }
  }, []);

  const setMission = useCallback((m: string) => {
    setMissionState(m);
    if (typeof window !== "undefined") {
      localStorage.setItem(MISSION_STORAGE_KEY, m);
    }
  }, []);

  const setMotionEnabled = useCallback((v: boolean) => {
    setMotionEnabledState(v);
    if (typeof window !== "undefined") {
      localStorage.setItem(MOTION_STORAGE_KEY, v ? "on" : "off");
    }
  }, []);

  const triggerPulse = useCallback(() => setPulse((p) => p + 1), []);

  const refreshMemories = useCallback(async () => {
    try {
      const data = await getMemories();
      setMemories(data);
    } catch {
      setMemories([]);
    }
  }, []);

  const refresh = useCallback(async () => {
    try {
      const isOnline = await checkBackendOnline();
      setOnline(isOnline);
      if (!isOnline) {
        setStatus(null);
        setMemories([]);
        setCodex(null);
        setWiki(null);
        setAgentRuntime(null);
        setNetwork(null);
        return;
      }
      try {
        const [boot, mems] = await Promise.all([
          getBootstrap(),
          getMemories().catch(() => []),
        ]);
        setStatus(boot.status);
        setMemories(mems);
        setCodex(boot.codex);
        setWiki(boot.wiki);
        setAgentRuntime(boot.agent_runtime);
        setNetwork(boot.network);
      } catch {
        // Health OK but bootstrap failed — stale backend; stay online, fetch piecemeal
        const [st, mems, net] = await Promise.all([
          getStatus().catch(() => null),
          getMemories().catch(() => []),
          getNetworkSettings().catch(() => null),
        ]);
        setStatus(st);
        setMemories(mems);
        setNetwork(net);
        setCodex(null);
        setWiki(null);
        setAgentRuntime(null);
      }
    } catch {
      setOnline(false);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleConsent = useCallback(async () => {
    if (!status) return;
    setConsentLoading(true);
    try {
      await apiSetConsent(!status.consent);
      await refresh();
    } finally {
      setConsentLoading(false);
    }
  }, [status, refresh]);

  const toggleInternetAccess = useCallback(async () => {
    if (!network) return;
    setNetworkLoading(true);
    try {
      const updated = await apiSetNetworkSettings(!network.internet_access);
      setNetwork(updated);
    } finally {
      setNetworkLoading(false);
    }
  }, [network]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 10000);
    return () => clearInterval(interval);
  }, [refresh]);

  const presences = useMemo(
    () => buildPresences(status, memories),
    [status, memories]
  );

  const activePresence = useMemo(
    () => (presences.length ? getActivePresence(presences) : null),
    [presences]
  );

  const geboStatus = useMemo(
    () => deriveGeboStatus(online === true, status),
    [online, status]
  );

  const value: GeboContextValue = {
    online,
    status,
    memories,
    codex,
    wiki,
    agentRuntime,
    network,
    geboStatus,
    activePresence,
    presences,
    mission,
    setMission,
    motionEnabled,
    setMotionEnabled,
    pulse,
    triggerPulse,
    refresh,
    refreshMemories,
    toggleConsent,
    toggleInternetAccess,
    consentLoading,
    networkLoading,
    loading,
  };

  return (
    <GeboContext.Provider value={value}>{children}</GeboContext.Provider>
  );
}

export function useGebo() {
  const ctx = useContext(GeboContext);
  if (!ctx) throw new Error("useGebo must be used within GeboProvider");
  return ctx;
}
