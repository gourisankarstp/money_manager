from sqlite_to_sheet_project.queries.query_builder import build_query
from sqlite_to_sheet_project.schema.schema import (
    db,
    table,
    table_alias,
)

INCOME_COLUMNS = [
    "account",
    "category",
    "subcategory",
    "transaction_type",
    "description",
    "date",
    "amount",
    "note",
    "transaction_id",
]

INCOME_QUERY = build_query(
    table_key="transaction",
    columns=INCOME_COLUMNS,
joins=[
    f"""
LEFT JOIN {table("from_asset")} {table_alias("from_asset")}
    ON {table_alias("transaction")}.{db("account_id")}
    = {table_alias("from_asset")}.uid
""",
    f"""
    LEFT JOIN {table("category")} {table_alias("category")}
        ON {table_alias("transaction")}.{db("category_id")}
        = {table_alias("category")}.uid
    """,
    f"""
    LEFT JOIN {table("parent_category")} {table_alias("parent_category")}
        ON {table_alias("category")}.pUid
        = {table_alias("parent_category")}.uid
    """,
],
    where=f"""
{table_alias("transaction")}.{db("transaction_type")} = 0
     AND TRIM(COALESCE({table_alias("transaction")}.{db("to_account_id")}, '')) = ''
""",
    order_by_column="date",
)