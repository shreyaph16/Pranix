
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error



LAG_HOURS = [1, 3, 6, 12, 24]

FEATURES = [
    'pm25_lag_1h', 'pm25_lag_3h', 'pm25_lag_6h', 'pm25_lag_12h', 'pm25_lag_24h',
    'pm25_roll_mean_6h', 'pm25_roll_mean_24h',
    'hour', 'day_of_week', 'month',
    'temperature_c', 'humidity_pct', 'wind_speed_kmh', 'pollution_trapped'
]


LGBM_PARAMS = dict(
    n_estimators     = 500,
    learning_rate    = 0.05,
    max_depth        = 6,
    num_leaves       = 31,
    subsample        = 0.8,
    colsample_bytree = 0.8,
    random_state     = 42,
)

TRAIN_MONTHS = [1, 2, 3, 4]   # Jan–Apr
VAL_MONTHS   = [5]             # May
TEST_MONTHS  = [6]             # Jun




def build_features(df: pd.DataFrame) -> pd.DataFrame:

   
    forecast_df = df[df['source_type'] == 'sensor'].copy()
    forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp'])
    forecast_df['pollution_trapped'] = forecast_df['pollution_trapped'].astype(int)
    forecast_df = forecast_df.sort_values(['station_name', 'timestamp'])

    # Lag features: pm25 at t-1, t-3, t-6, t-12, t-24 hours
    for lag in LAG_HOURS:
        forecast_df[f'pm25_lag_{lag}h'] = (
            forecast_df.groupby('station_name')['pm25'].shift(lag)
        )

    # Rolling means — shift(1) prevents current value leaking into the window
    forecast_df['pm25_roll_mean_6h'] = (
        forecast_df.groupby('station_name')['pm25']
        .transform(lambda x: x.shift(1).rolling(6, min_periods=1).mean())
    )
    forecast_df['pm25_roll_mean_24h'] = (
        forecast_df.groupby('station_name')['pm25']
        .transform(lambda x: x.shift(1).rolling(24, min_periods=1).mean())
    )

    # Target: PM2.5 24 hours ahead (what we want to predict)
    forecast_df['pm25_target'] = (
        forecast_df.groupby('station_name')['pm25'].shift(-24)
    )

    # Drop rows missing any lag feature or the target
    lag_cols = [f'pm25_lag_{l}h' for l in LAG_HOURS]
    df_model = forecast_df.dropna(
        subset=lag_cols + ['pm25_roll_mean_6h', 'pm25_roll_mean_24h', 'pm25_target']
    ).copy()

    print(f"[forecasting] Feature matrix: {len(df_model):,} rows · {len(FEATURES)} features")
    return df_model


def split_by_time(df_model: pd.DataFrame) -> tuple:
    """
    Time-based train/val/test split.
    Never use random split on time-series — it leaks future into training.

    Returns:
        (X_train, y_train, X_val, y_val, X_test, y_test, test_df)
        test_df is the full test slice, useful for per-station evaluation.
    """
    df_model = df_model.copy()
    df_model['timestamp'] = pd.to_datetime(df_model['timestamp'])

    train = df_model[df_model['timestamp'].dt.month.isin(TRAIN_MONTHS)]
    val   = df_model[df_model['timestamp'].dt.month.isin(VAL_MONTHS)]
    test  = df_model[df_model['timestamp'].dt.month.isin(TEST_MONTHS)]

    print(f"[forecasting] Train: {len(train):,} (Jan–Apr) | "
          f"Val: {len(val):,} (May) | Test: {len(test):,} (Jun)")

    return (
        train[FEATURES], train['pm25_target'],
        val[FEATURES],   val['pm25_target'],
        test[FEATURES],  test['pm25_target'],
        test
    )




def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    params: dict = LGBM_PARAMS
) -> lgb.LGBMRegressor:

    model = lgb.LGBMRegressor(**params)

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[
            lgb.early_stopping(50, verbose=False),
            lgb.log_evaluation(100)
        ]
    )

    print(f"[forecasting] Best iteration: {model.best_iteration_}")
    return model




