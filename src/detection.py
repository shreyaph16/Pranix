import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler



HOTSPOT_AQI_LEVELS = ['Poor', 'Very Poor', 'Severe']

DBSCAN_EPS         = 0.075
DBSCAN_MIN_SAMPLES = 3
PM25_WEIGHT        = 0.3   




def preprocess_for_clustering(df: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
   
    sensor_df = df[
        (df['source_type'] == 'sensor') &
        (df['aqi_category'].isin(HOTSPOT_AQI_LEVELS))
    ].copy()

    if sensor_df.empty:
        raise ValueError(
            f"No sensor rows with aqi_category in {HOTSPOT_AQI_LEVELS}. "
            "Check your data or HOTSPOT_AQI_LEVELS constant."
        )

    # Normalise pm25 to prevent domination of geo. distance
    scaler = StandardScaler()
    sensor_df['pm25_scaled'] = scaler.fit_transform(sensor_df[['pm25']])

    # Convert lat/lon to radians
    sensor_df['lat_rad'] = np.radians(sensor_df['latitude'])
    sensor_df['lon_rad'] = np.radians(sensor_df['longitude'])

    X       = sensor_df[['lat_rad', 'lon_rad']].values
    X_pm25  = sensor_df['pm25_scaled'].values * PM25_WEIGHT
    X_combined = np.column_stack([X, X_pm25])

    return X_combined, sensor_df


def run_dbscan(
    df: pd.DataFrame,
    eps: float = DBSCAN_EPS,
    min_samples: int = DBSCAN_MIN_SAMPLES
) -> pd.DataFrame:
    
    X_combined, sensor_df = preprocess_for_clustering(df)

    db = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean').fit(X_combined)

    sensor_df['cluster'] = db.labels_

    # Flag core points vs border points 
    core_mask = np.zeros(len(sensor_df), dtype=bool)
    core_mask[db.core_sample_indices_] = True
    sensor_df['is_core_point'] = core_mask

    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    n_noise    = list(db.labels_).count(-1)

    print(f"[detection] Clusters found : {n_clusters}")
    print(f"[detection] Noise points   : {n_noise:,} ({n_noise/len(sensor_df)*100:.1f}%)")

    return sensor_df


def get_station_summary(sensor_df: pd.DataFrame) -> pd.DataFrame:
    
    if 'cluster' not in sensor_df.columns:
        raise ValueError("sensor_df must have a 'cluster' column. Run run_dbscan() first.")

    summary = sensor_df.groupby('station_name').agg(
        latitude     = ('latitude',  'first'),
        longitude    = ('longitude', 'first'),
        pm25_mean    = ('pm25',      'mean'),
        pm25_max     = ('pm25',      'max'),
        record_count = ('pm25',      'count'),
        cluster      = ('cluster',   lambda x: x.mode()[0])
    ).reset_index()

    #severity label based on mean PM2.5
    summary['severity_label'] = summary['pm25_mean'].apply(_pm25_to_severity)

    return summary.sort_values('pm25_mean', ascending=False).round(2)


def flag_active_hotspots(sensor_df: pd.DataFrame, lookback_hours: int = 3) -> pd.DataFrame:
    
    if 'cluster' not in sensor_df.columns:
        raise ValueError("sensor_df must have a 'cluster' column. Run run_dbscan() first.")

    sensor_df = sensor_df.copy()
    sensor_df['timestamp'] = pd.to_datetime(sensor_df['timestamp'])

    cutoff = sensor_df['timestamp'].max() - pd.Timedelta(hours=lookback_hours)
    recent = sensor_df[sensor_df['timestamp'] >= cutoff]

    # Only real clusters 
    active = recent[recent['cluster'] != -1]

    if active.empty:
        print(f"[detection] No active hotspots in last {lookback_hours} hours.")
        return pd.DataFrame()

    hotspots = active.groupby('cluster').agg(
        centroid_lat  = ('latitude',  'mean'),
        centroid_lon  = ('longitude', 'mean'),
        pm25_mean     = ('pm25',      'mean'),
        pm25_max      = ('pm25',      'max'),
        station_count = ('station_name', 'nunique'),
        stations      = ('station_name', lambda x: list(x.unique())),
        hotspot_type  = ('hotspot_type', lambda x: x.mode()[0] if 'hotspot_type' in x.index else 'unknown')
    ).reset_index()

    hotspots['severity_label'] = hotspots['pm25_mean'].apply(_pm25_to_severity)
    hotspots = hotspots.sort_values('pm25_mean', ascending=False).reset_index(drop=True)

    print(f"[detection] Active hotspots: {len(hotspots)}")
    return hotspots



def _pm25_to_severity(pm25: float) -> str:
    """Map mean PM2.5 µg/m³ to CPCB AQI severity label."""
    if pm25 <= 30:   return 'Good'
    elif pm25 <= 60: return 'Satisfactory'
    elif pm25 <= 90: return 'Moderate'
    elif pm25 <= 120: return 'Poor'
    elif pm25 <= 250: return 'Very Poor'
    else:             return 'Severe'



if __name__ == '__main__':
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'data/BWA_final.csv'
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)

    sensor_df   = run_dbscan(df)
    summary     = get_station_summary(sensor_df)
    hotspots    = flag_active_hotspots(sensor_df, lookback_hours=3)

    print("\nStation summary:")
    print(summary[['station_name', 'pm25_mean', 'cluster', 'severity_label']].to_string(index=False))

    print("\nActive hotspots:")
    print(hotspots[['cluster', 'centroid_lat', 'centroid_lon', 'pm25_mean', 'severity_label', 'stations']].to_string(index=False))