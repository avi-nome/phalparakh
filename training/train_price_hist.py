import pandas as pd, numpy as np, joblib
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

df = pd.read_csv("data/fruits_raw.csv",
                 usecols=["ts", "target", "state", "variety", "commodity"])
df["ts"] = pd.to_datetime(df["ts"])

# fruit ka naam saaf karo, Pineapple hata do
def clean(c):
    c = str(c).lower()
    if "pine" in c or "custard" in c: return None
    for f in ["banana", "mango", "apple", "orange", "tomato"]:
        if f in c: return f
    return None
df["fruit"] = df["commodity"].map(clean)
df = df.dropna(subset=["fruit", "target"])
df = df[df["target"] > 0]

# commodity ka naam variety mein jod do (Banana - Green alag variety ban jayegi)
df["variety"] = df["commodity"].astype(str) + " | " + df["variety"].astype(str)
df["price_kg"] = df["target"] / 100          # quintal -> kg
# galat (outlier) prices hatao: fruit ke median se 5x zyada ya 10x kam
med = df.groupby("fruit")["price_kg"].transform("median")
before = len(df)
df = df[(df["price_kg"] <= 5 * med) & (df["price_kg"] >= med / 10)]
print(f"Outlier rows hataye: {before - len(df)} / {before}")
df["year"] = df["ts"].dt.year
df["month"] = df["ts"].dt.month

# daily data ko mahine ke average mein badlo (model tez chalega)
m = (df.groupby(["fruit", "state", "variety", "year", "month"], as_index=False)
       ["price_kg"].mean())
print("Monthly rows:", len(m))

feats = ["fruit", "state", "variety", "month", "year"]
train = m[m["year"] <= 2023]
test = m[m["year"] >= 2024]
print("Train:", len(train), " Test:", len(test))
Xtr, ytr, Xte, yte = train[feats], train["price_kg"], test[feats], test["price_kg"]

pre = ColumnTransformer(
    [("oh", OneHotEncoder(handle_unknown="ignore"), ["fruit", "state", "variety"])],
    remainder="passthrough")

# baseline: bas purana average price (isse model ko behtar hona chahiye)
base = train.groupby(["fruit", "state", "variety"])["price_kg"].mean()
bp = test.set_index(["fruit", "state", "variety"]).index.map(base).to_series()
bp = bp.fillna(train["price_kg"].mean()).values
print(f"Baseline : MAE={mean_absolute_error(yte, bp):.2f}  R2={r2_score(yte, bp):.3f}")

models = {
    "RandomForest": RandomForestRegressor(n_estimators=100, min_samples_leaf=2,
                                          n_jobs=-1, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.08,
                            random_state=42),
}
best, best_mae, best_name = None, 1e9, ""
for name, mdl in models.items():
    p = Pipeline([("pre", pre), ("m", mdl)]).fit(Xtr, ytr)
    pr = p.predict(Xte)
    mae = mean_absolute_error(yte, pr)
    rmse = np.sqrt(mean_squared_error(yte, pr))
    print(f"{name}: MAE={mae:.2f}  RMSE={rmse:.2f}  R2={r2_score(yte, pr):.3f}  (Rs/kg)")
    if mae < best_mae: best, best_mae, best_name = p, mae, name

# final model: ab saara data (2024+ bhi) se dobara train karo
best.fit(m[feats], m["price_kg"])
default_variety = m.groupby("fruit")["variety"].agg(
    lambda s: s.value_counts().index[0]).to_dict()
joblib.dump({"model": best, "name": best_name, "features": feats,
             "fruits": sorted(m["fruit"].unique()),
             "states": sorted(m["state"].unique()),
             "default_variety": default_variety,
             "latest_year": int(m["year"].max())},
            "models/price_model_hist.joblib")