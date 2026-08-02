import pandas as pd

def format_dates(df):
    df = df.copy()

    df["Date"] = pd.to_numeric(df["Date"], errors="coerce")

    df["Date"] = (
        pd.to_datetime(
            df["Date"],
            unit="ms",
            utc=True,
        )
        .dt.tz_convert("Asia/Kolkata")
        .dt.strftime("%d-%m-%Y %I:%M %p")
    )

    return df