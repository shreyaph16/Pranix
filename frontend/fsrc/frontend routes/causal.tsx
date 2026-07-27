import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Shell } from "@/components/pranix/Shell";
import { interventions } from "@/lib/pranix-data";

export const Route = createFileRoute("/causal")({
  head: () => ({
    meta: [
      { title: "Causal Lab — Pranix" },
      { name: "description", content: "Estimate average treatment effects of pollution interventions with doubly-robust methods." },
      { property: "og:title", content: "Causal Lab — Pranix" },
      { property: "og:description", content: "ATE estimation for air-quality interventions." },
    ],
  }),
  component: CausalPage,
});

function CausalPage() {
  const [id, setId] = useState(interventions[0].id);
  const int = interventions.find((i) => i.id === id)!;

  return (
    <Shell title="Causal Lab" subtitle="Doubly-robust ATE · propensity model: logit-L2 · outcome: rf-500">
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-4">
          <div className="panel p-4">
            <label className="mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Intervention</label>
            <select
              value={id}
              onChange={(e) => setId(e.target.value)}
              className="mono mt-2 w-full border border-border-strong bg-surface-2 px-3 py-2 text-[13px] text-foreground focus:border-aqi-good focus:outline-none"
            >
              {interventions.map((i) => (
                <option key={i.id} value={i.id}>{i.id} — {i.name}</option>
              ))}
            </select>
            <div className="mono mt-4 space-y-2 text-[11px] uppercase tracking-widest text-muted-foreground">
              <Row k="Target" v={int.target} />
              <Row k="Cost (₹ Cr)" v={int.cost.toFixed(2)} />
              <Row k="Confidence" v={`${(int.confidence * 100).toFixed(0)}%`} />
              <Row k="Est. reduction" v={`${int.est_reduction} µg/m³`} />
            </div>
          </div>
        </div>

        <div className="col-span-12 lg:col-span-8">
          <div className="panel p-8">
            <div className="mono flex items-center justify-between text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <span>Average Treatment Effect · ΔPM2.5</span>
              <span>n = 74,178 · bootstrap 1,000</span>
            </div>
            <div className="mt-6 flex items-end gap-4">
              <div className="num text-7xl font-semibold tracking-tight text-aqi-good md:text-8xl">
                {int.ate.toFixed(1)}
              </div>
              <div className="mono pb-4 text-[11px] uppercase tracking-widest text-muted-foreground">µg/m³</div>
            </div>
            <div className="mono mt-3 text-[12px] text-muted-foreground">
              95% CI [{int.ci[0].toFixed(1)}, {int.ci[1].toFixed(1)}] · p &lt; 0.01
            </div>

            {/* CI bar */}
            <div className="mt-8">
              <div className="relative h-8 border border-border bg-surface-2">
                <div className="absolute inset-y-0 left-1/2 w-px bg-border-strong" />
                <CIBar lo={int.ci[0]} hi={int.ci[1]} point={int.ate} />
              </div>
              <div className="mono mt-1 flex justify-between text-[10px] uppercase tracking-widest text-muted-foreground">
                <span>−60</span><span>0</span><span>+60</span>
              </div>
            </div>
          </div>

          <div className="panel mt-4">
            <div className="panel-header">Estimator diagnostics</div>
            <table className="w-full text-[13px]">
              <tbody>
                {[
                  ["Method", "Doubly-robust AIPW"],
                  ["Propensity balance", "SMD < 0.08 across 14 covariates"],
                  ["Positivity", "0.03 ≤ e(x) ≤ 0.97"],
                  ["Sensitivity (Γ)", "1.4 — moderate robustness to unobserved confounding"],
                  ["Placebo test", "null effect on pre-treatment period (p = 0.42)"],
                ].map(([k, v]) => (
                  <tr key={k} className="border-b border-border">
                    <td className="mono w-56 px-3 py-2 text-[11px] uppercase tracking-widest text-muted-foreground">{k}</td>
                    <td className="px-3 py-2">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Shell>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between border-b border-border pb-1.5">
      <span>{k}</span>
      <span className="num text-foreground">{v}</span>
    </div>
  );
}

function CIBar({ lo, hi, point }: { lo: number; hi: number; point: number }) {
  const toPct = (v: number) => ((v + 60) / 120) * 100;
  return (
    <>
      <div className="absolute inset-y-2 bg-aqi-good/25" style={{ left: `${toPct(lo)}%`, width: `${toPct(hi) - toPct(lo)}%` }} />
      <div className="absolute inset-y-0 w-0.5 bg-aqi-good" style={{ left: `${toPct(point)}%` }} />
    </>
  );
}
