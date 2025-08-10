# model_training.py
import numpy as np
from sklearn.linear_model import LinearRegression
from joblib import dump
from pathlib import Path

# create folder
Path("models").mkdir(exist_ok=True)

rng = np.random.default_rng(42)
n = 5000

# features ranges:
# panel power in kW (0.08 kW = 80 W  to 0.6 kW = 600 W)
panel_kw = rng.uniform(0.08, 0.6, n)

# sunlight hours (equivalent full-sun hours) 1.5 to 8.0
sun_hours = rng.uniform(1.5, 8.0, n)

# panel efficiency % (8% to 22%)
eff_pct = rng.uniform(8.0, 22.0, n)

# Assume performance ratio (losses) 0.75-0.9, include randomness
perf_ratio = rng.uniform(0.75, 0.9, n)

# true daily output (kWh/day) by formula:
y_true = panel_kw * sun_hours * (eff_pct / 100.0) * perf_ratio

# add small noise
noise = rng.normal(0, 0.01, n)
y = y_true + noise

# X features: panel_kw, sun_hours, eff_pct
X = np.vstack([panel_kw, sun_hours, eff_pct]).T

model = LinearRegression()
model.fit(X, y)

dump(model, "models/energy_model.pkl")
print("Saved model to models/energy_model.pkl")
print("Coefficients:", model.coef_, "Intercept:", model.intercept_)