"""Usage: python training/check_prices.py path\to\file.csv
Tells you: columns, which fruits exist (row counts), and how recent the data is."""
import sys
import pandas as pd

path = sys.argv[1]
d = pd.read_csv(path, low_memory=False)
print("\nROWS:", len(d))
print("COLUMNS:", d.columns.tolist())

# commodity column = the one holding the most fruit names
FRUITS = ["apple", "banana", "mango", "orange", "tomato"]
best, best_hits = None, 0
for c in d.columns:
    if not pd.api.types.is_numeric_dtype(d[c]):
        s = d[c].astype(str).str.lower()
        hits = sum(s.str.contains(f, regex=False).sum() for f in FRUITS)
        if hits > best_hits:
            best, best_hits = c, hits
if best is None:
    print("\nNO fruit names found in any column -> this dataset is NOT usable.")
    sys.exit()
s = d[best].astype(str).str.lower()
print(f"\nCommodity column: '{best}'")
for f in FRUITS:
    print(f"  {f:8s}: {int(s.str.contains(f, regex=False).sum())} rows")

# date column = first column that parses as dates for most rows
for c in d.columns:
    if "date" in c.lower() or "month" in c.lower() or "year" in c.lower():
        t = pd.to_datetime(d[c], errors="coerce", dayfirst=True)
        if t.notna().mean() > 0.8:
            print(f"\nDate column '{c}': {t.min().date()}  ->  {t.max().date()}")
            break
else:
    print("\nNo date column found.")
st = [c for c in d.columns if "state" in c.lower()]
print("State column:", st[0] + f" ({d[st[0]].nunique()} states)" if st else "none")
