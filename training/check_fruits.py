import duckdb

p = "data/mandibench/series/all.parquet"
con = duckdb.connect()

where = """(commodity ILIKE '%mango%' OR commodity ILIKE '%banana%'
          OR commodity ILIKE '%apple%' OR commodity ILIKE '%orange%'
          OR commodity ILIKE '%tomato%')"""

print(con.sql(f"""
    SELECT commodity, cclass, COUNT(*) AS rows,
           COUNT(DISTINCT series_id) AS series,
           MIN(ts) AS first_date, MAX(ts) AS last_date
    FROM '{p}' WHERE {where}
    GROUP BY 1, 2 ORDER BY rows DESC
""").df().to_string())

con.sql(f"COPY (SELECT * FROM '{p}' WHERE {where}) TO 'data/fruits_raw.csv' (HEADER, DELIMITER ',')")
print("Saved -> data/fruits_raw.csv")