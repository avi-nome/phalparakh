import joblib, pandas as pd

b = joblib.load("models/price_model_hist.joblib")
print("Fruits:", b["fruits"])

rows = pd.DataFrame([
    {"fruit": "banana", "state": "Haryana", "variety": "Banana | Banana", "month": 10, "year": 2026},
    {"fruit": "apple",  "state": "Haryana", "variety": "Apple | Delicious", "month": 10, "year": 2026},
    {"fruit": "tomato", "state": "Haryana", "variety": "Tomato | Tomato", "month": 10, "year": 2026},
])
print(b["model"].predict(rows[b["features"]]))