def evaluate(
    model: lgb.LGBMRegressor,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    test_df: pd.DataFrame = None
) -> dict:

    y_pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

    print(f"\n[forecasting] ── Test set metrics ──────────────────")
    print(f"  MAE  : {mae:.2f} µg/m³")
    print(f"  RMSE : {rmse:.2f} µg/m³")
    print(f"  MAPE : {mape:.2f}%")
    print(f"  WHO 24hr guideline = 15 µg/m³  "
          f"({'within ✓' if mae < 15 else 'above — acceptable for 24hr horizon'})")
    print(f"[forecasting] ─────────────────────────────────────\n")

    
    if test_df is not None:
        test_df = test_df.copy()
        test_df['y_pred'] = y_pred
        print("[forecasting] Per-station MAE:")
        per_station = (
            test_df.groupby('station_name')
            .apply(lambda g: mean_absolute_error(g['pm25_target'], g['y_pred']))
            .sort_values(ascending=False)
            .round(2)
        )
        print(per_station.to_string())
        print()

    return dict(mae=mae, rmse=rmse, mape=mape, y_pred=y_pred)




def predict_next_24h(
    model: lgb.LGBMRegressor,
    df_model: pd.DataFrame,
    station_name: str
) -> dict:
  
    station_data = df_model[df_model['station_name'] == station_name]

    if station_data.empty:
        raise ValueError(f"Station '{station_name}' not found in df_model.")

    last_row = station_data.dropna(subset=FEATURES).iloc[-1]
    X = pd.DataFrame([last_row[FEATURES]])
    pm25_pred = round(float(model.predict(X)[0]), 2)
    aqi_score, aqi_category = pm25_to_aqi(pm25_pred)

    return dict(
        station        = station_name,
        predicted_pm25 = pm25_pred,
        predicted_aqi  = aqi_score,
        aqi_category   = aqi_category,
        horizon_hours  = 24
    )


def predict_all_stations(
    model: lgb.LGBMRegressor,
    df_model: pd.DataFrame
) -> pd.DataFrame:

    results = []
    for station in df_model['station_name'].unique():
        try:
            results.append(predict_next_24h(model, df_model, station))
        except Exception as e:
            print(f"[forecasting] Warning: could not predict for {station} — {e}")

    out = pd.DataFrame(results).sort_values('predicted_pm25', ascending=False)
    out = out.reset_index(drop=True)
    return out



def pm25_to_aqi(pm25: float) -> tuple[int, str]:
 
    breakpoints = [
        (0,   30,   0,   50,  'Good'),
        (30,  60,   51,  100, 'Satisfactory'),
        (60,  90,   101, 200, 'Moderate'),
        (90,  120,  201, 300, 'Poor'),
        (120, 250,  301, 400, 'Very Poor'),
        (250, 500,  401, 500, 'Severe'),
    ]
    for c_lo, c_hi, i_lo, i_hi, category in breakpoints:
        if c_lo <= pm25 <= c_hi:
            aqi = i_lo + (pm25 - c_lo) * (i_hi - i_lo) / (c_hi - c_lo)
            return round(aqi), category
    return 500, 'Severe'


#test

if __name__ == '__main__':
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'data/BWA_final.csv'
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)

    # Build features
    df_model = build_features(df)

    # Split
    X_train, y_train, X_val, y_val, X_test, y_test, test_df = split_by_time(df_model)

    # Train
    model = train_model(X_train, y_train, X_val, y_val)

    # Evaluate
    metrics = evaluate(model, X_test, y_test, test_df)

    # Predict all stations
    print("24hr forecast for all stations:")
    forecasts = predict_all_stations(model, df_model)
    print(forecasts[['station', 'predicted_pm25', 'aqi_category']].to_string(index=False))