"""Download CURRENT mandi prices (data.gov.in / Agmarknet) for our fruits and APPEND to data/mandi_prices.csv.

    python training/fetch_prices.py --key YOUR_DATA_GOV_IN_API_KEY

The API only returns the latest day. Run this again on other days: new rows are appended
(duplicates dropped), so history builds up and the price model gets better with time.
The API is slow/flaky, so: small pages, retries, and data is saved after every fruit.
"""
import argparse, os, time
from pathlib import Path
import pandas as pd
import requests

URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
FRUITS = ["Apple", "Banana", "Mango", "Orange", "Tomato"]
KEYS = ["state", "district", "market", "commodity", "variety", "grade", "arrival_date"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/124.0 Safari/537.36",
           "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9"}
TIMEOUT = (20, 180)          # connect, read (seconds)
RETRIES = 5


def get_page(get, params):
    for attempt in range(1, RETRIES + 1):
        try:
            r = get(URL, params=params, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code in (401, 403):
                raise SystemExit("API key galat hai ya activate nahi hui (HTTP %d)." % r.status_code)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.exceptions.RequestException(f"HTTP {r.status_code}")
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            wait = 5 * attempt
            print(f"   dikkat ({type(e).__name__}), {wait}s baad dobara try ({attempt}/{RETRIES})...")
            time.sleep(wait)
    raise SystemExit("API 5 baar try karne par bhi jawab nahi de rahi. Thodi der baad dobara chalao "
                     "(data wahi se aage badhega jo save ho chuka hai).")


def fetch_commodity(name, key, page=200, get=None, pause=1.0):
    get = get or requests.get
    rows, offset = [], 0
    while True:
        js = get_page(get, {"api-key": key, "format": "json", "limit": page, "offset": offset,
                            "filters[commodity]": name})
        recs = js.get("records", [])
        rows += recs
        total = int(js.get("total", len(rows)))
        print(f"   {name}: {len(rows)}/{total}")
        offset += page
        if not recs or offset >= total:
            return rows
        time.sleep(pause)


def save(new, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    new = new.astype(str)
    if out.exists():
        new = pd.concat([pd.read_csv(out, dtype=str), new], ignore_index=True)
    new = new.drop_duplicates(subset=[k for k in KEYS if k in new.columns])
    new.to_csv(out, index=False)
    return new


def import_folder(folder, out):
    """Backup path: files saved from the browser (csv or json) -> data/mandi_prices.csv"""
    import json
    frames = []
    for f in sorted(Path(folder).glob("*")):
        if f.suffix.lower() == ".csv":
            df = pd.read_csv(f, dtype=str)
        elif f.suffix.lower() == ".json":
            df = pd.DataFrame(json.load(open(f, encoding="utf-8")).get("records", []))
        else:
            continue
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        print(f"{f.name}: {len(df)} rows")
        frames.append(df)
    if not frames:
        raise SystemExit(f"{folder} mein koi .csv / .json file nahi mili.")
    total = save(pd.concat(frames, ignore_index=True), out)
    print(f"\nSaved {len(total)} total rows -> {out}")
    print("Fruit-wise:", total.commodity.value_counts().to_dict())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("DATA_GOV_KEY"))
    ap.add_argument("--out", default="data/mandi_prices.csv")
    ap.add_argument("--import-folder", default=None,
                    help="skip the API: import .csv/.json files you saved from the browser")
    a = ap.parse_args()
    if a.import_folder:
        return import_folder(a.import_folder, Path(a.out))
    if not a.key:
        raise SystemExit("API key do: --key <KEY>")
    out = Path(a.out)

    total = None
    for f in FRUITS:
        print(f"\n{f} ...")
        recs = fetch_commodity(f, a.key)
        print(f"{f:8s}: {len(recs)} rows mili")
        if recs:
            total = save(pd.DataFrame(recs), out)          # saved after every fruit
    if total is None:
        raise SystemExit("Koi row nahi mili. Key ya internet check karo.")
    print(f"\nSaved {len(total)} total rows -> {out}")
    if "arrival_date" in total.columns:
        print("Dates in file:", sorted(total.arrival_date.unique())[:10])
    print("Fruit-wise:", total.commodity.value_counts().to_dict())


if __name__ == "__main__":
    main()
