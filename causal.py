"""
causal.py — CleanAir & Clear Streets
Causal reasoning layer: root cause attribution and intervention ATE estimation.

This is the differentiating layer of the pipeline. While detection.py finds
hotspots and forecasting.py predicts future PM2.5, this module answers:
  - "Why did this spike happen?" (root cause attribution via DoWhy)
  - "What is the causal effect of this pollution source on PM2.5?" (EconML DR Learner)
  - "What would PM2.5 look like if we deployed intervention X?" (counterfactual sim)
  - "Which intervention gives the highest PM2.5 reduction?" (ranked recommendations)

Usage:
    from causal import build_causal_dataset, fit_dr_learner, get_ate,
                       simulate_intervention, rank_interventions, run_dowhy_refutation
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from dowhy import CausalModel
from econml.dr import DRLearner
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LassoCV


CONFOUNDERS = [
    'wind_speed_kmh',     
    'humidity_pct',         
    'temperature_c',        
    'pollution_trapped',    
    'hour',                
    'month',               
    'wind_direction_deg',   
    'zone_industrial',     
    'zone_traffic',
]


CAUSAL_GRAPH = """digraph {
    industrial_plume -> pm25;
    wind_speed_kmh -> pm25;
    wind_speed_kmh -> industrial_plume;
    humidity_pct -> pm25;
    temperature_c -> pm25;
    temperature_c -> industrial_plume;
    pollution_trapped -> pm25;
    pollution_trapped -> industrial_plume;
    hour -> pm25;
    hour -> industrial_plume;
    month -> pm25;
    month -> industrial_plume;
    wind_direction_deg -> pm25;
    wind_direction_deg -> industrial_plume;
    zone_industrial -> pm25;
    zone_industrial -> industrial_plume;
    zone_traffic -> pm25;
}"""


INTERVENTIONS = {
    'water_mist_cannon': {
        'description': 'Deploy water-mist cannon — suppresses coarse PM, raises humidity',
        'changes': {'humidity_pct': lambda x: np.minimum(x + 15, 100)},
    },
    'traffic_reroute': {
        'description': 'Reroute traffic away from junction — removes mobile source',
        'changes': {'zone_traffic': 0},
    },
    'increase_wind': {
        'description': 'Simulate 5 km/h wind speed increase (natural dispersal)',
        'changes': {'wind_speed_kmh': lambda x: x + 5.0},
    },
    'remove_inversion': {
        'description': 'Remove temperature inversion — allows vertical mixing',
        'changes': {'pollution_trapped': 0},
    },
    'industrial_shutdown': {
        'description': 'Temporary industrial shutdown — removes stationary source',
        'changes': {'zone_industrial': 0, 'industrial_plume': 0},
    },
}




def build_causal_dataset(df: pd.DataFrame) -> pd.DataFrame:
      
    sensor_df = df[df['source_type'] == 'sensor'].copy()
    sensor_df['industrial_plume'] = sensor_df['industrial_plume'].astype(int)
    sensor_df['fire_flag']        = sensor_df['fire_flag'].astype(int)
    sensor_df['pollution_trapped']= sensor_df['pollution_trapped'].astype(int)

    # Encode zone_type as binary columns (treatment/confounder interaction)
    sensor_df['zone_industrial'] = (sensor_df['zone_type'] == 'industrial').astype(int)
    sensor_df['zone_traffic']    = (sensor_df['zone_type'] == 'traffic').astype(int)

    keep_cols = ['pm25', 'industrial_plume', 'fire_flag', 'station_name'] + CONFOUNDERS
    causal_df = sensor_df[keep_cols].dropna().copy()

    n_treated = causal_df['industrial_plume'].sum()
    n_control = (causal_df['industrial_plume'] == 0).sum()

    print(f"[causal] Dataset: {len(causal_df):,} rows")
    print(f"[causal] Treatment=1 (industrial plume): {n_treated:,} ({n_treated/len(causal_df)*100:.1f}%)")
    print(f"[causal] Treatment=0 (no plume):         {n_control:,} ({n_control/len(causal_df)*100:.1f}%)")

    return causal_df




def fit_dr_learner(causal_df: pd.DataFrame) -> DRLearner:
  
    X = causal_df[CONFOUNDERS].values
    T = causal_df['industrial_plume'].values
    Y = causal_df['pm25'].values

    dr = DRLearner(
        model_propensity = GradientBoostingClassifier(
            n_estimators=100, random_state=42
        ),
        model_regression = GradientBoostingRegressor(
            n_estimators=100, random_state=42
        ),
        model_final = LassoCV(cv=3),
        random_state=42
    )

    dr.fit(Y, T, X=X, W=None)

    ate = dr.ate(X=X)
    print(f"[causal] DR Learner fitted.")
    print(f"[causal] Global ATE (industrial_plume → pm25): {ate:+.2f} µg/m³")
    print(f"[causal] Interpretation: industrial plume events raise PM2.5 by "
          f"~{abs(ate):.1f} µg/m³ on average, after controlling for confounders.")

    return dr


def get_ate(
    dr: DRLearner,
    causal_df: pd.DataFrame,
    subset_mask: pd.Series = None,
    bootstrap_ci: bool = False,
    n_bootstrap: int = 30 ) -> dict:
  
    df_sub = causal_df if subset_mask is None else causal_df[subset_mask]
    X_sub  = df_sub[CONFOUNDERS].values
    Y_sub  = df_sub['pm25'].values
    T_sub  = df_sub['industrial_plume'].values

    ate = float(dr.ate(X=X_sub))
    ci_lower, ci_upper = None, None

    if bootstrap_ci:
        print(f"[causal] Running {n_bootstrap} bootstrap iterations for 95% CI...")
        boot_ates = []
        np.random.seed(42)
        for _ in range(n_bootstrap):
            idx = np.random.choice(len(Y_sub), len(Y_sub), replace=True)
            dr_b = DRLearner(
                model_propensity=GradientBoostingClassifier(n_estimators=50, random_state=0),
                model_regression=GradientBoostingRegressor(n_estimators=50, random_state=0),
                model_final=LassoCV(cv=3),
                random_state=0
            )
            dr_b.fit(Y_sub[idx], T_sub[idx], X=X_sub[idx], W=None)
            boot_ates.append(float(dr_b.ate(X=X_sub[idx])))
        ci_lower = float(np.percentile(boot_ates, 2.5))
        ci_upper = float(np.percentile(boot_ates, 97.5))

    return dict(
        ate      = round(ate, 2),
        ci_lower = round(ci_lower, 2) if ci_lower is not None else None,
        ci_upper = round(ci_upper, 2) if ci_upper is not None else None,
        n_samples= len(df_sub)
    )




def simulate_intervention(
    dr: DRLearner,
    causal_df: pd.DataFrame,
    intervention_name: str
) -> dict:
 
    if intervention_name not in INTERVENTIONS:
        raise ValueError(
            f"Unknown intervention '{intervention_name}'. "
            f"Available: {list(INTERVENTIONS.keys())}"
        )

    config   = INTERVENTIONS[intervention_name]
    X_base   = causal_df[CONFOUNDERS].copy()
    X_inter  = X_base.copy()

    for col, val in config['changes'].items():
        if col not in X_inter.columns:
            continue
        if callable(val):
            X_inter[col] = val(X_inter[col].values)
        else:
            X_inter[col] = val

    ate_base  = float(dr.ate(X=X_base.values))
    ate_inter = float(dr.ate(X=X_inter.values))
    delta     = ate_inter - ate_base

    result = dict(
        intervention    = intervention_name,
        description     = config['description'],
        ate_baseline    = round(ate_base, 2),
        ate_intervention= round(ate_inter, 2),
        delta_pm25      = round(delta, 2),
        interpretation  = (
            f"This intervention {'reduces' if delta < 0 else 'increases'} the "
            f"causal effect of industrial plume on PM2.5 by "
            f"{abs(delta):.1f} µg/m³ on average."
        )
    )

    return result


def rank_interventions(
    dr: DRLearner,
    causal_df: pd.DataFrame
) -> pd.DataFrame:
   
    results = []
    for name in INTERVENTIONS:
        result = simulate_intervention(dr, causal_df, name)
        results.append(result)

    ranking = pd.DataFrame(results).sort_values('delta_pm25').reset_index(drop=True)
    ranking.index += 1  # rank starts at 1

    print("\n[causal] ── Intervention ranking (best → worst) ──────────────")
    for _, row in ranking.iterrows():
        print(f"  {_}. {row['intervention']:<25} Δ PM2.5 = {row['delta_pm25']:+.2f} µg/m³")
    print("[causal] ─────────────────────────────────────────────────────\n")

    return ranking


def run_dowhy_refutation(
    causal_df: pd.DataFrame,
    num_simulations: int = 5
) -> dict:
 
    print("[causal] Running DoWhy refutation test...")

    dowhy_model = CausalModel(
        data      = causal_df,
        treatment = 'industrial_plume',
        outcome   = 'pm25',
        graph     = CAUSAL_GRAPH
    )

    identified = dowhy_model.identify_effect(proceed_when_unidentifiable=True)
    estimate   = dowhy_model.estimate_effect(
        identified,
        method_name="backdoor.linear_regression"
    )

    refutation = dowhy_model.refute_estimate(
        identified, estimate,
        method_name="random_common_cause",
        num_simulations=num_simulations
    )

    original_effect = round(float(estimate.value), 2)
    refuted_effect  = round(float(refutation.new_effect), 2)
    relative_change = abs(refuted_effect - original_effect) / abs(original_effect)
    passed          = relative_change < 0.1  # < 10% change = robust

    print(f"[causal] Original effect : {original_effect:.2f} µg/m³")
    print(f"[causal] Refuted effect  : {refuted_effect:.2f} µg/m³")
    print(f"[causal] Relative change : {relative_change*100:.1f}%")
    print(f"[causal] Refutation {'PASSED ✓' if passed else 'FAILED ✗ — review your DAG'}")

    return dict(
        original_effect = original_effect,
        refuted_effect  = refuted_effect,
        relative_change = round(relative_change, 4),
        passed          = passed
    )



def attribute_by_zone(dr: DRLearner, causal_df: pd.DataFrame) -> pd.DataFrame:
   
    zones = {
        'industrial': causal_df['zone_industrial'] == 1,
        'traffic'   : causal_df['zone_traffic']    == 1,
        'other'     : (causal_df['zone_industrial'] == 0) & (causal_df['zone_traffic'] == 0),
    }

    rows = []
    for zone_name, mask in zones.items():
        result = get_ate(dr, causal_df, subset_mask=mask)
        result['zone'] = zone_name
        rows.append(result)

    out = pd.DataFrame(rows)[['zone','ate','n_samples']].copy()
    out['severity'] = out['ate'].apply(
        lambda x: 'High' if x > 60 else ('Medium' if x > 30 else 'Low')
    )
    out = out.sort_values('ate', ascending=False).reset_index(drop=True)
    return out



if __name__ == '__main__':
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'data/BWA_final.csv'
    print(f"Loading {csv_path} ...")
    df = pd.read_csv(csv_path)


    causal_df = build_causal_dataset(df)


    dr = fit_dr_learner(causal_df)

  
    print("\nGlobal ATE (with 95% bootstrap CI):")
    ate_result = get_ate(dr, causal_df, bootstrap_ci=True, n_bootstrap=30)
    print(f"  ATE = {ate_result['ate']} µg/m³  "
          f"95% CI: [{ate_result['ci_lower']}, {ate_result['ci_upper']}]")


    print("\nATE by zone:")
    zone_df = attribute_by_zone(dr, causal_df)
    print(zone_df.to_string(index=False))


    ranking = rank_interventions(dr, causal_df)
    print(ranking[['intervention','description','delta_pm25']].to_string(index=False))


    refutation = run_dowhy_refutation(causal_df, num_simulations=5)