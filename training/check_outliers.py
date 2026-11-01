import pandas as pd

df = pd.read_csv("data/fruits_raw.csv", usecols=["ts", "target", "state", "commodity"])
df = df[df["target"] > 0]
df["price_kg"] = df["target"] / 100

print(df.groupby("commodity")["price_kg"].describe(
    percentiles=[0.5, 0.99, 0.999]).round(1).to_string())

print("\nSabse mehnge 10 rows:")
print(df.nlargest(10, "price_kg")[["ts", "state", "commodity", "price_kg"]].to_string())