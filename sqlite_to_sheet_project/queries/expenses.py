from sqlite_to_sheet_project.queries.query_builder import build_query
from sqlite_to_sheet_project.schema.schema import (
    db,
    table,
    table_alias,
)

EXPENSE_COLUMNS = [
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

EXPENSE_QUERY = build_query(
    table_key="transaction",
    columns=EXPENSE_COLUMNS,
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
    ],
    where=f"""
    {table_alias("transaction")}.{db("transaction_type")} = 1
     AND TRIM(COALESCE({table_alias("transaction")}.{db("to_account_id")}, '')) = ''
    """,
        order_by_column="date",
)