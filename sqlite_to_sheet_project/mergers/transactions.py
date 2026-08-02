import pandas as pd

from .mapping import (
    EXPORT_MAPPING,
    EXPORT_COLUMNS,
)


def map_dataframe(df, source_type):
    """
    Convert a source dataframe to the common export schema.

    source_type:
        "transaction"
        "transfer"
    """

    export_df = pd.DataFrame(index=df.index)

    for key in EXPORT_COLUMNS:
        mapping = EXPORT_MAPPING[key]

        source_column = mapping[f"{source_type}_column"]

        if source_column is None:
            export_df[mapping["title"]] = mapping["default"]

        elif source_column in df.columns:
            export_df[mapping["title"]] = df[source_column]

        else:
            export_df[mapping["title"]] = mapping["default"]

    return export_df


def merge_transactions(
    transaction_df,
    transfer_df,
    date_column="Date",
    sort=True,
):
    """
    Merge transaction and transfer dataframes into a common export format.
    """

    transaction_df = map_dataframe(
        transaction_df,
        "transaction",
    )

    transfer_df = map_dataframe(
        transfer_df,
        "transfer",
    )

    merged_df = pd.concat(
        [
            transaction_df,
            transfer_df,
        ],
        ignore_index=True,
    )

    if sort:
        merged_df = merged_df.sort_values(
            by=date_column,
            ascending=True,
            ignore_index=True,
        )

    return merged_df


def sort_transactions(
    transaction_df,
    date_column="Date",
):
    """
    Sort transactions chronologically.
    """

    return transaction_df.sort_values(
        by=date_column,
        ascending=True,
        ignore_index=True,
    )