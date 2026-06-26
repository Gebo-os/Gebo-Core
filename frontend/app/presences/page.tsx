"use client";

import { PageHeader } from "@/components/PageHeader";
import { PresenceCard } from "@/components/PresenceCard";
import { useGebo } from "@/lib/GeboProvider";

export default function PresencesPage() {
  const { presences, status, loading } = useGebo();

  return (
    <>
      <PageHeader
        eyebrow="Ecosystem"
        title="Presence Dock"
        description="Gebo ecosystem beings and their current focus."
      />

      {loading ? (
        <div className="presence-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 200 }} />
          ))}
        </div>
      ) : (
        <>
          {status?.memory_count === 0 && (
            <div className="alert alert-info" style={{ marginBottom: "1.5rem" }}>
              Presences become more useful as memory grows.
            </div>
          )}
          <div className="presence-grid">
            {presences.map((p) => (
              <PresenceCard key={p.id} presence={p} />
            ))}
          </div>
        </>
      )}
    </>
  );
}
