import logging

import pandas as pd
import pathlib

from sqlite_to_sheet_project.filters import (
    filter_transactions,
    REPORT_TZ,
)


# =============================================================
# READ PAYTM PAYMENTS
# =============================================================

def read_paytm_payments(
    file_path,
    account_map,
    previous_month=False,
):
    """
    Read and normalize Paytm payment records.

    Paytm raw amount conventions:

        -500
            -> Expense
            -> Payment Amount = 500

        +500
            -> Income
            -> Payment Amount = 500

        500
            -> Transfer
            -> Payment Amount = 500

    Time is ignored.

    Output:

        Payment Date
        Payment Amount
        Paytm Account
        Money Manager Account
        Transaction Type
    """

    logging.info(
        f"Reading Paytm export from '{file_path}'."
    )

    # ---------------------------------------------------------
    # 1. Read second worksheet
    # ---------------------------------------------------------

    paytm = pd.read_excel(
        file_path,
        sheet_name=1,
    )

    logging.info(
        f"Paytm export loaded. Rows: {len(paytm)}"
    )

    # ---------------------------------------------------------
    # 2. Validate raw columns
    # ---------------------------------------------------------

    required_columns = [
        "Date",
        "Your Account",
        "Amount",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in paytm.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required Paytm columns: "
            + ", ".join(missing_columns)
        )

    # ---------------------------------------------------------
    # 3. Keep required columns
    # ---------------------------------------------------------

    paytm = paytm[
        required_columns
    ].copy()

    # ---------------------------------------------------------
    # 4. Rename columns
    # ---------------------------------------------------------

    paytm.rename(
        columns={
            "Date": "Payment Date",
            "Your Account": "Paytm Account",
            "Amount": "Raw Amount",
        },
        inplace=True,
    )

    # ---------------------------------------------------------
    # 5. Payment Date
    # ---------------------------------------------------------

    paytm["Payment Date"] = pd.to_datetime(
        paytm["Payment Date"],
        format="%d/%m/%Y",
        errors="coerce",
    ).dt.date

    # ---------------------------------------------------------
    # 5a. Create timestamp for common transaction filtering
    #
    # filter_transactions() expects epoch milliseconds.
    #
    # Paytm only provides a date, so use midnight in the
    # report timezone before converting to UTC epoch ms.
    # ---------------------------------------------------------

    paytm_datetime = pd.to_datetime(
        paytm["Payment Date"],
        errors="coerce",
    )

    paytm_datetime = paytm_datetime.dt.tz_localize(
        REPORT_TZ
    )

    paytm["Payment Date_ms"] = (
        paytm_datetime.dt.as_unit("ms").astype("int64")
    )

    # Keep invalid dates as missing
    paytm.loc[
        paytm["Payment Date"].isna(),
        "Payment Date_ms",
    ] = pd.NA

    logging.info(
        f"Paytm Payment Date_ms range: "
        f"{paytm['Payment Date_ms'].min()} -> "
        f"{paytm['Payment Date_ms'].max()}"
    )

    # ---------------------------------------------------------
    # 6. Preserve raw amount
    # ---------------------------------------------------------

    raw_amount = (
        paytm["Raw Amount"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
    )

    # ---------------------------------------------------------
    # 7. Determine Transaction Type
    # ---------------------------------------------------------

    paytm["Transaction Type"] = "Transfer"

    # Negative Paytm amount = Expense
    paytm.loc[
        raw_amount.str.startswith("-"),
        "Transaction Type",
    ] = "Expense"

    # Explicit positive amount = Income
    paytm.loc[
        raw_amount.str.startswith("+"),
        "Transaction Type",
    ] = "Income"

    # ---------------------------------------------------------
    # 8. Convert amount to numeric
    # ---------------------------------------------------------

    paytm["Payment Amount"] = pd.to_numeric(
        raw_amount
        .str.replace("+", "", regex=False)
        .str.replace("-", "", regex=False),
        errors="coerce",
    )

    # ---------------------------------------------------------
    # 9. Paytm Account
    # ---------------------------------------------------------

    paytm["Paytm Account"] = (
        paytm["Paytm Account"]
        .astype("string")
        .str.strip()
    )

    # ---------------------------------------------------------
    # 10. Account Mapping
    # ---------------------------------------------------------

    paytm["Money Manager Account"] = (
        paytm["Paytm Account"]
        .map(account_map)
    )

    # ---------------------------------------------------------
    # 11. Log unmapped accounts
    # ---------------------------------------------------------

    unmapped_accounts = (
        paytm.loc[
            paytm["Money Manager Account"].isna(),
            "Paytm Account",
        ]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if unmapped_accounts:

        logging.warning(
            "Unmapped Paytm accounts found:"
        )

        for account in unmapped_accounts:
            logging.warning(
                f"  Paytm account: {account}"
            )

    # ---------------------------------------------------------
    # 12. Remove invalid rows
    # ---------------------------------------------------------

    invalid_rows = (
        paytm["Payment Date"].isna()
        | paytm["Payment Amount"].isna()
        | paytm["Paytm Account"].isna()
    )

    invalid_count = int(
        invalid_rows.sum()
    )

    logging.info(
        f"Paytm invalid rows: "
        f"{invalid_count} / {len(paytm)}"
    )

    if invalid_count:

        logging.warning(
            f"Removing {invalid_count} invalid "
            f"Paytm records."
        )

        paytm = paytm[
            ~invalid_rows
        ].copy()

    logging.info(
        f"Paytm rows BEFORE reconciliation-period filter: "
        f"{len(paytm)}"
    )

    # ---------------------------------------------------------
    # 12a. Filter by report month
    #
    # All month/timezone logic is handled centrally by
    # filter_transactions().
    # ---------------------------------------------------------

    paytm = filter_transactions(
        paytm,
        date_column="Payment Date_ms",
        previous_month=previous_month,
    )

    logging.info(
        f"Paytm rows AFTER reconciliation-period filter: "
        f"{len(paytm)}"
    )

    # ---------------------------------------------------------
    # 12b. Remove helper date column
    # ---------------------------------------------------------

    paytm.drop(
        columns=["Payment Date_ms"],
        inplace=True,
    )

    # ---------------------------------------------------------
    # 13. Final normalized columns
    # ---------------------------------------------------------

    paytm = paytm[
        [
            "Payment Date",
            "Payment Amount",
            "Paytm Account",
            "Money Manager Account",
            "Transaction Type",
        ]
    ]

    # ---------------------------------------------------------
    # 14. Logging
    # ---------------------------------------------------------

    logging.info(
        f"Paytm payment records ready for "
        f"reconciliation: {len(paytm)}"
    )

    type_counts = (
        paytm["Transaction Type"]
        .value_counts()
        .to_dict()
    )

    logging.info(
        f"Paytm transaction types: {type_counts}"
    )

    # ---------------------------------------------------------
    # DEBUG: ₹40 records
    # ---------------------------------------------------------

    print("\n===== NORMALIZED PAYTM ₹40 =====")

    print(
        paytm[
            paytm["Payment Amount"]
            .astype(float)
            .eq(40)
        ][
            [
                "Payment Date",
                "Payment Amount",
                "Paytm Account",
                "Money Manager Account",
                "Transaction Type",
            ]
        ].to_string(index=False)
    )

    # ---------------------------------------------------------
    # DEBUG CSV
    # ---------------------------------------------------------

    csv_path = pathlib.Path(
        "debug_paytm.csv"
    ).resolve()

    paytm.to_csv(
        csv_path,
        index=False,
    )

    return paytm