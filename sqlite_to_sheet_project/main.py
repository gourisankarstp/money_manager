import logging
import gspread
import os

from sqlite_to_sheet_project.logger_setup import setup_logger

from sqlite_to_sheet_project.config import (
    SPREADSHEET_NAME,
    PAYTM_ACCOUNT_MAP,
)

from sqlite_to_sheet_project.google_services import (
    get_drive_and_creds,
    download_latest_sqlite_file,
    download_latest_paytm_export,
)

from sqlite_to_sheet_project.data_extraction import (
    extract_transactions_from_sqlite,
)

from sqlite_to_sheet_project.sheet_writer import (
    get_or_create_monthly_sheet,
    get_or_create_sheet,
)

from sqlite_to_sheet_project.sheet_data_writer import (
    write_dataframe,
)

from sqlite_to_sheet_project.mergers import (
    merge_transactions,
)

from sqlite_to_sheet_project.paytm_app_data_processor.paytm_reconciliation import (
    read_paytm_payments,
)

from sqlite_to_sheet_project.paytm_app_data_processor.payment_reconciliation import (
    reconcile_paytm_with_money_manager,
)


def main(request=None, previous=False):
    setup_logger()
    logging.info("Function started.")

    file_path = None
    paytm_file_path = None

    try:
        # =====================================================
        # 1. Google Drive
        # =====================================================

        creds, drive_service = get_drive_and_creds()

        # =====================================================
        # 2. Money Manager
        # =====================================================

        file_path = download_latest_sqlite_file(
            drive_service
        )

        if not file_path:
            return "No matching SQLite files found.", 404

        transaction_df, transfer_df = (
            extract_transactions_from_sqlite(
                file_path,
                previous_month=previous,
            )
        )

        transaction_df = merge_transactions(
            transaction_df,
            transfer_df
        )
        # Debug: export Money Manager transactions
        transaction_df.to_csv(
            "transaction_debug.csv",
            index=False,
            encoding="utf-8-sig",
        )
        if transaction_df.empty:
            return "No valid transaction data found.", 204

        logging.info(
            f"Money Manager processing completed. "
            f"Transactions: {len(transaction_df)}"
        )

        # =====================================================
        # 3. Paytm reconciliation
        # =====================================================

        discrepancy_df = None

        paytm_file_path = download_latest_paytm_export(
            drive_service
        )

        if paytm_file_path:
            try:
                paytm_df = read_paytm_payments(
                    paytm_file_path,
                    PAYTM_ACCOUNT_MAP,
                    previous_month=previous
                )

                # =================================================
                # DEBUG: Compare ₹40 transaction
                # =================================================

                print("\n===== PAYTM ₹40 =====")
                print(
                    paytm_df[
                        paytm_df["Payment Amount"].eq(40)
                    ].to_string(index=False)
                )

                print("\n===== MONEY MANAGER ₹40 =====")
                print(
                    transaction_df[
                        transaction_df["Amount"]
                        .astype(float)
                        .eq(40)
                    ].to_string(index=False)
                )

                # =================================================
                # Reconciliation
                # =================================================

                discrepancy_df = (
                    reconcile_paytm_with_money_manager(
                        paytm_df,
                        transaction_df,
                    )
                )

                logging.info(
                    f"Paytm reconciliation completed. "
                    f"Discrepancies: {len(discrepancy_df)}"
                )

            finally:
                if os.path.exists(paytm_file_path):
                    os.remove(paytm_file_path)

                    logging.info(
                        f"Temp Paytm file "
                        f"{paytm_file_path} removed."
                    )

        else:
            logging.warning(
                "No Paytm export found. "
                "Skipping payment reconciliation."
            )

        # =====================================================
        # 4. Google Sheet authorization
        # =====================================================

        gc = gspread.authorize(creds)

        # =====================================================
        # 5. Existing Money Manager monthly sheet
        # =====================================================

        sheet = get_or_create_monthly_sheet(
            gc,
            SPREADSHEET_NAME,
            previous,
        )

        # =====================================================
        # 6. Write Transactions
        # =====================================================

        write_dataframe(
            sheet=sheet,
            dataframe=transaction_df,
            title="Transactions",
            start_row=1,
            start_col=1,
            clear=True,
        )

        # =====================================================
        # 7. Write Payment Discrepancies
        # =====================================================

        if discrepancy_df is not None:
            discrepancy_sheet = get_or_create_sheet(
                gc,
                SPREADSHEET_NAME,
                "Payment_Discrepancy_Record",
            )

            write_dataframe(
                sheet=discrepancy_sheet,
                dataframe=discrepancy_df,
                title="Payment_Discrepancy_Record",
                start_row=1,
                start_col=1,
                clear=True,
            )

            logging.info(
                "Payment discrepancy data written to "
                "'Payment_Discrepancy_Record'."
            )

        # =====================================================
        # 8. Cleanup Money Manager temporary file
        # =====================================================

        logging.info("Data written to Google Sheet.")

        return "Success", 200

    except Exception as e:
        logging.exception("Error occurred.")
        return f"Error: {str(e)}", 500

    finally:
        # =====================================================
        # 9. Always remove Money Manager temporary file
        # =====================================================

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

            logging.info(
                f"Temp file {file_path} removed "
                f"after processing."
            )


if __name__ == "__main__":
    class DummyRequest:
        method = "GET"

    result, status = main(DummyRequest())