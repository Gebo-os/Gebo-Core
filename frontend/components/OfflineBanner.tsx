"use client";

import { useGebo } from "@/lib/GeboProvider";

export function OfflineBanner() {
  const { online } = useGebo();
  if (online !== false) return null;

  return (
    <div className="offline-banner" role="alert">
      Backend offline — start FastAPI on port 8000. Chat and memory are paused
      until Gebo reconnects.
    </div>
  );
}
