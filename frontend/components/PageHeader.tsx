interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: PageHeaderProps) {
  return (
    <header className="page-header">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "1rem",
          flexWrap: "wrap",
        }}
      >
        <div>
          {eyebrow && <div className="page-header-eyebrow">{eyebrow}</div>}
          <h1 className="page-header-title">{title}</h1>
          {description && (
            <p className="page-header-desc">{description}</p>
          )}
        </div>
        {action}
      </div>
    </header>
  );
}
