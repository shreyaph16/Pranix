import { createFileRoute } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { Shell } from "@/components/pranix/Shell";

export const Route = createFileRoute("/copilot")({
  head: () => ({
    meta: [
      { title: "AI Copilot — Pranix" },
      { name: "description", content: "Natural-language interface over Delhi air-quality telemetry, forecasts and policies." },
      { property: "og:title", content: "AI Copilot — Pranix" },
      { property: "og:description", content: "Conversational analytics for municipal air quality." },
    ],
  }),
  component: CopilotPage,
});

type Msg = { role: "user" | "system"; text: string; ts: string };

const seed: Msg[] = [
  { role: "system", text: "Pranix Copilot online. Ask about stations, forecasts, ATE estimates or dispatch queues.", ts: "00:12:04" },
  { role: "user", text: "Which cluster has the highest 24h projected exceedance?", ts: "00:12:37" },
  { role: "system", text: "HS-01 (North-East Corridor) — mean projected PM2.5 = 318 µg/m³ across 4 stations. Anand Vihar dominates (+29 vs. now).", ts: "00:12:38" },
];

const suggestions = [
  "Rank interventions by cost-adjusted ATE",
  "Compare Anand Vihar vs Jahangirpuri forecast",
  "Which stations breach Severe tomorrow?",
  "Explain last night’s spike in Rohini",
];

function CopilotPage() {
  const [msgs, setMsgs] = useState<Msg[]>(seed);
  const [input, setInput] = useState("");
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    boxRef.current?.scrollTo({ top: boxRef.current.scrollHeight });
  }, [msgs]);

  const send = (t: string) => {
    const text = t.trim();
    if (!text) return;
    const now = new Date().toISOString().slice(11, 19);
    setMsgs((m) => [
      ...m,
      { role: "user", text, ts: now },
      { role: "system", text: "Query queued to analytics engine. (mock) Results would appear here from your data pipeline.", ts: now },
    ]);
    setInput("");
  };

  return (
    <Shell title="AI Copilot" subtitle="model: pranix-analyst-v0 · context: 18 stations · 30d">
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-9">
          <div className="panel flex h-[70vh] flex-col">
            <div className="panel-header flex justify-between">
              <span>SESSION · #A19-DEL</span>
              <span className="text-aqi-good">● connected</span>
            </div>
            <div ref={boxRef} className="flex-1 space-y-4 overflow-auto px-4 py-4">
              {msgs.map((m, i) => (
                <div key={i} className="font-mono text-[13px]">
                  <div className="mono flex gap-2 text-[10px] uppercase tracking-widest text-muted-foreground">
                    <span>{m.ts}</span>
                    <span className={m.role === "user" ? "text-aqi-satisfactory" : "text-primary"}>
                      {m.role === "user" ? "OPERATOR" : "PRANIX"}
                    </span>
                  </div>
                  <div className={`mt-1 whitespace-pre-wrap border-l-2 pl-3 text-[13.5px] leading-relaxed ${m.role === "user" ? "border-aqi-satisfactory text-foreground" : "border-primary text-foreground/90"}`}>
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
            <form
              onSubmit={(e) => { e.preventDefault(); send(input); }}
              className="flex items-center gap-2 border-t border-border px-3 py-2"
            >
              <span className="mono text-aqi-good">›</span>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Query stations, forecasts, ATE…"
                className="mono flex-1 bg-transparent py-2 text-[13px] text-foreground placeholder:text-muted-foreground focus:outline-none"
              />
              <button className="mono border border-border-strong bg-surface-2 px-3 py-1.5 text-[10px] uppercase tracking-widest text-foreground hover:border-aqi-good hover:text-aqi-good">
                Send ↵
              </button>
            </form>
          </div>
        </div>
        <aside className="col-span-12 space-y-4 lg:col-span-3">
          <div className="panel">
            <div className="panel-header">Suggested Queries</div>
            <div className="divide-y divide-border">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="block w-full px-3 py-2 text-left text-[13px] text-muted-foreground hover:bg-surface-2 hover:text-foreground"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
          <div className="panel p-3">
            <div className="mono mb-2 text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Context Loaded</div>
            <ul className="mono space-y-1 text-[11px] text-muted-foreground">
              <li>› stations.csv (18 rows)</li>
              <li>› forecast_24h.parquet</li>
              <li>› interventions.registry</li>
              <li>› cpcb_stream · live</li>
            </ul>
          </div>
        </aside>
      </div>
    </Shell>
  );
}
