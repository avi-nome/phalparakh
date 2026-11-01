"""Price estimation = ML base price (Rs/kg) x weight x ripeness multiplier x retail markup."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "price_model_hist.joblib"

RIPENESS_MULTIPLIER = {"unripe": 0.90, "ripe": 1.00, "overripe": 0.60}
RETAIL_MARKUP = 1.25

_bundle = None


class PriceModelMissing(RuntimeError):
    pass


def load_bundle():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise PriceModelMissing(
                "models/price_model_hist.joblib nahi mila. "
                "Pehle training/train_price_hist.py chalao.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def options() -> dict:
    """Dropdown values for the UI."""
    b = load_bundle()
    return {
        "fruits": [f.title() for f in b["fruits"]],
        "states": list(b["states"]),
        "grades": ["Any"],   # naye model mein grade nahi hai
    }


def predict_price(fruit: str, ripeness: str, weight_kg: float, state: str,
                  month: int, grade: str | None = None) -> dict:
    b = load_bundle()

    fruit_key = str(fruit).strip().lower()
    if fruit_key not in b["fruits"]:
        raise ValueError(f"Fruit '{fruit}' model mein nahi hai. "
                         f"Available: {[f.title() for f in b['fruits']]}")

    states = {s.lower(): s for s in b["states"]}
    state_key = str(state).strip().lower()
    if state_key not in states:
        raise ValueError(f"State '{state}' model mein nahi hai.")

    ripeness = str(ripeness).strip().lower()
    if ripeness not in RIPENESS_MULTIPLIER:
        raise ValueError(f"Unknown ripeness '{ripeness}'")

    if not (1 <= int(month) <= 12):
        raise ValueError("Month 1 se 12 ke beech hona chahiye.")
    if weight_kg is None or weight_kg <= 0:
        raise ValueError("Weight 0 se zyada hona chahiye.")

    row = pd.DataFrame([{
        "fruit": fruit_key,
        "state": states[state_key],
        "variety": b["default_variety"][fruit_key],
        "month": int(month),
        "year": b["latest_year"],
    }])
    base = max(float(b["model"].predict(row[b["features"]])[0]), 0.0)  # Rs/kg wholesale

    mult = RIPENESS_MULTIPLIER[ripeness]
    per_kg = base * mult * RETAIL_MARKUP
    return {
        "base_price_per_kg": round(base, 2),
        "ripeness_multiplier": mult,
        "retail_markup": RETAIL_MARKUP,
        "price_per_kg": round(per_kg, 2),
        "total_price": round(per_kg * weight_kg, 2),
        "model": b["name"],
    }