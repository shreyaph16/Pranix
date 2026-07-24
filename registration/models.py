from pydantic import BaseModel, Field
from typing import Optional

class HotspotStation(BaseModel):
    station_name  : str
    latitude      : float
    longitude     : float
    pm25_mean     : float
    pm25_max      : float
    record_count  : int
    cluster       : int
    severity_label: str


class ActiveHotspot(BaseModel):
    cluster_id   : int
    centroid_lat : float
    centroid_lon : float
    pm25_mean    : float
    pm25_max     : float
    station_count: int
    stations     : list[str]
    severity_label: str


class HotspotsResponse(BaseModel):
  
    city         : str
    total_clusters: int
    hotspots     : list[ActiveHotspot]
    stations     : list[HotspotStation]



class StationForecast(BaseModel):
    """24hr PM2.5 forecast for one station."""
    station       : str
    predicted_pm25: float
    predicted_aqi : int
    aqi_category  : str
    horizon_hours : int = 24


class ForecastResponse(BaseModel):
    city     : str
    forecasts: list[StationForecast]


class ATEResult(BaseModel):

    ate      : float = Field(..., description="ATE in µg/m³")
    ci_lower : Optional[float] = Field(None, description="95% CI lower bound")
    ci_upper : Optional[float] = Field(None, description="95% CI upper bound")
    n_samples: int
    treatment : str = "industrial_plume"
    outcome   : str = "pm25"


class ZoneATEResult(BaseModel):
    zone     : str
    ate      : float
    n_samples: int
    severity : str


class ZoneAttributionResponse(BaseModel):
    city : str
    zones: list[ZoneATEResult]


class InterventionResult(BaseModel):
    rank            : int
    intervention    : str
    description     : str
    ate_baseline    : float
    ate_intervention: float
    delta_pm25      : float
    interpretation  : str


class InterventionRankingResponse(BaseModel):
    city        : str
    interventions: list[InterventionResult]


class SimulateRequest(BaseModel):
    intervention_name: str = Field(
        ...,
        description="One of: water_mist_cannon, traffic_reroute, increase_wind, "
                    "remove_inversion, industrial_shutdown"
    )


class SimulateResponse(BaseModel):
    intervention    : str
    description     : str
    ate_baseline    : float
    ate_intervention: float
    delta_pm25      : float
    interpretation  : str


class ChatRequest(BaseModel):

    message         : str
    include_hotspots: bool = True
    include_forecast: bool = True
    include_causal  : bool = True


class ChatResponse(BaseModel):
    reply      : str
    model_used : str = "claude-sonnet-4-6"


class HealthResponse(BaseModel):

    status       : str = "ok"
    city         : str
    models_loaded: bool
    rows_loaded  : int