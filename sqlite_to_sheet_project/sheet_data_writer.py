from gspread.utils import rowcol_to_a1


def write_dataframe(
    sheet,
    dataframe,
    title,
    start_row=1,
    start_col=1,
    clear=False,
):
    """
    Writes a DataFrame to a Google Sheet.

    Parameters
    ----------
    sheet : gspread.Worksheet
    dataframe : pandas.DataFrame
    title : str
        Section title (e.g. "Transactions")
    start_row : int
    start_col : int
    clear : bool
        Whether to clear the sheet before writing.

    Returns
    -------
    tuple
        (next_available_row, next_available_col)
    """

    if clear:
        sheet.clear()

    if dataframe is None or dataframe.empty:
        return start_row, start_col

    # title_cell = rowcol_to_a1(start_row, start_col)
    header_cell = rowcol_to_a1(start_row , start_col)
    data_cell = rowcol_to_a1(start_row + 1, start_col)

    # # Section title
    # sheet.update(title_cell, [[title]])

    # Header + Data
    values = [dataframe.columns.tolist()] + dataframe.fillna("").values.tolist()

    sheet.update(header_cell, values)

    next_row = start_row + len(values) + 1
    next_col = start_col + len(dataframe.columns) + 2

    return next_row, next_col

from gspread.utils import rowcol_to_a1


def setup_discrepancy_sheet(
    sheet,
    dataframe,
    start_row=1,
    start_col=1,
):
    """
    Configure Payment_Discrepancy_Record sheet.

    - Freeze header row.
    - Convert Is_Verified column to checkboxes.
    - Turn the entire row green when Is_Verified is TRUE.
    """

    if dataframe is None or dataframe.empty:
        return

    if "Is_Verified" not in dataframe.columns:
        return

    # ---------------------------------------------------------
    # Locate Is_Verified column
    # ---------------------------------------------------------

    verified_col = (
        start_col
        + dataframe.columns.get_loc("Is_Verified")
    )

    first_data_row = start_row + 1
    last_data_row = start_row + len(dataframe)

    # Google Sheets uses zero-based indexes
    verified_column_index = verified_col - 1
    first_data_row_index = first_data_row - 1
    last_data_row_index = last_data_row

    # Column letter, e.g. I
    verified_column_letter = (
        rowcol_to_a1(1, verified_col)
        .rstrip("1")
    )

    # ---------------------------------------------------------
    # Google Sheets requests
    # ---------------------------------------------------------

    requests = [

        # -----------------------------------------------------
        # 1. Freeze header row
        # -----------------------------------------------------

        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "gridProperties": {
                        "frozenRowCount": 1,
                    },
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },

        # -----------------------------------------------------
        # 2. Add checkboxes
        # -----------------------------------------------------

        {
            "setDataValidation": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": first_data_row_index,
                    "endRowIndex": last_data_row_index,
                    "startColumnIndex": verified_column_index,
                    "endColumnIndex": verified_column_index + 1,
                },
                "rule": {
                    "condition": {
                        "type": "BOOLEAN",
                    },
                    "showCustomUi": True,
                    "strict": True,
                },
            }
        },

        # -----------------------------------------------------
        # 3. Green row when verified
        # -----------------------------------------------------

        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": sheet.id,
                            "startRowIndex": first_data_row_index,
                            "endRowIndex": last_data_row_index,
                            "startColumnIndex": start_col - 1,
                            "endColumnIndex": (
                                start_col
                                + len(dataframe.columns)
                                - 1
                            ),
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [
                                {
                                    "userEnteredValue": (
                                        f"=${verified_column_letter}2=TRUE"
                                    )
                                }
                            ],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.180,
                                "green": 0.490,
                                "blue": 0.196,
                            },
                            "textFormat": {
                                "foregroundColor": {
                                    "red": 1.0,
                                    "green": 1.0,
                                    "blue": 1.0,
                                }
                            },
                        }
                    },
                },
                "index": 0,
            }
        },
    ]

    # ---------------------------------------------------------
    # Apply all requests
    # ---------------------------------------------------------

    sheet.spreadsheet.batch_update(
        {
            "requests": requests
        }
    )