import os
import pandas as pd, joblib

b = joblib.load("models/price_model_hist.joblib")
df = pd.read_csv("data/fruits_raw.csv",
                 usecols=["ts", "target", "state", "variety", "commodity"])
df["ts"] = pd.to_datetime(df["ts"])

def clean(c):
    c = str(c).lower()
    if "pine" in c or "custard" in c: return None
    for f in ["banana", "mango", "apple", "orange", "tomato"]:
        if f in c: return f
    return None

df["fruit"] = df["commodity"].map(clean)
df = df.dropna(subset=["fruit", "target"])
df = df[df["target"] > 0]
df["price_kg"] = df["target"] / 100

# wahi outlier filter jo training mein tha
med = df.groupby("fruit")["price_kg"].transform("median")
df = df[(df["price_kg"] <= 5 * med) & (df["price_kg"] >= med / 10)]

# sirf wahi variety jo price model use karta hai
df["variety"] = df["commodity"].astype(str) + " | " + df["variety"].astype(str)
df = df[df["variety"] == df["fruit"].map(b["default_variety"])]

df["year"] = df["ts"].dt.year
df["month"] = df["ts"].dt.month
m = df.groupby(["fruit", "state", "year", "month"], as_index=False)["price_kg"].mean()

# All India average (jis state ka data na ho uske liye)
allin = m.groupby(["fruit", "year", "month"], as_index=False)["price_kg"].mean()
allin["state"] = "All India"

out = pd.concat([m, allin])
out["price_kg"] = out["price_kg"].round(2)
os.makedirs("assets", exist_ok=True)
out.to_csv("assets/price_history.csv", index=False)
print(len(out), "rows saved -> assets/price_history.csv")
print(out.groupby("fruit")["year"].agg(["min", "max"]))