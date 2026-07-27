import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Shell } from "@/components/pranix/Shell";
import { modules, stations } from "@/lib/pranix-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Pranix — Hyperlocal Air Quality Intelligence for Delhi" },
      { name: "description", content: "Command-center intelligence for Delhi municipal air quality teams: hotspots, forecasts, causal impact and dispatch." },
      { property: "og:title", content: "Pranix — Towards Breathable Cities" },
      { property: "og:description", content: "Hyperlocal air quality intelligence for Delhi municipal teams." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function useCounter(target: number, ms = 1400) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const start = performance.now();
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / ms);
      setN(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);
  return n;
}

function Stat({ value, label, sub }: { value: number; label: string; sub: string }) {
  const n = useCounter(value);
  return (
    <div className="panel p-5">
      <div className="mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">{label}</div>
      <div className="num mt-3 text-4xl font-semibold tabular-nums text-foreground md:text-5xl">
        {n.toLocaleString("en-IN")}
      </div>
      <div className="mono mt-2 text-[11px] text-muted-foreground">{sub}</div>
    </div>
  );
}

function Index() {
  const worst = [...stations].sort((a, b) => b.pm25 - a.pm25).slice(0, 6);
  return (
    <Shell>
      {/* HERO */}
      <section className="border-b border-border">
        <div className="grid grid-cols-12 gap-0">
          <div className="col-span-12 border-border px-2 py-10 md:col-span-8 md:border-r md:px-6 md:py-16">
            <div className="mono flex items-center gap-3 text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
              <span className="h-px w-8 bg-border-strong" />
              <span>Pranix / v0.1 / DELHI-NCT</span>
            </div>
            <h1 className="mt-6 text-[44px] font-semibold leading-[1.02] tracking-tight md:text-[72px]">
              Towards <span className="text-aqi-good">Breathable</span> Cities.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
              An operational intelligence layer for Delhi municipal air-quality teams — fusing 18 CPCB
              stations, meteorological priors and causal inference into a single dispatch surface.
            </p>
            <div className="mono mt-8 flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.14em]">
              <Link to="/map" className="border border-border-strong bg-surface-2 px-3 py-2 text-foreground hover:border-aqi-good hover:text-aqi-good">→ Open Hotspot Map</Link>
              <Link to="/alerts" className="border border-border px-3 py-2 text-muted-foreground hover:text-foreground">Dispatch Queue</Link>
              <Link to="/copilot" className="border border-border px-3 py-2 text-muted-foreground hover:text-foreground">Ask Copilot</Link>
            </div>
          </div>
          <aside className="col-span-12 px-2 py-6 md:col-span-4 md:px-4 md:py-8">
            <div className="mono mb-3 text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
              Live Watchlist · Top 6 PM2.5
            </div>
            <div className="panel divide-y divide-border">
              {worst.map((s) => (
                <div key={s.id} className="flex items-center justify-between px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className={`inline-block h-2 w-2 ${s.band === "Severe" ? "bg-aqi-severe" : "bg-aqi-very-poor"}`} />
                    <span className="mono text-[11px] text-muted-foreground">{s.id}</span>
                    <span className="text-sm">{s.name}</span>
                  </div>
                  <span className="num text-sm font-medium text-foreground">{s.pm25}</span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </section>

      {/* STAT COUNTERS */}
      <section className="grid grid-cols-1 gap-0 border-b border-border md:grid-cols-3">
        <Stat value={74178} label="Rows Analyzed" sub="CPCB continuous monitor stream · last 30d" />
        <div className="border-t border-border md:border-l md:border-t-0" />
        <Stat value={18} label="Stations Monitored" sub="Real-time telemetry · 15-min cadence" />
        <div className="border-t border-border md:border-l md:border-t-0" />
        <Stat value={3} label="Hotspot Clusters" sub="Density-based · PM2.5 &gt; 250 µg/m³" />
      </section>

      {/* MODULES */}
      <section className="py-8">
        <div className="mono mb-4 flex items-center justify-between text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
          <span>// Modules</span>
          <span>05 systems online</span>
        </div>
        <div className="grid grid-cols-1 gap-px border border-border bg-border md:grid-cols-2 lg:grid-cols-5">
          {modules.map((m) => (
            <Link
              key={m.to}
              to={m.to}
              className="group flex flex-col justify-between bg-surface p-5 transition-colors hover:bg-surface-2"
            >
              <div>
                <div className="mono flex items-center justify-between text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                  <span>MOD·{m.code}</span>
                  <span className="text-aqi-good">●</span>
                </div>
                <div className="mt-6 text-lg font-medium text-foreground group-hover:text-aqi-good">
                  {m.title}
                </div>
                <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">{m.desc}</p>
              </div>
              <div className="mono mt-8 flex items-center justify-between text-[11px] uppercase tracking-[0.14em]">
                <span className="text-muted-foreground">{m.stat}</span>
                <span className="text-foreground">Open →</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Shell>
  );
}
