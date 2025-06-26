import logging
from config import MONTH_SHEET_TITLE

def get_or_create_monthly_sheet(gc, spreadsheet_name):
    spreadsheet = gc.open(spreadsheet_name)
    sheet_titles = [ws.title for ws in spreadsheet.worksheets()]

    if MONTH_SHEET_TITLE in sheet_titles:
        sheet = spreadsheet.worksheet(MONTH_SHEET_TITLE)
        logging.info(f"Found existing worksheet: {MONTH_SHEET_TITLE}")
    else:
        sheet = spreadsheet.add_worksheet(title=MONTH_SHEET_TITLE, rows=1000, cols=26)
        logging.info(f"Created new worksheet: {MONTH_SHEET_TITLE}")

    return sheet
