import os
from sqlite_to_sheet_project.data_extraction import extract_transactions_from_sqlite

# Your .mmbak file
DB_FILE = "MMGF(31-07-26-113621).mmbak"

# Extract exactly the same data that goes to Google Sheets
df = extract_transactions_from_sqlite(DB_FILE, previous_month=False)

if df is None or df.empty:
    print("No transactions found.")
else:
    output_file = "INOUTCOME.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Exported {len(df)} rows to {os.path.abspath(output_file)}")