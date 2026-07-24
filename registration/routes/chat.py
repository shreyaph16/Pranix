
import os
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException

from api.state  import AppState, get_state
from api.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["LLM Analyst"])

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL             = "claude-sonnet-4-6"


def _build_system_prompt(state: AppState) -> str:

    lines = [
        "You are CleanAir Analyst, an AI assistant for municipal air quality "
        f"teams in {state.city}, India.",
        "You have access to live outputs from three ML models. Ground every "
        "answer in this data. Be concise and use plain language — your audience "
        "is municipal officers, not data scientists.",
        "",
    ]

    if state.station_summary is not None:
        lines.append("ACTIVE HOTSPOT CLUSTERS (DBSCAN detection):")
        summary = state.station_summary.sort_values('pm25_mean', ascending=False)
        for _, r in summary.iterrows():
            cluster_label = f"Cluster {r['cluster']}" if r['cluster'] != -1 else "Noise"
            lines.append(
                f"  {r['station_name']} | {cluster_label} | "
                f"Mean PM2.5: {r['pm25_mean']:.1f} µg/m³ | "
                f"Max: {r['pm25_max']:.1f} | Severity: {r['severity_label']}"
            )
        lines.append("")

    if state.lgbm_model is not None and state.df_model is not None:
        from forecasting import predict_all_stations
        forecasts = predict_all_stations(state.lgbm_model, state.df_model)
        lines.append("24HR PM2.5 FORECAST (LightGBM):")
        for _, r in forecasts.iterrows():
            lines.append(
                f"  {r['station']} | Predicted: {r['predicted_pm25']:.1f} µg/m³ | "
                f"AQI: {r['predicted_aqi']} ({r['aqi_category']})"
            )
        lines.append("")

    if state.dr_model is not None and state.causal_df is not None:
        from causal import get_ate, rank_interventions
        ate_result = get_ate(state.dr_model, state.causal_df)
        lines.append(
            f"CAUSAL ANALYSIS (EconML DR Learner):\n"
            f"  Industrial plume ATE on PM2.5: +{ate_result['ate']:.1f} µg/m³ "
            f"(n={ate_result['n_samples']:,})"
        )
        ranking = rank_interventions(state.dr_model, state.causal_df)
        lines.append("  Intervention ranking (best → worst):")
        for _, r in ranking.iterrows():
            lines.append(
                f"    {r['intervention']}: Δ PM2.5 = {r['delta_pm25']:+.1f} µg/m³"
            )
        lines.append("")

    lines.append(
        "If asked about something not covered by the above data, say so clearly. "
        "Never invent numbers. Cite which model produced each figure when relevant."
    )

    return "\n".join(lines)


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    state: AppState = Depends(get_state)
):
 
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not set. Add it to your .env file."
        )

    system_prompt = _build_system_prompt(state)

    payload = {
        "model"     : MODEL,
        "max_tokens": 1024,
        "system"    : system_prompt,
        "messages"  : [{"role": "user", "content": body.message}]
    }


    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key"        : api_key,
                "anthropic-version": "2023-06-01",
                "content-type"     : "application/json"
            },
            json=payload
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,   # 502 = Bad Gateway (upstream API failed)
            detail=f"Anthropic API error {resp.status_code}: {resp.text}"
        )

    data  = resp.json()
    reply = data["content"][0]["text"]

    return ChatResponse(reply=reply, model_used=MODEL)