from sqlite_to_sheet_project.mergers.mapping import EXPORT_MAPPING


TRANSACTION_COLUMNS = [
    "note",
    "date",
    "account",
    "amount",
    "description",
    "category",
    "subcategory",
    "transaction_type",
]


TRANSFER_COLUMNS = [
    "note",
    "date",
    "account",
    "amount",
    "description",
    "transaction_type",
    "to_account",
]


def rename_columns(df):
    """
    Rename Money Manager columns to internal source column names.
    """

    return df.rename(
        columns={
            "ZDATE": "Date",
            "ZMONEY": "Amount",
            "ZCONTENT": "Description",
            "ZDATA": "Note",
            "txUidTrans": "Transaction ID",
        }
    )


def _get_columns(column_keys, source_type):
    """
    Returns the actual dataframe column names for the given source.
    """

    columns = []

    for key in column_keys:

        column_name = EXPORT_MAPPING[key].get(f"{source_type}_column")

        if column_name:
            columns.append(column_name)

    return columns


def reorder_transaction_columns(df):
    """
    Reorder transaction dataframe columns.
    """

    columns = _get_columns(
        TRANSACTION_COLUMNS,
        "transaction",
    )

    return df[[c for c in columns if c in df.columns]]


def reorder_transfer_columns(df):
    """
    Reorder transfer dataframe columns.
    """

    columns = _get_columns(
        TRANSFER_COLUMNS,
        "transfer",
    )

    return df[[c for c in columns if c in df.columns]]