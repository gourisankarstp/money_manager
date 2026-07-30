import logging
from datetime import datetime, timedelta
from sqlite_to_sheet_project.config import target_year, target_month
from gspread_formatting import format_cell_range, CellFormat, NumberFormat

def get_or_create_monthly_sheet(gc, spreadsheet_name,previous_month=False):
    spreadsheet = gc.open(spreadsheet_name)
    sheet_titles = [ws.title for ws in spreadsheet.worksheets()]

    if previous_month:
        # Assume target date is the 1st of current target month
        target_date = datetime(target_year, target_month, 1)

        # Go to last day of previous month by subtracting 1 second from the 1st of this month
        end = target_date - timedelta(seconds=1)

        # Start of previous month is always day 1 of that month
        start = datetime(end.year, end.month, 1)
        # === Sheet title based on target month-year ===
        MONTH_SHEET_TITLE = start.strftime("%b-%Y")
    else:
        # === Sheet title based on target month-year ===
        MONTH_SHEET_TITLE = datetime(target_year, target_month, 1).strftime("%b-%Y")


    if MONTH_SHEET_TITLE in sheet_titles:
        sheet = spreadsheet.worksheet(MONTH_SHEET_TITLE)
        logging.info(f"Found existing worksheet: {MONTH_SHEET_TITLE}")
    else:
        sheet = spreadsheet.add_worksheet(title=MONTH_SHEET_TITLE, rows=1000, cols=26)
        logging.info(f"Created new worksheet: {MONTH_SHEET_TITLE}")

    # === Format the "Amount" column as Indian Rupees ===
    try:
        format_cell_range(
            sheet,
            'D2:D',  # Amount column (after Note, Date, and Account)
            CellFormat(
                numberFormat=NumberFormat(
                    type='CURRENCY',
                    pattern='₹#,##0.00'
                )
            )
        )
        logging.info("Formatted 'Amount' column as Indian Rupees.")
    except Exception as e:
        logging.warning(f"Could not format 'Amount' column: {e}")

    return sheet
