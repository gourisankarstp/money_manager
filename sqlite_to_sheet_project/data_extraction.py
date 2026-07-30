import sqlite3
import pandas as pd
import logging
from sqlite_to_sheet_project.filters import filter_transactions_for_month


def extract_transactions_from_sqlite(db_path,previous_month=False):
    try:
        conn = sqlite3.connect(db_path)

        zcategory_df = pd.read_sql("SELECT uid, pUid, NAME FROM ZCATEGORY", conn)
        assets_df = pd.read_sql("SELECT ID, uid, NIC_NAME FROM ASSETS", conn)

        account_dict = {}
        for _, row in assets_df.iterrows():
            account_name = row["NIC_NAME"]
            if pd.isna(account_name) or not str(account_name).strip():
                continue
            # Older records use ASSETS.ID while newer records use ASSETS.uid.
            for account_id in (row["ID"], row["uid"]):
                if not pd.isna(account_id):
                    account_dict[str(account_id)] = account_name

        category_dict = {}
        subcategory_dict = {}
        for _, row in zcategory_df.iterrows():
            uid, pUid, name = row["uid"], row["pUid"], row["NAME"]
            if pd.isna(pUid) or str(pUid) in ('0', ''):
                category_dict[uid] = name
            else:
                subcategory_dict[uid] = (pUid, name)

        query = """SELECT assetUid, ASSET_NIC, ctgUid, DO_TYPE, ZCONTENT, ZDATE, ZMONEY, ZDATA
                   FROM INOUTCOME WHERE DO_TYPE IN ('0', '1')"""
        df = pd.read_sql(query, conn)

        if df.empty:
            logging.warning("No valid transactions found.")
            return None
        # Ensure Amount is float
        df["ZMONEY"] = pd.to_numeric(df["ZMONEY"], errors="coerce").astype(float)
        df = filter_transactions_for_month(df, date_column="ZDATE",previous_month=previous_month)

        def map_category(ctgUid):
            category = category_dict.get(ctgUid, "Unknown")
            subcategory = None
            if ctgUid in subcategory_dict:
                parent_uid, subcat_name = subcategory_dict[ctgUid]
                category = category_dict.get(parent_uid, "Unknown")
                subcategory = subcat_name
            return category, subcategory

        df["Category"], df["Subcategory"] = zip(*df["ctgUid"].apply(map_category))
        # Match Google Sheets' REGEXREPLACE(E2:E, "^[^A-Za-z]+", "") so
        # category icons (for example, emoji prefixes) are not exported.
        df["Category"] = df["Category"].astype("string").str.replace(
            r"^[^A-Za-z]+", "", regex=True
        )
        df["Transaction Type"] = df["DO_TYPE"].apply(lambda x: "In" if int(x) == 0 else "Out")

        def map_account(row):
            account_name = account_dict.get(str(row["assetUid"]))
            if account_name:
                return account_name
            fallback_name = row["ASSET_NIC"]
            if pd.notna(fallback_name) and str(fallback_name).strip():
                return fallback_name
            return "Unknown"

        df["Account"] = df.apply(map_account, axis=1)

        df.rename(columns={
            "ZCONTENT": "Note",
            "ZDATE": "Date",
            "ZMONEY": "Amount",
            "ZDATA": "Description"
        }, inplace=True)

        df.drop(columns=["assetUid", "ASSET_NIC", "ctgUid", "DO_TYPE"], inplace=True)
        df = df[
            [
                "Note",
                "Date",
                "Account",
                "Amount",
                "Description",
                "Category",
                "Subcategory",
                "Transaction Type",
            ]
        ]
        # Google Sheets' API rejects NaN/NaT values because they are not valid
        # JSON numbers. Export missing database fields as blank cells instead.
        df = df.astype(object).where(pd.notna(df), None)
        logging.info(f"Processed {len(df)} valid transactions.")
        return df

    except Exception as e:
        logging.exception("Data extraction failed.")
        return None

    finally:
        conn.close()
