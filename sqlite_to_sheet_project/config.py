import os
from datetime import datetime
from pathlib import Path

LOG_FILE_PATH = 'process_log.log'
DB_FILE = 'temp.mmbak'
# Optional explicit service-account key.  In Cloud Run, the secret may be
# mounted at /secrets/service_account.json; locally, leave this unset and use
# Application Default Credentials (``gcloud auth application-default login``).
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
MOUNTED_SERVICE_ACCOUNT_FILE = "/secrets/service_account.json"
LOCAL_SERVICE_ACCOUNT_FILE = str(
    Path(__file__).resolve().parent.parent / "service_account.json"
)
SPREADSHEET_NAME = "Expenses Datasheet"
ACCOUNTING_APP_FOLDER_NAME="MoneyManager"
PAYMENT_APP_EXPORT_FOLDER_NAME="Paytm_Export"

# For automatic recent data
# Set both to None if you want current month automatically
TARGET_YEAR = None #2025
TARGET_MONTH = None #5

# # For manual month filter data
# TARGET_YEAR = 2025
# TARGET_MONTH = 3

# === Resolve target date ===
now = datetime.now()
target_year = TARGET_YEAR if TARGET_YEAR else now.year
target_month = TARGET_MONTH if TARGET_MONTH else now.month

# === Sheet title based on target month-year ===
MONTH_SHEET_TITLE = datetime(target_year, target_month, 1).strftime("%b-%Y")

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]


# Paytm account name -> Money Manager account name
PAYTM_ACCOUNT_MAP = {
    "State Bank Of India - 66": "SBI",
    "HDFC Bank - 05": "HDFC BANK",
    "HDFC Bank RuPay Credit Card - 98": "HDFC CREDIT CARD",
    "Yes Bank RuPay Credit Card - 44": "Yes Bank UPI CC",
    "IDFC FIRST Rupay Credit Card - 90": "IDFC First Power Plus",
    "Bank Of Baroda Rupay Credit Card - 03": "Uni Card UPI",
    "Slice Small Finance Bank Limited - 22": "Slice Bank",
    "Paytm Postpaid - 42": "Paytm postpaid",
}
