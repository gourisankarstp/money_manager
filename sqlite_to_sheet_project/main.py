import logging
import gspread
import os

from logger_setup import setup_logger
from config import DB_FILE, SPREADSHEET_NAME
from google_services import get_drive_and_creds, download_latest_sqlite_file
from data_extraction import extract_transactions_from_sqlite
from sheet_writer import get_or_create_monthly_sheet

def main(request=None):
    setup_logger()
    logging.info("Function started.")

    try:
        creds, drive_service = get_drive_and_creds()
        file_path = download_latest_sqlite_file(drive_service)
        if not file_path:
            return "No matching SQLite files found.", 404

        df = extract_transactions_from_sqlite(file_path)
        if df is None or df.empty:
            return "No valid transaction data found.", 204

        gc = gspread.authorize(creds)
        sheet = get_or_create_monthly_sheet(gc, SPREADSHEET_NAME)

        sheet.clear()
        sheet.append_rows([df.columns.tolist()] + df.values.tolist())
        logging.info("Data written to Google Sheet.")

        # After df is processed
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
    print(f"Status: {status}")
    print(f"Result: {result}")
