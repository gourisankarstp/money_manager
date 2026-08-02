import sqlite3
import csv

DB_FILE = "MMGF(02-08-26-122439).mmbak"
OUTPUT_FILE = "result.csv"

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()
cursor.execute("""
SELECT
    '[' || IFNULL(toAssetUid, 'NULL') || ']' AS Value,
    COUNT(*) AS Count
FROM INOUTCOME
WHERE DO_TYPE = 1
GROUP BY toAssetUid;
""")

rows = cursor.fetchall()

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)

    # Write header
    writer.writerow(rows[0].keys() if rows else [])

    # Write data
    for row in rows:
        writer.writerow(row)

conn.close()

print(f"Exported {len(rows)} rows to {OUTPUT_FILE}")