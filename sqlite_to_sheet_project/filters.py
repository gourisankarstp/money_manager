import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlite_to_sheet_project.config import (
    target_year,
    target_month,
)

# Default report timezone
REPORT_TIMEZONE = "Asia/Kolkata"

REPORT_TZ = ZoneInfo(REPORT_TIMEZONE)
UTC = ZoneInfo("UTC")


def filter_transactions(df, date_column="Date", previous_month=False):

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

    df = df.copy()
    df[date_column] = pd.to_numeric(df[date_column], errors="coerce")

    filtered_df = df[
        (df[date_column] >= start_ts) &
        (df[date_column] <= end_ts)
    ].copy()

    filtered_df.sort_values(by=date_column,ascending=True, inplace=True)

    # Display in report timezone
    filtered_df[date_column] = (
        pd.to_datetime(filtered_df[date_column], unit="ms", utc=True)
        .dt.tz_convert(REPORT_TZ)
        .dt.strftime("%d-%m-%Y %I:%M %p")
    )

    return filtered_df