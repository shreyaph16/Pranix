import { Link } from "@tanstack/react-router";

const links = [
  { to: "/", label: "OVERVIEW" },
  { to: "/map", label: "MAP" },
  { to: "/forecast", label: "FORECAST" },
  { to: "/causal", label: "CAUSAL" },
  { to: "/alerts", label: "ALERTS" },
  { to: "/copilot", label: "COPILOT" },
] as const;

export function TopBar() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div className="flex h-11 items-center justify-between px-4">
        <Link to="/" className="mono flex items-center gap-2 text-sm font-semibold tracking-[0.24em]">
          <span className="inline-block h-2 w-2 bg-aqi-good" />
          PRANIX
        </Link>
        <nav className="mono flex items-center gap-1 text-[11px] tracking-[0.14em]">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              activeOptions={{ exact: l.to === "/" }}
              className="px-2.5 py-1 text-muted-foreground transition-colors hover:text-foreground"
              activeProps={{ className: "px-2.5 py-1 text-foreground border-b border-aqi-good" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="mono hidden items-center gap-3 text-[11px] text-muted-foreground md:flex">
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-1.5 w-1.5 animate-pulse bg-aqi-good" />
            LIVE
          </span>
          <span>DEL · 28.61°N</span>
        </div>
      </div>
    </header>
  );
}