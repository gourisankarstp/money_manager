import pandas as pd

from sqlite_to_sheet_project.queries.accounts import ACCOUNTS_QUERY
from sqlite_to_sheet_project.queries.categories import CATEGORIES_QUERY


def get_asset_uid_dict(conn):
    """
    Returns:
    {
        asset_uid: account_name
    }
    """

    df = pd.read_sql_query(
        ACCOUNTS_QUERY,
        conn,
    )

    return dict(zip(df["uid"], df["NIC_NAME"]))


def get_asset_name_dict(conn):
    """
    Returns:
    {
        account_name: asset_uid
    }
    """

    df = pd.read_sql_query(
        ACCOUNTS_QUERY,
        conn,
    )

    return dict(zip(df["NIC_NAME"], df["uid"]))


def get_category_uid_dict(conn):
    """
    Returns:
    {
        category_uid: {
            "Category": "...",
            "Subcategory": "..."
        }
    }
    """

    df = pd.read_sql_query(
        CATEGORIES_QUERY,
        conn,
    )

    return {
        row["uid"]: {
            "Category": row["CATEGORY"] if pd.notna(row["CATEGORY"]) else row["SUBCATEGORY"],
            "Subcategory": row["SUBCATEGORY"] if pd.notna(row["CATEGORY"]) else "",
        }
        for _, row in df.iterrows()
    }