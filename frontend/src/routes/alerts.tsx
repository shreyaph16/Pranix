import { createFileRoute } from "@tanstack/react-router";
import { Shell } from "@/components/pranix/Shell";
import { interventions } from "@/lib/pranix-data";

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Alert Center — Pranix" },
      { name: "description", content: "Ranked, cost-aware intervention queue for Delhi municipal dispatch." },
      { property: "og:title", content: "Alert Center — Pranix" },
      { property: "og:description", content: "Ranked intervention dispatch queue." },
    ],
  }),
  component: AlertsPage,
});

function AlertsPage() {
  const ranked = [...interventions].sort((a, b) => b.est_reduction / b.cost - a.est_reduction / a.cost);
  return (
    <Shell title="Alert Center" subtitle="7 open · ranked by reduction/₹ · updated 00:12 UTC">
      <div className="grid grid-cols-3 gap-4">
        {[
          { l: "Open", v: "07", c: "text-aqi-poor" },
          { l: "Dispatched", v: "12", c: "text-aqi-satisfactory" },
          { l: "Total ΔPM2.5 avail.", v: "167", c: "text-aqi-good", u: "µg/m³" },
        ].map((k) => (
          <div key={k.l} className="panel p-4">
            <div className="mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">{k.l}</div>
            <div className={`num mt-2 text-3xl ${k.c}`}>{k.v} {k.u && <span className="mono text-[10px] uppercase tracking-widest text-muted-foreground">{k.u}</span>}</div>
          </div>
        ))}
      </div>

      <div className="panel mt-4">
        <div className="panel-header flex justify-between">
          <span>Ranked Interventions</span>
          <span>Score = |ATE| / cost</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead className="mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
              <tr className="border-b border-border">
                <th className="px-3 py-2 text-left">Rank</th>
                <th className="px-3 py-2 text-left">ID</th>
                <th className="px-3 py-2 text-left">Intervention</th>
                <th className="px-3 py-2 text-left">Target</th>
                <th className="px-3 py-2 text-right">ATE</th>
                <th className="px-3 py-2 text-right">Cost (₹Cr)</th>
                <th className="px-3 py-2 text-right">Conf.</th>
                <th className="px-3 py-2 text-right">Score</th>
                <th className="px-3 py-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {ranked.map((i, idx) => {
                const score = (Math.abs(i.ate) / i.cost).toFixed(1);
                return (
                  <tr key={i.id} className="border-b border-border hover:bg-surface-2">
                    <td className="num px-3 py-2 text-muted-foreground">{String(idx + 1).padStart(2, "0")}</td>
                    <td className="mono px-3 py-2 text-[11px] text-muted-foreground">{i.id}</td>
                    <td className="px-3 py-2">{i.name}</td>
                    <td className="mono px-3 py-2 text-[11px] text-muted-foreground">{i.target}</td>
                    <td className="num px-3 py-2 text-right text-aqi-good">{i.ate.toFixed(1)}</td>
                    <td className="num px-3 py-2 text-right">{i.cost.toFixed(2)}</td>
                    <td className="num px-3 py-2 text-right">{(i.confidence * 100).toFixed(0)}%</td>
                    <td className="num px-3 py-2 text-right text-foreground">{score}</td>
                    <td className="px-3 py-2 text-right">
                      <button className="mono border border-border-strong bg-surface-2 px-2 py-1 text-[10px] uppercase tracking-widest text-foreground hover:border-aqi-good hover:text-aqi-good">
                        Dispatch
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </Shell>
  );
}
