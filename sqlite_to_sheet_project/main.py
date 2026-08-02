import logging
import gspread
import os

from sqlite_to_sheet_project.logger_setup import setup_logger
from sqlite_to_sheet_project.config import SPREADSHEET_NAME
from sqlite_to_sheet_project.google_services import (
    get_drive_and_creds,
    download_latest_sqlite_file,
)
from sqlite_to_sheet_project.data_extraction import (
    extract_transactions_from_sqlite,
)
from sqlite_to_sheet_project.sheet_writer import (
    get_or_create_monthly_sheet,
)
from sqlite_to_sheet_project.sheet_data_writer import (
    write_dataframe,
)
from sqlite_to_sheet_project.mergers import merge_transactions


def main(request=None, previous=False):
    setup_logger()
    logging.info("Function started.")

    try:
        creds, drive_service = get_drive_and_creds()

        file_path = download_latest_sqlite_file(drive_service)

        if not file_path:
            return "No matching SQLite files found.", 404

        transaction_df, transfer_df = extract_transactions_from_sqlite(
            file_path,
            previous_month=previous,
        )

        transaction_df = merge_transactions(
                transaction_df,
                transfer_df
            )

        if transaction_df.empty:
            return "No valid transaction data found.", 204


        gc = gspread.authorize(creds)

        sheet = get_or_create_monthly_sheet(
            gc,
            SPREADSHEET_NAME,
            previous,
        )

        # Write Transactions
        _, next_col = write_dataframe(
            sheet=sheet,
            dataframe=transaction_df,
            title="Transactions",
            start_row=1,
            start_col=1,
            clear=True,
        )

        # # Write Transfers
        # write_dataframe(
        #     sheet=sheet,
        #     dataframe=transfer_df,
        #     title="Transfers",
        #     start_row=1,
        #     start_col=next_col,
        # )

        logging.info("Data written to Google Sheet.")

        os.remove(file_path)
        logging.info(f"Temp file {file_path} removed after processing.")

        return "Success", 200

    except Exception as e:
        logging.exception("Error occurred.")
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    class DummyRequest:
        method = "GET"

    result, status = main(DummyRequest())