import pandas as pd

from sqlite_to_sheet_project.queries.expenses import EXPENSE_QUERY
from sqlite_to_sheet_project.transformers.transactions import transform_transactions
from sqlite_to_sheet_project.transformers.emoji_cleanup import remove_emojis
from sqlite_to_sheet_project.transformers.text2num import convert_to_number

def extract_expenses(conn, asset_uid_dict, category_uid_dict):
    """
    Extract and transform expense transactions.
    """
    df = pd.read_sql_query(EXPENSE_QUERY, conn)

    df = remove_emojis(df, "category")
    df = remove_emojis(df, "subcategory")
    df = remove_emojis(df, "account")
    df = remove_emojis(df, "to_account")
    df = convert_to_number(df, "amount")

    return transform_transactions(
        df,
        asset_uid_dict=asset_uid_dict,
        category_uid_dict=category_uid_dict,
    )