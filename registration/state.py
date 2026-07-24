
import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from detection   import run_dbscan, get_station_summary, flag_active_hotspots
from forecasting import build_features, split_by_time, train_model
from causal      import build_causal_dataset, fit_dr_learner


class AppState:
    """
    Holds every expensive object that should only be created once.

    """

    def __init__(self):
        
        self.df            : pd.DataFrame | None = None
        self.city          : str = "Delhi"
        self.rows_loaded   : int = 0

       
        self.sensor_df     : pd.DataFrame | None = None  # post-DBSCAN labelled
        self.station_summary: pd.DataFrame | None = None

  
        self.lgbm_model    = None   # fitted LGBMRegressor
        self.df_model      : pd.DataFrame | None = None  # feature-engineered
        self.forecast_features: list[str] = []

       
        self.dr_model      = None   # fitted DRLearner
        self.causal_df     : pd.DataFrame | None = None

      
        self.models_loaded : bool = False



app_state = AppState()


async def startup(csv_path: str = "data/BWA_final.csv"):

    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pollution_trapped'] = df['pollution_trapped'].astype(int)
    df['industrial_plume']  = df['industrial_plume'].astype(int)

    app_state.df          = df
    app_state.rows_loaded = len(df)
  


    app_state.sensor_df      = run_dbscan(df)
    app_state.station_summary = get_station_summary(app_state.sensor_df)
    

   
    print("[startup] Building features and training LightGBM...")
    df_model = build_features(df)
    X_train, y_train, X_val, y_val, _, _, _ = split_by_time(df_model)
    app_state.lgbm_model       = train_model(X_train, y_train, X_val, y_val)
    app_state.df_model         = df_model
    print("[startup] LightGBM trained")

    print("[startup] Fitting DR Learner (this takes ~30s)...")
    app_state.causal_df = build_causal_dataset(df)
    app_state.dr_model  = fit_dr_learner(app_state.causal_df)
    print("[startup] DR Learner fitted")

    app_state.models_loaded = True
    print("[startup]  All models ready — API is live")


def get_state() -> AppState:
    return app_state