"""Optional local diagnostics for inspecting Money Manager SQLite backups."""

import argparse
import json
import logging
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPENSE_PREVIEW_FILE = PROJECT_ROOT / "expense_preview_top_5.csv"
ACCOUNT_PREVIEW_FILE = PROJECT_ROOT / "account_preview_top_5.csv"
DATABASE_SCHEMA_FILE = PROJECT_ROOT / "database_schema.json"


def export_sqlite_debug_previews(conn):
    """Write schema and five-row previews to local files for manual inspection."""
    table_names = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name",
        conn,
    )["name"].tolist()
    database_schema = {}
    for table_name in table_names:
        safe_table_name = table_name.replace('"', '""')
        columns = pd.read_sql(
            f'PRAGMA table_info("{safe_table_name}")', conn
        )["name"].tolist()
        database_schema[table_name] = columns

    DATABASE_SCHEMA_FILE.write_text(
        json.dumps(database_schema, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logging.info("Database table schema written to %s", DATABASE_SCHEMA_FILE)

    expense_preview = pd.read_sql(
        "SELECT * FROM INOUTCOME WHERE DO_TYPE IN ('0', '1') LIMIT 5", conn
    )
    expense_preview.to_csv(EXPENSE_PREVIEW_FILE, index=False, encoding="utf-8-sig")
    logging.info("Expense preview written to %s", EXPENSE_PREVIEW_FILE)

    account_table_names = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND upper(name) LIKE '%ACCOUNT%'",
        conn,
    )["name"].tolist()
    if not account_table_names:
        logging.warning("No account table found in the SQLite database.")
        pd.DataFrame().to_csv(ACCOUNT_PREVIEW_FILE, index=False, encoding="utf-8-sig")
        return

    account_previews = []
    for table_name in account_table_names:
        safe_table_name = table_name.replace('"', '""')
        account_preview = pd.read_sql(
            f'SELECT * FROM "{safe_table_name}" LIMIT 5', conn
        )
        account_preview.insert(0, "source_table", table_name)
        account_previews.append(account_preview)

    pd.concat(account_previews, ignore_index=True, sort=False).to_csv(
        ACCOUNT_PREVIEW_FILE, index=False, encoding="utf-8-sig"
    )
    logging.info("Account preview written to %s", ACCOUNT_PREVIEW_FILE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Money Manager SQLite schema and five-row previews."
    )
    parser.add_argument("database", help="Path to the downloaded .mmbak SQLite file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    with sqlite3.connect(args.database) as connection:
        export_sqlite_debug_previews(connection)
