

from fastapi import APIRouter, Depends, HTTPException
from sys import path
from os.path import dirname, join

path.append(join(dirname(__file__), '..', '..', 'src'))

import sys
sys.path.append(join(dirname(__file__), '..', '..', 'src'))

from causal     import get_ate, simulate_intervention, rank_interventions, attribute_by_zone, INTERVENTIONS
from api.state  import AppState, get_state
from api.models import (
    ATEResult, ZoneATEResult, ZoneAttributionResponse,
    InterventionResult, InterventionRankingResponse,
    SimulateRequest, SimulateResponse
)

router = APIRouter(prefix="/causal", tags=["Causal Reasoning"])


@router.get("/ate", response_model=ATEResult)
async def get_global_ate(state: AppState = Depends(get_state)):
    """
    Returns the global Average Treatment Effect of industrial_plume on PM2.5.
    This is the headline causal number: "industrial plume events raise
    PM2.5 by X µg/m³ on average, after controlling for confounders."
    """
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    result = get_ate(state.dr_model, state.causal_df, bootstrap_ci=False)

    return ATEResult(
        ate      = result['ate'],
        ci_lower = result['ci_lower'],
        ci_upper = result['ci_upper'],
        n_samples= result['n_samples']
    )


@router.get("/zones", response_model=ZoneAttributionResponse)
async def get_zone_attribution(state: AppState = Depends(get_state)):
    """
    Returns ATE broken down by zone type (industrial, traffic, other).
    Tells municipal teams WHERE the industrial plume effect is strongest.
    """
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    zone_df = attribute_by_zone(state.dr_model, state.causal_df)

    zones = [
        ZoneATEResult(
            zone     = str(r['zone']),
            ate      = float(r['ate']),
            n_samples= int(r['n_samples']),
            severity = str(r['severity'])
        )
        for _, r in zone_df.iterrows()
    ]

    return ZoneAttributionResponse(city=state.city, zones=zones)


@router.get("/interventions", response_model=InterventionRankingResponse)
async def get_intervention_ranking(state: AppState = Depends(get_state)):
    """
    Returns all defined interventions ranked by estimated PM2.5 reduction.
    Most negative delta_pm25 = best intervention.

    This is the endpoint the LLM chat module and frontend alert panel
    both consume to answer "what should we deploy right now?"
    """
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    ranking_df = rank_interventions(state.dr_model, state.causal_df)

    interventions = [
        InterventionResult(
            rank            = int(idx + 1),
            intervention    = str(r['intervention']),
            description     = str(r['description']),
            ate_baseline    = float(r['ate_baseline']),
            ate_intervention= float(r['ate_intervention']),
            delta_pm25      = float(r['delta_pm25']),
            interpretation  = str(r['interpretation'])
        )
        for idx, (_, r) in enumerate(ranking_df.iterrows())
    ]

    return InterventionRankingResponse(city=state.city, interventions=interventions)


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(
    body: SimulateRequest,
    state: AppState = Depends(get_state)
):

    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    if body.intervention_name not in INTERVENTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown intervention '{body.intervention_name}'. "
                   f"Valid options: {list(INTERVENTIONS.keys())}"
        )

    result = simulate_intervention(
        state.dr_model,
        state.causal_df,
        body.intervention_name
    )

    return SimulateResponse(**result)