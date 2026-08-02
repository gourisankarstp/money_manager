import sqlite3
import pandas as pd

from sqlite_to_sheet_project.extractors.expenses import extract_expenses
from sqlite_to_sheet_project.extractors.income import extract_income
from sqlite_to_sheet_project.extractors.transfers import extract_transfers
from sqlite_to_sheet_project.transformers.dates import format_dates

from sqlite_to_sheet_project.filters import filter_transactions

from sqlite_to_sheet_project.lookup import (
    get_asset_uid_dict,
    get_category_uid_dict,
)


def extract_transactions_from_sqlite(
    db_path,
    previous_month=False,
):
    """
    Extract expense, income and transfer transactions from the SQLite database.
    """

    conn = sqlite3.connect(db_path)

    try:
        # Build lookup dictionaries
        asset_uid_dict = get_asset_uid_dict(conn)
        category_uid_dict = get_category_uid_dict(conn)

        # Extract data
        expense_df = extract_expenses(
            conn,
            asset_uid_dict,
            category_uid_dict,
        )

        income_df = extract_income(
            conn,
            asset_uid_dict,
            category_uid_dict,
        )

        transfer_df = extract_transfers(
            conn,
            asset_uid_dict,
        )

        # Combine expenses and income
        transaction_df = pd.concat(
            [expense_df, income_df],
            ignore_index=True,
        )

        # Apply filters
        transaction_df = filter_transactions(
            transaction_df,
            previous_month=previous_month,
        )

        transfer_df = filter_transactions(
            transfer_df,
            previous_month=previous_month,
        )

        # transaction_df = format_dates(transaction_df)

        # transfer_df = format_dates(transfer_df)

        return transaction_df, transfer_df

    finally:
        conn.close()