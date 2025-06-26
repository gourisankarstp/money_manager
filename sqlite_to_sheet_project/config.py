from datetime import datetime

LOG_FILE_PATH = 'process_log.log'
DB_FILE = 'temp.mmbak'
SERVICE_ACCOUNT_FILE = "/app/service_account.json"
SPREADSHEET_NAME = "Expense Plan"

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
