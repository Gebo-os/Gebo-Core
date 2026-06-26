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
  getMemories,
  getStatus,
  setConsent as apiSetConsent,
} from "@/lib/api";
import { DEFAULT_MISSION, MISSION_STORAGE_KEY } from "@/lib/constants";
import { deriveGeboStatus, getActivePresence, buildPresences } from "@/lib/presences";
import type { GeboSystemStatus, Memory, Presence, Status } from "@/lib/types";

interface GeboContextValue {
  online: boolean | null;
  status: Status | null;
  memories: Memory[];
  geboStatus: GeboSystemStatus;
  activePresence: Presence | null;
  presences: Presence[];
  mission: string;
  setMission: (m: string) => void;
  refresh: () => Promise<void>;
  refreshMemories: () => Promise<void>;
  toggleConsent: () => Promise<void>;
  consentLoading: boolean;
  loading: boolean;
}

const GeboContext = createContext<GeboContextValue | null>(null);

export function GeboProvider({ children }: { children: ReactNode }) {
  const [online, setOnline] = useState<boolean | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [mission, setMissionState] = useState(DEFAULT_MISSION);
  const [consentLoading, setConsentLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(MISSION_STORAGE_KEY);
      if (stored) setMissionState(stored);
    }
  }, []);

  const setMission = useCallback((m: string) => {
    setMissionState(m);
    if (typeof window !== "undefined") {
      localStorage.setItem(MISSION_STORAGE_KEY, m);
    }
  }, []);

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
      if (isOnline) {
        const s = await getStatus();
        setStatus(s);
        await refreshMemories();
      } else {
        setStatus(null);
      }
    } catch {
      setOnline(false);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, [refreshMemories]);

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
    geboStatus,
    activePresence,
    presences,
    mission,
    setMission,
    refresh,
    refreshMemories,
    toggleConsent,
    consentLoading,
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
