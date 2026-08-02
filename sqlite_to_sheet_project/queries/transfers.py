from sqlite_to_sheet_project.queries.query_builder import build_query
from sqlite_to_sheet_project.schema.schema import (
    db,
    table,
    table_alias,
)

TRANSFER_COLUMNS = [
    "from_account",
    "to_account",
    "description",
    "date",
    "amount",
    "note",
]

TRANSFER_QUERY = build_query(
    table_key="transaction",
    columns=TRANSFER_COLUMNS,
joins=[
    f"""
LEFT JOIN {table("from_asset")} FA
    ON {table_alias("transaction")}.{db("account_id")} = FA.uid
""",
    f"""
LEFT JOIN {table("to_asset")} TA
    ON {table_alias("transaction")}.{db("to_account_id")} = TA.uid
""",
],
    where=f"""
     TRIM(COALESCE({table_alias("transaction")}.{db("to_account_id")}, '')) != ''
""",
    order_by_column="date",
)