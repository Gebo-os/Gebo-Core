import { PageHeader } from "@/components/PageHeader";
import { BuildLogPanel } from "@/components/BuildLogPanel";

export default function BuildLogPage() {
  return (
    <>
      <PageHeader
        eyebrow="Progress"
        title="Build Log"
        description="Founder journal — what was built, what broke, what was learned."
      />
      <BuildLogPanel />
    </>
  );
}
