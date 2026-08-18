import logging

import pandas as pd


# =============================================================
# RECONCILE PAYTM WITH MONEY MANAGER
# =============================================================

def reconcile_paytm_with_money_manager(
    paytm_df,
    money_manager_df,
):
    """
    Reconcile Paytm payments against Money Manager.

    Paytm is the source being verified.

    Paytm data is expected to already be normalized.

    Money Manager data is normalized here only to create
    the common fields required for reconciliation.

    Matching key:

        Payment Date
        Payment Amount
        Money Manager Account
        Transaction Type

    Status:

        MATCHED
        AMBIGUOUS
        MISSING_IN_MONEY_MANAGER
        UNMAPPED_ACCOUNT

    All transaction types are considered.

    Transaction Type is NOT identified or changed here.
    Payment Amount is NOT changed or converted using abs().
    """

    paytm = paytm_df.copy()
    money_manager = money_manager_df.copy()

    # =========================================================
    # 1. NORMALIZE MONEY MANAGER DATE
    # =========================================================

    money_manager["Payment Date"] = pd.to_datetime(
        money_manager["Date"],
        format="%d-%m-%Y %I:%M %p",
        errors="coerce",
    ).dt.date

    # =========================================================
    # 2. NORMALIZE MONEY MANAGER AMOUNT
    # =========================================================

    money_manager["Payment Amount"] = pd.to_numeric(
        money_manager["Amount"],
        errors="coerce",
    )

    # =========================================================
    # 3. NORMALIZE MONEY MANAGER ACCOUNT
    # =========================================================

    money_manager["Money Manager Account"] = (
        money_manager["Account"]
        .astype("string")
        .str.strip()
    )

    # =========================================================
    # 4. NORMALIZE MONEY MANAGER TRANSACTION TYPE
    # =========================================================

    money_manager["Transaction Type"] = (
        money_manager["Transaction Type"]
        .astype("string")
        .str.strip()
    )

    # =========================================================
    # 5. MATCHING KEY
    # =========================================================

    key_columns = [
        "Payment Date",
        "Payment Amount",
        "Money Manager Account",
        "Transaction Type",
    ]

    # =========================================================
    # 6. COUNT PAYTM RECORDS
    # =========================================================

    paytm_counts = (
        paytm
        .groupby(
            key_columns,
            dropna=False,
        )
        .size()
        .reset_index(
            name="Paytm Count"
        )
    )

    # =========================================================
    # 7. COUNT MONEY MANAGER RECORDS
    # =========================================================

    money_manager_counts = (
        money_manager
        .groupby(
            key_columns,
            dropna=False,
        )
        .size()
        .reset_index(
            name="Money Manager Count"
        )
    )

    # =========================================================
    # 8. COMPARE PAYTM AGAINST MONEY MANAGER
    # =========================================================

    reconciliation = paytm_counts.merge(
        money_manager_counts,
        on=key_columns,
        how="left",
    )

    reconciliation["Money Manager Count"] = (
        reconciliation["Money Manager Count"]
        .fillna(0)
        .astype(int)
    )

    # =========================================================
    # 9. DETERMINE STATUS
    # =========================================================

    reconciliation["Status"] = "MATCHED"

    # ---------------------------------------------------------
    # Unmapped Money Manager account
    # ---------------------------------------------------------

    unmapped_account = (
        reconciliation["Money Manager Account"].isna()
        |
        reconciliation["Money Manager Account"]
        .astype("string")
        .str.strip()
        .eq("")
    )

    reconciliation.loc[
        unmapped_account,
        "Status",
    ] = "UNMAPPED_ACCOUNT"

    # ---------------------------------------------------------
    # No matching Money Manager transaction
    # ---------------------------------------------------------

    reconciliation.loc[
        ~unmapped_account
        & reconciliation["Money Manager Count"].eq(0),
        "Status",
    ] = "MISSING_IN_MONEY_MANAGER"

    # ---------------------------------------------------------
    # More Paytm records than Money Manager records
    # ---------------------------------------------------------

    reconciliation.loc[
        ~unmapped_account
        & reconciliation["Money Manager Count"].gt(0)
        & (
            reconciliation["Money Manager Count"]
            < reconciliation["Paytm Count"]
        ),
        "Status",
    ] = "AMBIGUOUS"

    # =========================================================
    # 10. KEEP DISCREPANCIES ONLY
    # =========================================================

    discrepancy_df = reconciliation[
        reconciliation["Status"] != "MATCHED"
    ].copy()

    # =========================================================
    # 11. ADD ORIGINAL PAYTM ACCOUNT
    # =========================================================

    paytm_accounts = (
        paytm[
            [
                "Payment Date",
                "Payment Amount",
                "Money Manager Account",
                "Transaction Type",
                "Paytm Account",
            ]
        ]
        .drop_duplicates()
    )

    discrepancy_df = discrepancy_df.merge(
        paytm_accounts,
        on=[
            "Payment Date",
            "Payment Amount",
            "Money Manager Account",
            "Transaction Type",
        ],
        how="left",
    )

    # =========================================================
    # 12. ADD TRANSACTION ID
    # =========================================================

    discrepancy_df.insert(
        0,
        "Transaction_ID",
        [
            f"PAYTM_{i:04d}"
            for i in range(1, len(discrepancy_df) + 1)
        ],
    )

    # =========================================================
    # 13. ADD VERIFICATION FLAG
    # =========================================================

    discrepancy_df["Is_Verified"] = False

    # =========================================================
    # 14. ARRANGE OUTPUT COLUMNS
    # =========================================================

    discrepancy_df = discrepancy_df[
        [
            "Transaction_ID",
            "Payment Date",
            "Payment Amount",
            "Paytm Account",
            "Money Manager Account",
            "Transaction Type",
            "Paytm Count",
            "Money Manager Count",
            "Status",
            "Is_Verified",
        ]
    ]

    # =========================================================
    # 15. FORMAT PAYMENT DATE
    # =========================================================

    discrepancy_df["Payment Date"] = (
        pd.to_datetime(
            discrepancy_df["Payment Date"],
            errors="coerce",
        )
        .dt.strftime("%d-%m-%Y")
    )

    # =========================================================
    # 16. FORMAT PAYMENT AMOUNT
    # =========================================================

    discrepancy_df["Payment Amount"] = (
        pd.to_numeric(
            discrepancy_df["Payment Amount"],
            errors="coerce",
        )
        .apply(
            lambda x: (
                f"₹{x:,.2f}"
                if pd.notna(x)
                else ""
            )
        )
    )

    # =========================================================
    # 17. REMOVE NaN / NaT
    # =========================================================

    discrepancy_df = discrepancy_df.fillna("")

    # =========================================================
    # 18. LOGGING
    # =========================================================

    logging.info(
        f"Paytm reconciliation completed. "
        f"Total Paytm groups: {len(reconciliation)}, "
        f"Discrepancies: {len(discrepancy_df)}"
    )

    return discrepancy_df