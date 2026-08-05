import pandas as pd

from sqlite_to_sheet_project.schema.schema import column


def convert_to_number(df, column_key):
    """
    Convert the specified column to numeric.

    Args:
        df: DataFrame
        column_key: COLUMN_SCHEMA key (e.g. "amount")

    Returns:
        DataFrame with the column converted to numeric.
    """

    column_name = column(column_key)

    if column_name in df.columns:
        df[column_name] = pd.to_numeric(
            df[column_name],
            errors="coerce",
        ).astype("Float64")  # Nullable float dtype

    return df