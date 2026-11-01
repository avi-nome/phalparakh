"""ONLY FOR TESTING THE PIPELINE. Makes a fake mandi CSV in the Agmarknet column layout.
Never use its numbers in your report - use real data (Kaggle / data.gov.in)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(0)
rows = []
base = {"Mango": 6000, "Banana": 2500, "Apple": 9000}          # Rs / quintal
states = ["Haryana", "Maharashtra", "Uttar Pradesh", "Punjab"]
for d in pd.date_range("2022-01-01", "2024-12-28", freq="3D"):
    for f, b in base.items():
        for s_i, s in enumerate(states):
            season = 1 + 0.25 * np.sin(2 * np.pi * d.month / 12 + len(f))
            rows.append({"State": s, "Commodity": f, "Grade": "FAQ",
                         "Arrival_Date": d.strftime("%d/%m/%Y"),
                         "Modal_Price": b * season * (1 + 0.05 * s_i) * (1 + rng.normal(0, 0.05))})
pd.DataFrame(rows).to_csv("tests/fake_prices.csv", index=False)
print("tests/fake_prices.csv", len(rows))
