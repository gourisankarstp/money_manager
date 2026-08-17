import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

from sqlite_to_sheet_project.config import (
    target_year,
    target_month,
)

# Default report timezone
REPORT_TIMEZONE = "Asia/Kolkata"

REPORT_TZ = ZoneInfo(REPORT_TIMEZONE)
UTC = ZoneInfo("UTC")


def filter_transactions(df, date_column="Date", previous_month=False):
    logging.info(
        f"filter_transactions: "
        f"target_year={target_year}, "
        f"target_month={target_month}, "
        f"previous_month={previous_month}"
    )

    if previous_month:
        target_start = datetime(
            target_year,
            target_month,
            1,
            tzinfo=REPORT_TZ
        )

        end = target_start - timedelta(seconds=1)
        start = datetime(end.year, end.month, 1, tzinfo=REPORT_TZ)

    else:
        start = datetime(
            target_year,
            target_month,
            1,
            tzinfo=REPORT_TZ
        )

        next_month = datetime(
            target_year + (target_month == 12),
            (target_month % 12) + 1,
            1,
            tzinfo=REPORT_TZ
        )

        end = next_month - timedelta(seconds=1)

    # Convert report boundaries to UTC epoch milliseconds
    start_ts = int(start.astimezone(UTC).timestamp() * 1000)
    end_ts = int(end.astimezone(UTC).timestamp() * 1000)

    logging.info(
        f"Filter period: "
        f"start={start}, "
        f"end={end}, "
        f"start_ts={start_ts}, "
        f"end_ts={end_ts}"
    )

    logging.info(
        f"Input {date_column} range: "
        f"{df[date_column].min()} -> {df[date_column].max()}"
    )

    df = df.copy()
    df[date_column] = pd.to_numeric(df[date_column], errors="coerce")

    filtered_df = df[
        (df[date_column] >= start_ts) &
        (df[date_column] <= end_ts)
    ].copy()

    logging.info(
        f"Rows after timestamp filter: {len(filtered_df)}"
    )

    filtered_df.sort_values(by=date_column,ascending=True, inplace=True)

    # Display in report timezone
    filtered_df[date_column] = (
        pd.to_datetime(filtered_df[date_column], unit="ms", utc=True)
        .dt.tz_convert(REPORT_TZ)
        .dt.strftime("%d-%m-%Y %I:%M %p")
    )

    return filtered_df