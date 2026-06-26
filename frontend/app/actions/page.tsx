import { PageHeader } from "@/components/PageHeader";
import { AutonomyPanel } from "@/components/AutonomyPanel";

export default function ActionsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Autonomy"
        title="Autonomy Queue"
        description="Safe action proposals. Approve before anything runs."
      />
      <AutonomyPanel />
    </>
  );
}
