import pandas as pd
from datetime import datetime, timedelta
from sqlite_to_sheet_project.config import target_year, target_month

def filter_transactions_for_month(df, date_column="ZDATE"):
    
    start = datetime(target_year, target_month, 1)
    end = datetime(target_year + (target_month == 12), (target_month % 12) + 1, 1) - timedelta(seconds=1)

    start_ts = int(start.timestamp() * 1000)
    end_ts = int(end.timestamp() * 1000)

    df[date_column] = pd.to_numeric(df[date_column], errors='coerce')

    filtered_df = df[(df[date_column] >= start_ts) & (df[date_column] <= end_ts)].copy()

    filtered_df[date_column] = (
        pd.to_datetime(filtered_df[date_column], unit='ms')
        .dt.tz_localize('UTC')
        .dt.tz_convert('Asia/Kolkata')
        .dt.strftime("%d-%m-%Y %I:%M %p")
    )

    return filtered_df
