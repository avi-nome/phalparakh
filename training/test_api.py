"""Tiny API test: python training/test_api.py --key YOUR_KEY
Asks for just 1 row and prints what the server really answers (status code, time, text)."""
import argparse, time
import requests

URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/124.0 Safari/537.36", "Accept": "application/json, text/plain, */*"}
ap = argparse.ArgumentParser(); ap.add_argument("--key", required=True); a = ap.parse_args()

for label, extra in [("bina filter", {}), ("Apple filter", {"filters[commodity]": "Apple"})]:
    p = {"api-key": a.key, "format": "json", "limit": 1, "offset": 0, **extra}
    t = time.time()
    try:
        r = requests.get(URL, params=p, headers=HEADERS, timeout=(20, 90))
        print(f"[{label}] status={r.status_code}  time={time.time()-t:.1f}s")
        print("   jawab:", r.text[:300].replace(a.key, "<KEY>"))
    except Exception as e:
        print(f"[{label}] FAIL after {time.time()-t:.1f}s: {type(e).__name__}")
