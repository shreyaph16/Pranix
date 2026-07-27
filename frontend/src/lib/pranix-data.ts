export type Station = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  pm25: number;
  pm25_6h: number;
  pm25_24h: number;
  band: "Good" | "Satisfactory" | "Moderate" | "Poor" | "Very Poor" | "Severe";
};

export const stations: Station[] = [
  { id: "DL001", name: "Anand Vihar", lat: 28.6469, lng: 77.3154, pm25: 342, pm25_6h: 358, pm25_24h: 371, band: "Severe" },
  { id: "DL002", name: "R.K. Puram", lat: 28.5636, lng: 77.1735, pm25: 287, pm25_6h: 301, pm25_24h: 315, band: "Very Poor" },
  { id: "DL003", name: "Punjabi Bagh", lat: 28.6742, lng: 77.1310, pm25: 268, pm25_6h: 279, pm25_24h: 288, band: "Very Poor" },
  { id: "DL004", name: "ITO", lat: 28.6289, lng: 77.2410, pm25: 254, pm25_6h: 262, pm25_24h: 271, band: "Very Poor" },
  { id: "DL005", name: "Dwarka Sector-8", lat: 28.5710, lng: 77.0710, pm25: 231, pm25_6h: 240, pm25_24h: 249, band: "Very Poor" },
  { id: "DL006", name: "Rohini", lat: 28.7360, lng: 77.1210, pm25: 219, pm25_6h: 227, pm25_24h: 234, band: "Very Poor" },
  { id: "DL007", name: "Jahangirpuri", lat: 28.7325, lng: 77.1706, pm25: 312, pm25_6h: 325, pm25_24h: 338, band: "Severe" },
  { id: "DL008", name: "Bawana", lat: 28.7761, lng: 77.0357, pm25: 298, pm25_6h: 305, pm25_24h: 314, band: "Very Poor" },
  { id: "DL009", name: "Wazirpur", lat: 28.6960, lng: 77.1650, pm25: 276, pm25_6h: 284, pm25_24h: 293, band: "Very Poor" },
  { id: "DL010", name: "Mundka", lat: 28.6820, lng: 77.0290, pm25: 289, pm25_6h: 298, pm25_24h: 307, band: "Very Poor" },
  { id: "DL011", name: "Nehru Nagar", lat: 28.5679, lng: 77.2506, pm25: 245, pm25_6h: 251, pm25_24h: 259, band: "Very Poor" },
  { id: "DL012", name: "Patparganj", lat: 28.6280, lng: 77.2919, pm25: 261, pm25_6h: 270, pm25_24h: 278, band: "Very Poor" },
  { id: "DL013", name: "Sirifort", lat: 28.5502, lng: 77.2166, pm25: 198, pm25_6h: 205, pm25_24h: 213, band: "Poor" },
  { id: "DL014", name: "Mandir Marg", lat: 28.6360, lng: 77.2010, pm25: 187, pm25_6h: 194, pm25_24h: 201, band: "Poor" },
  { id: "DL015", name: "Lodhi Road", lat: 28.5918, lng: 77.2273, pm25: 176, pm25_6h: 182, pm25_24h: 190, band: "Poor" },
  { id: "DL016", name: "Aya Nagar", lat: 28.4707, lng: 77.1341, pm25: 142, pm25_6h: 149, pm25_24h: 156, band: "Moderate" },
  { id: "DL017", name: "IGI Airport T3", lat: 28.5562, lng: 77.1000, pm25: 165, pm25_6h: 171, pm25_24h: 178, band: "Poor" },
  { id: "DL018", name: "Najafgarh", lat: 28.6094, lng: 76.9800, pm25: 208, pm25_6h: 216, pm25_24h: 224, band: "Poor" },
];

export const hotspots = [
  { id: "HS-01", label: "North-East Corridor", centroid: [28.71, 77.19], radius_km: 4.2, stations: 4, mean_pm25: 305 },
  { id: "HS-02", label: "Trans-Yamuna Belt", centroid: [28.64, 77.30], radius_km: 3.1, stations: 3, mean_pm25: 278 },
  { id: "HS-03", label: "West Industrial Arc", centroid: [28.70, 77.07], radius_km: 5.6, stations: 4, mean_pm25: 269 },
];

export const interventions = [
  { id: "INT-01", name: "Water Sprinkling — Anand Vihar", target: "DL001", est_reduction: 42, ate: -38.4, ci: [-46.1, -30.7], cost: 1.2, confidence: 0.91 },
  { id: "INT-02", name: "Truck Rerouting — NH-9", target: "HS-02", est_reduction: 31, ate: -27.8, ci: [-33.9, -21.7], cost: 0.4, confidence: 0.86 },
  { id: "INT-03", name: "Construction Halt — Rohini", target: "DL006", est_reduction: 28, ate: -24.1, ci: [-30.2, -18.0], cost: 2.8, confidence: 0.78 },
  { id: "INT-04", name: "Smog Tower Boost — Jahangirpuri", target: "DL007", est_reduction: 22, ate: -19.5, ci: [-25.0, -14.0], cost: 3.1, confidence: 0.72 },
  { id: "INT-05", name: "Diesel Genset Ban — Bawana", target: "DL008", est_reduction: 19, ate: -16.9, ci: [-22.4, -11.4], cost: 0.9, confidence: 0.81 },
  { id: "INT-06", name: "Mechanized Sweeping — ITO", target: "DL004", est_reduction: 14, ate: -12.2, ci: [-17.0, -7.4], cost: 0.6, confidence: 0.77 },
  { id: "INT-07", name: "Biomass Alert — Peri-Urban", target: "HS-03", est_reduction: 11, ate: -9.6, ci: [-14.3, -4.9], cost: 0.3, confidence: 0.69 },
];

export const modules = [
  { to: "/map", code: "01", title: "Hotspot Map", desc: "Spatial clustering of PM2.5 exceedance zones across the NCT.", stat: "3 clusters" },
  { to: "/forecast", code: "02", title: "AQI Forecast", desc: "6h / 24h station-level PM2.5 predictions from ensemble model.", stat: "18 stations" },
  { to: "/causal", code: "03", title: "Causal Lab", desc: "Estimate ATE of interventions using doubly-robust estimators.", stat: "ATE −27.8" },
  { to: "/alerts", code: "04", title: "Alert Center", desc: "Ranked, cost-aware intervention queue for field dispatch.", stat: "7 open" },
  { to: "/copilot", code: "05", title: "AI Copilot", desc: "Natural-language interface over stations, forecasts, and policies.", stat: "online" },
] as const;