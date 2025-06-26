import sqlite3
import pandas as pd
import logging
from sqlite_to_sheet_project.filters import filter_transactions_for_month

def extract_transactions_from_sqlite(db_path):
    try:
        conn = sqlite3.connect(db_path)

        zcategory_df = pd.read_sql("SELECT uid, pUid, NAME FROM ZCATEGORY", conn)

        category_dict = {}
        subcategory_dict = {}
        for _, row in zcategory_df.iterrows():
            uid, pUid, name = row["uid"], row["pUid"], row["NAME"]
            if pd.isna(pUid) or str(pUid) in ('0', ''):
                category_dict[uid] = name
            else:
                subcategory_dict[uid] = (pUid, name)

        query = """SELECT ctgUid, DO_TYPE, ZCONTENT, ZDATE, ZMONEY, ZDATA FROM INOUTCOME WHERE DO_TYPE IN ('0', '1')"""
        df = pd.read_sql(query, conn)

        if df.empty:
            logging.warning("No valid transactions found.")
            return None

        df = filter_transactions_for_month(df, date_column="ZDATE")

        def map_category(ctgUid):
            category = category_dict.get(ctgUid, "Unknown")
            subcategory = None
            if ctgUid in subcategory_dict:
                parent_uid, subcat_name = subcategory_dict[ctgUid]
                category = category_dict.get(parent_uid, "Unknown")
                subcategory = subcat_name
            return category, subcategory

        df["Category"], df["Subcategory"] = zip(*df["ctgUid"].apply(map_category))
        df["Transaction Type"] = df["DO_TYPE"].apply(lambda x: "In" if int(x) == 0 else "Out")

        df.rename(columns={
            "ZCONTENT": "Note",
            "ZDATE": "Date",
            "ZMONEY": "Amount",
            "ZDATA": "Description"
        }, inplace=True)

        df.drop(columns=["ctgUid", "DO_TYPE"], inplace=True)
        logging.info(f"Processed {len(df)} valid transactions.")
        return df

    except Exception as e:
        logging.exception("Data extraction failed.")
        return None

    finally:
        conn.close()
