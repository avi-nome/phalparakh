import os, duckdb
from huggingface_hub import hf_hub_download

token = os.environ["HF_TOKEN"]
path = hf_hub_download("judicialmind/MandiBench", "series/all.parquet",
                       repo_type="dataset", token=token, local_dir="data/mandibench")
print("Saved:", path)

con = duckdb.connect()
print(con.sql(f"DESCRIBE SELECT * FROM '{path}'"))
print(con.sql(f"SELECT * FROM '{path}' LIMIT 5"))