import { createFileRoute } from "@tanstack/react-router";
import { Shell, severityBg, severityColor } from "@/components/pranix/Shell";
import { stations, hotspots } from "@/lib/pranix-data";

export const Route = createFileRoute("/map")({
  head: () => ({
    meta: [
      { title: "Hotspot Map — Pranix" },
      { name: "description", content: "Spatial view of Delhi PM2.5 station telemetry and clustered exceedance hotspots." },
      { property: "og:title", content: "Hotspot Map — Pranix" },
      { property: "og:description", content: "Spatial view of Delhi PM2.5 station telemetry." },
    ],
  }),
  component: MapPage,
});

// project lat/lng to a 100x100 viewbox
const LAT_MIN = 28.45, LAT_MAX = 28.80, LNG_MIN = 76.95, LNG_MAX = 77.35;
const px = (lng: number) => ((lng - LNG_MIN) / (LNG_MAX - LNG_MIN)) * 100;
const py = (lat: number) => (1 - (lat - LAT_MIN) / (LAT_MAX - LAT_MIN)) * 100;

function MapPage() {
  return (
    <Shell title="Hotspot Map" subtitle="18 stations · 3 active clusters · updated 12s ago">
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-9">
          <div className="panel">
            <div className="panel-header flex items-center justify-between">
              <span>DELHI-NCT · PM2.5 EXCEEDANCE MAP</span>
              <span className="text-muted-foreground">EPSG:4326 · Leaflet placeholder</span>
            </div>
            <div className="relative aspect-[4/3] w-full overflow-hidden bg-[#0a0e13]">
              {/* grid */}
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
                <defs>
                  <pattern id="g" width="5" height="5" patternUnits="userSpaceOnUse">
                    <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#161b22" strokeWidth="0.15" />
                  </pattern>
                </defs>
                <rect width="100" height="100" fill="url(#g)" />
                {/* yamuna sketch */}
                <path d="M 62 10 Q 58 40 66 60 T 72 95" stroke="#1f6feb" strokeOpacity="0.35" strokeWidth="0.6" fill="none" />
                {/* hotspot circles */}
                {hotspots.map((h) => (
                  <g key={h.id}>
                    <circle cx={px(h.centroid[1])} cy={py(h.centroid[0])} r={h.radius_km * 1.6} fill="#ef4444" fillOpacity="0.08" stroke="#ef4444" strokeOpacity="0.4" strokeWidth="0.2" strokeDasharray="0.6 0.6" />
                    <text x={px(h.centroid[1]) + 1} y={py(h.centroid[0]) - h.radius_km * 1.6 - 0.5} fontSize="1.6" fill="#ef4444" fontFamily="monospace">{h.id}</text>
                  </g>
                ))}
                {/* station markers */}
                {stations.map((s) => {
                  const color = s.band === "Severe" ? "#7c3aed" : s.band === "Very Poor" ? "#ef4444" : s.band === "Poor" ? "#f97316" : s.band === "Moderate" ? "#eab308" : "#22c55e";
                  return (
                    <g key={s.id}>
                      <circle cx={px(s.lng)} cy={py(s.lat)} r="1.1" fill={color} />
                      <circle cx={px(s.lng)} cy={py(s.lat)} r="2.4" fill={color} fillOpacity="0.15" />
                    </g>
                  );
                })}
              </svg>
              {/* corner readout */}
              <div className="mono absolute left-2 top-2 space-y-1 text-[10px] uppercase tracking-widest text-muted-foreground">
                <div>LAT {LAT_MIN}° – {LAT_MAX}°</div>
                <div>LNG {LNG_MIN}° – {LNG_MAX}°</div>
              </div>
              <div className="mono absolute bottom-2 right-2 flex gap-3 text-[10px] uppercase tracking-widest">
                {["Good","Moderate","Poor","Very Poor","Severe"].map((b) => (
                  <span key={b} className="flex items-center gap-1 text-muted-foreground">
                    <span className={`inline-block h-2 w-2 ${severityBg(b)}`} /> {b}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-12 space-y-4 lg:col-span-3">
          <div className="panel">
            <div className="panel-header">Clusters</div>
            <div className="divide-y divide-border">
              {hotspots.map((h) => (
                <div key={h.id} className="px-3 py-3">
                  <div className="mono flex justify-between text-[11px] text-muted-foreground">
                    <span>{h.id}</span><span>{h.stations} stns</span>
                  </div>
                  <div className="mt-1 text-sm">{h.label}</div>
                  <div className="num mt-1 text-lg font-medium text-aqi-very-poor">{h.mean_pm25} <span className="mono text-[10px] uppercase tracking-widest text-muted-foreground">µg/m³</span></div>
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">Station Roster</div>
            <div className="max-h-[420px] divide-y divide-border overflow-auto">
              {stations.map((s) => (
                <div key={s.id} className="flex items-center justify-between px-3 py-1.5">
                  <div className="flex items-center gap-2 text-[13px]">
                    <span className={`inline-block h-1.5 w-1.5 ${severityBg(s.band)}`} />
                    <span className="mono text-[10px] text-muted-foreground">{s.id}</span>
                    <span>{s.name}</span>
                  </div>
                  <span className={`num text-[12px] ${severityColor(s.band)}`}>{s.pm25}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Shell>
  );
}
