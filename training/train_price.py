"""Train the price model from a mandi price CSV (e.g. Agmarknet / data.gov.in).

    python training/train_price.py --csv prices.csv --fruits mango,banana,apple

The CSV needs (any spelling like 'Modal_Price' / 'Modal Price' works):
    Arrival_Date, Commodity, State, Grade (optional), Modal_Price  (Rs per quintal by default)

What it does: monthly average per (fruit, state, grade) -> time-based split (last 20% of
months are the test set) -> Random Forest vs XGBoost -> best model by MAE saved.
"""
import argparse, json, re
from pathlib import Path
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBRegressor

CANDIDATES = {
    "date": ["arrival_date", "date", "price_date"],
    "commodity": ["commodity", "fruit", "crop"],
    "state": ["state", "state_name"],
    "grade": ["variety", "grade"],
    "price": ["modal_price", "modal", "price", "modal_x0020_price"],
}


def clean_cols(df):
    df.columns = [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in df.columns]
    return df


def find(df, key, required=True):
    for c in CANDIDATES[key]:
        if c in df.columns:
            return c
    if required:
        raise SystemExit(f"Column for '{key}' not found. Columns are: {list(df.columns)}")
    return None


def make_pipe(model):
    pre = ColumnTransformer([
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
         ["commodity", "state", "grade"]),
        ("num", "passthrough", ["month"]),
    ])
    return Pipeline([("pre", pre), ("model", model)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--fruits", default="mango,banana,apple")
    ap.add_argument("--unit", choices=["quintal", "kg"], default="quintal")
    ap.add_argument("--out", default="models")
    a = ap.parse_args()

    df = clean_cols(pd.read_csv(a.csv))
    c_date, c_com, c_state, c_price = (find(df, k) for k in ("date", "commodity", "state", "price"))
    c_grade = find(df, "grade", required=False)

    d = pd.DataFrame({
        "date": pd.to_datetime(df[c_date], dayfirst=True, errors="coerce"),
        "commodity": df[c_com].astype(str).str.strip().str.title(),
        "state": df[c_state].astype(str).str.strip().str.title(),
        "grade": df[c_grade].astype(str).str.strip().str.title() if c_grade else "Standard",
        "price": pd.to_numeric(df[c_price], errors="coerce"),
    }).dropna()
    d = d[d.price > 0]
    vc = d.grade.value_counts()
    d.loc[d.grade.isin(vc[vc < 20].index), "grade"] = "Other"      # rare varieties -> Other
    d["price"] = d.price / (100 if a.unit == "quintal" else 1)   # -> Rs per kg

    wanted = [f.strip().title() for f in a.fruits.split(",")]
    d = d[d.commodity.isin(wanted)]
    if d.empty:
        raise SystemExit(f"No rows for fruits {wanted}. Commodities in file: {sorted(df[c_com].unique())[:30]}")

    lo, hi = d.price.quantile([0.005, 0.995])           # remove typing errors / extreme outliers
    d = d[(d.price >= lo) & (d.price <= hi)]

    d["month"] = d.date.dt.month
    d["period"] = d.date.dt.to_period("M")
    m = d.groupby(["period", "commodity", "state", "grade", "month"], as_index=False).price.mean()
    m = m.sort_values("period")
    m["period"] = m.period.astype(str)

    periods = sorted(m.period.unique())
    if len(periods) >= 6:
        cut = periods[int(len(periods) * 0.8)]
        train, test = m[m.period < cut], m[m.period >= cut]
        split = f"time-based (test from {cut})"
    else:
        # Only a few days/months of data (e.g. data.gov.in snapshot): time split impossible.
        # Random 80/20 split instead; month has no signal yet. Re-run fetch_prices.py over time.
        m = m.sample(frac=1, random_state=42)
        k = int(len(m) * 0.8)
        train, test = m.iloc[:k], m.iloc[k:]
        cut = "random split"
        split = f"random 80/20 (only {len(periods)} month(s) of data)"
    print(f"{len(m)} rows | train {len(train)} | test {len(test)} | split: {split}")
    feats = ["commodity", "state", "grade", "month"]

    models = {
        "RandomForest": RandomForestRegressor(n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=400, learning_rate=0.06, max_depth=6, subsample=0.9,
                                colsample_bytree=0.9, random_state=42),
    }
    results, preds = {}, {}
    for name, mdl in models.items():
        p = make_pipe(mdl).fit(train[feats], train.price).predict(test[feats])
        preds[name] = p
        results[name] = {"MAE": float(mean_absolute_error(test.price, p)),
                         "RMSE": float(np.sqrt(mean_squared_error(test.price, p))),
                         "R2": float(r2_score(test.price, p))}
        print(name, {k: round(v, 3) for k, v in results[name].items()})

    best = min(results, key=lambda k: results[k]["MAE"])
    print("Best model:", best)
    final = make_pipe(models[best]).fit(m[feats], m.price)       # refit on all data

    out = Path(a.out); out.mkdir(exist_ok=True)
    joblib.dump({
        "model": final, "name": best,
        "categories": {"fruits": sorted(m.commodity.unique()),
                       "states": sorted(m.state.unique()),
                       "grades": sorted(m.grade.unique())},
    }, out / "price_model.joblib")
    json.dump({"best": best, "unit": "Rs per kg", "split": split, "results": results},
              open(out / "price_metrics.json", "w"), indent=2)

    plt.figure(figsize=(5, 5))
    plt.scatter(test.price, preds[best], s=8, alpha=0.5)
    lim = [0, max(test.price.max(), preds[best].max())]
    plt.plot(lim, lim, "r--")
    plt.xlabel("Actual price (Rs/kg)"); plt.ylabel("Predicted price (Rs/kg)"); plt.title(f"{best}: actual vs predicted")
    plt.tight_layout(); plt.savefig(out / "price_actual_vs_predicted.png", dpi=150)
    print("Saved models/price_model.joblib, price_metrics.json, price_actual_vs_predicted.png")


if __name__ == "__main__":
    main()
