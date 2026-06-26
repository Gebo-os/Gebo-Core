interface StatusCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}

export function StatusCard({ label, value, sub, accent }: StatusCardProps) {
  return (
    <div className="status-card">
      <div className="status-card-label">{label}</div>
      <div className={`status-card-value ${accent ? "accent" : ""}`}>
        {value}
      </div>
      {sub && <div className="status-card-sub">{sub}</div>}
    </div>
  );
}
