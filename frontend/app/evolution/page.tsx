import { PageHeader } from "@/components/PageHeader";
import { EvolutionPanel } from "@/components/EvolutionPanel";

export default function EvolutionPage() {
  return (
    <>
      <PageHeader
        eyebrow="Evolution Loop"
        title="Gebo Evolution Loop"
        description="Autonomy that learns from outcomes, upgrades reflexes, and proposes better tools."
      />
      <EvolutionPanel />
    </>
  );
}
