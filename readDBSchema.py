import sqlite3
import json
from pathlib import Path

DB_FILE = "MMGF(31-07-26-133144).mmbak"         # Change to your SQLite file
OUTPUT_FILE = "database_schema.json"

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

schema = {
    "database": Path(DB_FILE).name,
    "tables": [],
    "views": [],
    "triggers": []
}

# -------------------------------------------------------------------
# Tables
# -------------------------------------------------------------------
cursor.execute("""
SELECT name, sql
FROM sqlite_master
WHERE type='table'
AND name NOT LIKE 'sqlite_%'
ORDER BY name;
""")

tables = cursor.fetchall()

for table in tables:
    table_name = table["name"]

    table_info = {
        "name": table_name,
        "create_sql": table["sql"],
        "columns": [],
        "foreign_keys": [],
        "indexes": []
    }

    # Columns
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    for col in cursor.fetchall():
        table_info["columns"].append({
            "cid": col["cid"],
            "name": col["name"],
            "type": col["type"],
            "notnull": bool(col["notnull"]),
            "default": col["dflt_value"],
            "primary_key": bool(col["pk"])
        })

    # Foreign Keys
    cursor.execute(f'PRAGMA foreign_key_list("{table_name}")')
    for fk in cursor.fetchall():
        table_info["foreign_keys"].append(dict(fk))

    # Indexes
    cursor.execute(f'PRAGMA index_list("{table_name}")')
    indexes = cursor.fetchall()

    for idx in indexes:
        index_name = idx["name"]

        cursor.execute(f'PRAGMA index_info("{index_name}")')
        columns = [r["name"] for r in cursor.fetchall()]

        table_info["indexes"].append({
            "name": index_name,
            "unique": bool(idx["unique"]),
            "origin": idx["origin"],
            "partial": bool(idx["partial"]),
            "columns": columns
        })

    schema["tables"].append(table_info)

# -------------------------------------------------------------------
# Views
# -------------------------------------------------------------------
cursor.execute("""
SELECT name, sql
FROM sqlite_master
WHERE type='view'
ORDER BY name;
""")

for row in cursor.fetchall():
    schema["views"].append({
        "name": row["name"],
        "create_sql": row["sql"]
    })

# -------------------------------------------------------------------
# Triggers
# -------------------------------------------------------------------
cursor.execute("""
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type='trigger'
ORDER BY name;
""")

for row in cursor.fetchall():
    schema["triggers"].append({
        "name": row["name"],
        "table": row["tbl_name"],
        "create_sql": row["sql"]
    })

conn.close()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print(f"Schema written to {OUTPUT_FILE}")