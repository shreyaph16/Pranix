
from fastapi import APIRouter, Depends, HTTPException
from sys import path
from os.path import dirname, join

path.append(join(dirname(__file__), '..', '..', 'src'))

from detection import flag_active_hotspots
from api.state  import AppState, get_state
from api.models import (
    HotspotsResponse, ActiveHotspot, HotspotStation
)

router = APIRouter(prefix="/hotspots", tags=["Hotspot Detection"])


@router.get("", response_model=HotspotsResponse)
async def get_hotspots(
    lookback_hours: int = 3,
    state: AppState = Depends(get_state)
  
):
    """
    Returns all active pollution hotspots detected by DBSCAN,
    filtered to readings within the last `lookback_hours` hours.
    """
    if not state.models_loaded:

        raise HTTPException(status_code=503, detail="Models not yet loaded")

    active = flag_active_hotspots(state.sensor_df, lookback_hours=lookback_hours)
    summary = state.station_summary

    hotspot_list = []
    if not active.empty:
        for _, row in active.iterrows():
            hotspot_list.append(ActiveHotspot(
                cluster_id    = int(row['cluster']),
                centroid_lat  = round(float(row['centroid_lat']), 5),
                centroid_lon  = round(float(row['centroid_lon']), 5),
                pm25_mean     = round(float(row['pm25_mean']), 2),
                pm25_max      = round(float(row['pm25_max']), 2),
                station_count = int(row['station_count']),
                stations      = list(row['stations']),
                severity_label= str(row['severity_label'])
            ))

    station_list = [
        HotspotStation(
            station_name  = str(r['station_name']),
            latitude      = round(float(r['latitude']), 5),
            longitude     = round(float(r['longitude']), 5),
            pm25_mean     = round(float(r['pm25_mean']), 2),
            pm25_max      = round(float(r['pm25_max']), 2),
            record_count  = int(r['record_count']),
            cluster       = int(r['cluster']),
            severity_label= str(r['severity_label'])
        )
        for _, r in summary.iterrows()
    ]

    return HotspotsResponse(
        city          = state.city,
        total_clusters= len(hotspot_list),
        hotspots      = hotspot_list,
        stations      = station_list
    )


@router.get("/{station_name}", response_model=HotspotStation)
async def get_station_hotspot(
    station_name: str,
    state: AppState = Depends(get_state)
):

    if not state.models_loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded")

    summary = state.station_summary
    match = summary[summary['station_name'].str.lower() == station_name.lower()]

    if match.empty:
      
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_name}' not found. "
                   f"Available: {summary['station_name'].tolist()}"
        )

    r = match.iloc[0]
    return HotspotStation(
        station_name  = str(r['station_name']),
        latitude      = round(float(r['latitude']), 5),
        longitude     = round(float(r['longitude']), 5),
        pm25_mean     = round(float(r['pm25_mean']), 2),
        pm25_max      = round(float(r['pm25_max']), 2),
        record_count  = int(r['record_count']),
        cluster       = int(r['cluster']),
        severity_label= str(r['severity_label'])
    )