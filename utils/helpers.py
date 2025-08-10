# utils/helpers.py
from pathlib import Path
from joblib import load

SQFT_TO_M2 = 0.092903

def sqft_to_m2(sqft):
    return sqft * SQFT_TO_M2

def w_to_kw(w):
    return w / 1000.0

def compute_efficiency_pct(panel_output_w, panel_area_m2):
    """
    Efficiency (%) = (panel_output_power (W) / (panel_area (m^2) * 1000 (W/m^2))) * 100
    => = (panel_output_w / (panel_area_m2 * 1000)) * 100
    """
    if panel_area_m2 <= 0:
        return 0.0
    return (panel_output_w / (panel_area_m2 * 1000.0)) * 100.0

# load model
MODEL_PATH = Path("models/energy_model.pkl")
if not MODEL_PATH.exists():
    model = None
else:
    model = load(str(MODEL_PATH))

def predict_expected_output(panel_kw, sunlight_hours, efficiency_pct):
    """
    Uses the regression model if available. Otherwise uses physics formula:
      expected_kwh = panel_kw * sunlight_hours * (efficiency_pct / 100.0) * performance_ratio
    We'll use a default performance ratio of 0.85 when falling back to formula.
    """
    if model is not None:
        X = [[panel_kw, sunlight_hours, efficiency_pct]]
        pred = model.predict(X)[0]
        return max(pred, 0.0)  # avoid negative
    else:
        perf_ratio = 0.85
        return max(panel_kw * sunlight_hours * (efficiency_pct / 100.0) * perf_ratio, 0.0)