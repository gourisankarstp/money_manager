import pandas as pd

from sqlite_to_sheet_project.queries.transfers import TRANSFER_QUERY
from sqlite_to_sheet_project.transformers.transactions import transform_transfers
from sqlite_to_sheet_project.transformers.emoji_cleanup import remove_emojis
from sqlite_to_sheet_project.transformers.text2num import convert_to_number

def extract_transfers(conn, asset_uid_dict):
    """
    Extract and transform transfer transactions.
    """
    df = pd.read_sql_query(TRANSFER_QUERY, conn)

    df = remove_emojis(df, "category")
    df = remove_emojis(df, "subcategory")
    df = remove_emojis(df, "account")
    df = convert_to_number(df, "amount")


    return transform_transfers(
        df,
        asset_uid_dict=asset_uid_dict,
    )