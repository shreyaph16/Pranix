
from fastapi import APIRouter, Depends, HTTPException
from sys import path
from os.path import dirname, join

path.append(join(dirname(__file__), '..', '..', 'src'))

from forecasting import predict_next_24h, predict_all_stations
from api.state   import AppState, get_state
from api.models  import ForecastResponse, StationForecast

router = APIRouter(prefix="/forecast", tags=["24hr Forecasting"])


@router.get("", response_model=ForecastResponse)
async def get_all_forecasts(state: AppState = Depends(get_state)):

    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    forecasts_df = predict_all_stations(state.lgbm_model, state.df_model)

    forecasts = [
        StationForecast(
            station       = str(r['station']),
            predicted_pm25= round(float(r['predicted_pm25']), 2),
            predicted_aqi = int(r['predicted_aqi']),
            aqi_category  = str(r['aqi_category']),
            horizon_hours = 24
        )
        for _, r in forecasts_df.iterrows()
    ]

    return ForecastResponse(city=state.city, forecasts=forecasts)


@router.get("/{station_name}", response_model=StationForecast)
async def get_station_forecast(
    station_name: str,
    state: AppState = Depends(get_state)
):
 
    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    try:
        result = predict_next_24h(state.lgbm_model, state.df_model, station_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return StationForecast(
        station       = result['station'],
        predicted_pm25= result['predicted_pm25'],
        predicted_aqi = result['predicted_aqi'],
        aqi_category  = result['aqi_category'],
        horizon_hours = result['horizon_hours']
    )