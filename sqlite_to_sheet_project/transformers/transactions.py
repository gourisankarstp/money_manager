from .accounts import map_accounts, map_transfer_accounts
from .categories import map_categories
from .columns import (
    rename_columns,
    reorder_transaction_columns,
    reorder_transfer_columns,
)
from .dates import format_dates
from sqlite_to_sheet_project.schema.schema import column


TRANSACTION_TYPE = {
    0: "Income",
    1: "Expense",
    2: "Transfer",
    "0": "Income",
    "1": "Expense",
    "2": "Transfer",
}


def map_transaction_type(df):
    transaction_type_column = column("transaction_type")

    if transaction_type_column in df.columns:
        df[transaction_type_column] = (
            df[transaction_type_column]
            .map(TRANSACTION_TYPE)
        )

    return df


def transform_transactions(
    df,
    asset_uid_dict,
    category_uid_dict,
):
    """
    Common transformations for Expenses & Income.
    """

    df = rename_columns(df)
    # df = format_dates(df)
    df = map_accounts(df, asset_uid_dict)
    df = map_categories(df, category_uid_dict)
    df = map_transaction_type(df)
    df = reorder_transaction_columns(df)

    return df


def transform_transfers(
    df,
    asset_uid_dict,
):
    df = rename_columns(df)

    df = map_transfer_accounts(
        df,
        asset_uid_dict,
    )

    if "Transaction Type" not in df.columns:
        df["Transaction Type"] = "Transfer"

    if "Description" not in df.columns:
        df["Description"] = "Transfer"

    if "Note" in df.columns:
        df["Note"] = df["Note"].fillna("")

    df = reorder_transfer_columns(df)

    return df