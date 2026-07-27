import { createFileRoute } from "@tanstack/react-router";
import { Shell, severityBg, severityColor } from "@/components/pranix/Shell";
import { stations } from "@/lib/pranix-data";

export const Route = createFileRoute("/forecast")({
  head: () => ({
    meta: [
      { title: "AQI Forecast — Pranix" },
      { name: "description", content: "6h and 24h PM2.5 forecasts for 18 Delhi CPCB stations." },
      { property: "og:title", content: "AQI Forecast — Pranix" },
      { property: "og:description", content: "Station-level PM2.5 forecasts." },
    ],
  }),
  component: ForecastPage,
});

function delta(a: number, b: number) {
  const d = b - a;
  const s = d > 0 ? "+" : "";
  return { text: `${s}${d}`, up: d > 0 };
}

function ForecastPage() {
  const rows = [...stations].sort((a, b) => b.pm25_24h - a.pm25_24h);
  return (
    <Shell title="AQI Forecast" subtitle="Model: ensemble-gbm-v3 · horizon 24h · MAE ±14 µg/m³">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {[
          { l: "Model MAE", v: "14.2", u: "µg/m³" },
          { l: "Rows", v: "74,178", u: "last 30d" },
          { l: "Cutoff", v: "00:00", u: "IST" },
          { l: "Horizon", v: "24", u: "hours" },
        ].map((k) => (
          <div key={k.l} className="panel p-4">
            <div className="mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">{k.l}</div>
            <div className="num mt-2 text-2xl">{k.v} <span className="mono text-[10px] uppercase tracking-widest text-muted-foreground">{k.u}</span></div>
          </div>
        ))}
      </div>

      <div className="panel mt-4">
        <div className="panel-header flex justify-between">
          <span>Station Forecast Table</span>
          <span>PM2.5 µg/m³ · sorted by 24h projection</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px]">
            <thead className="mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
              <tr className="border-b border-border">
                <th className="px-3 py-2 text-left">ID</th>
                <th className="px-3 py-2 text-left">Station</th>
                <th className="px-3 py-2 text-left">Band</th>
                <th className="px-3 py-2 text-right">Now</th>
                <th className="px-3 py-2 text-right">+6h</th>
                <th className="px-3 py-2 text-right">Δ6</th>
                <th className="px-3 py-2 text-right">+24h</th>
                <th className="px-3 py-2 text-right">Δ24</th>
                <th className="px-3 py-2 text-right">Trend</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => {
                const d6 = delta(s.pm25, s.pm25_6h);
                const d24 = delta(s.pm25, s.pm25_24h);
                return (
                  <tr key={s.id} className="border-b border-border hover:bg-surface-2">
                    <td className="mono px-3 py-2 text-[11px] text-muted-foreground">{s.id}</td>
                    <td className="px-3 py-2">{s.name}</td>
                    <td className="px-3 py-2">
                      <span className="flex items-center gap-1.5">
                        <span className={`inline-block h-1.5 w-1.5 ${severityBg(s.band)}`} />
                        <span className={`mono text-[11px] ${severityColor(s.band)}`}>{s.band}</span>
                      </span>
                    </td>
                    <td className="num px-3 py-2 text-right">{s.pm25}</td>
                    <td className="num px-3 py-2 text-right">{s.pm25_6h}</td>
                    <td className={`num px-3 py-2 text-right ${d6.up ? "text-aqi-poor" : "text-aqi-good"}`}>{d6.text}</td>
                    <td className="num px-3 py-2 text-right">{s.pm25_24h}</td>
                    <td className={`num px-3 py-2 text-right ${d24.up ? "text-aqi-very-poor" : "text-aqi-good"}`}>{d24.text}</td>
                    <td className="px-3 py-2 text-right">
                      <Spark v={[s.pm25, s.pm25_6h, s.pm25_24h]} />
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

function Spark({ v }: { v: number[] }) {
  const min = Math.min(...v), max = Math.max(...v);
  const norm = (n: number) => (max === min ? 10 : 20 - ((n - min) / (max - min)) * 16);
  const pts = v.map((n, i) => `${(i / (v.length - 1)) * 60},${norm(n)}`).join(" ");
  const up = v[v.length - 1] > v[0];
  return (
    <svg viewBox="0 0 60 20" className="ml-auto h-4 w-16">
      <polyline points={pts} fill="none" stroke={up ? "#ef4444" : "#22c55e"} strokeWidth="1.2" />
    </svg>
  );
}
