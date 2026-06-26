import { PageHeader } from "@/components/PageHeader";
import { MemoryPanel } from "@/components/MemoryPanel";

export default function MemoryPage() {
  return (
    <>
      <PageHeader
        eyebrow="Continuity"
        title="Memory Garden"
        description="View, add, search, and filter Gebo's stored memory."
      />
      <MemoryPanel />
    </>
  );
}
