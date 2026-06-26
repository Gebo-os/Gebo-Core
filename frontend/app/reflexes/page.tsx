import { PageHeader } from "@/components/PageHeader";
import { ReflexPanel } from "@/components/ReflexPanel";

export default function ReflexesPage() {
  return (
    <>
      <PageHeader
        eyebrow="Reflex Engine"
        title="Gebo Reflex Engine"
        description="Memory-aware automation. Pattern → proposal → approval → execution → stronger memory."
      />
      <ReflexPanel />
    </>
  );
}
