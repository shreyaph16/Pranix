import type { ReactNode } from "react";
import { TopBar } from "./TopBar";

export function Shell({ children, title, subtitle }: { children: ReactNode; title?: string; subtitle?: string }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <TopBar />
      {title && (
        <div className="border-b border-border">
          <div className="flex items-end justify-between px-4 py-4">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
              {subtitle && <p className="mono mt-1 text-[11px] uppercase tracking-[0.14em] text-muted-foreground">{subtitle}</p>}
            </div>
          </div>
        </div>
      )}
      <main className="px-4 py-4">{children}</main>
      <footer className="mono border-t border-border px-4 py-3 text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
        PRANIX v0.1 · Delhi Municipal Air Ops · Data refreshed 00:12 UTC
      </footer>
    </div>
  );
}

export function severityColor(band: string) {
  switch (band) {
    case "Good": return "text-aqi-good";
    case "Satisfactory": return "text-aqi-satisfactory";
    case "Moderate": return "text-aqi-moderate";
    case "Poor": return "text-aqi-poor";
    case "Very Poor": return "text-aqi-very-poor";
    case "Severe": return "text-aqi-severe";
    default: return "text-muted-foreground";
  }
}

export function severityBg(band: string) {
  switch (band) {
    case "Good": return "bg-aqi-good";
    case "Satisfactory": return "bg-aqi-satisfactory";
    case "Moderate": return "bg-aqi-moderate";
    case "Poor": return "bg-aqi-poor";
    case "Very Poor": return "bg-aqi-very-poor";
    case "Severe": return "bg-aqi-severe";
    default: return "bg-muted-foreground";
  }
}