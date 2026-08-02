import pandas as pd

from sqlite_to_sheet_project.queries.expenses import EXPENSE_QUERY
from sqlite_to_sheet_project.transformers.transactions import transform_transactions
from sqlite_to_sheet_project.transformers.emoji_cleanup import remove_emojis

def extract_expenses(conn, asset_uid_dict, category_uid_dict):
    """
    Extract and transform expense transactions.
    """
    df = pd.read_sql_query(EXPENSE_QUERY, conn)

    df = remove_emojis(df, "category")
    df = remove_emojis(df, "subcategory")

    return transform_transactions(
        df,
        asset_uid_dict=asset_uid_dict,
        category_uid_dict=category_uid_dict,
    )