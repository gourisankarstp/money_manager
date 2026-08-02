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

    title_cell = rowcol_to_a1(start_row, start_col)
    header_cell = rowcol_to_a1(start_row + 1, start_col)
    data_cell = rowcol_to_a1(start_row + 2, start_col)

    # Section title
    sheet.update(title_cell, [[title]])

    # Header + Data
    values = [dataframe.columns.tolist()] + dataframe.fillna("").values.tolist()

    sheet.update(header_cell, values)

    next_row = start_row + len(values) + 1
    next_col = start_col + len(dataframe.columns) + 2

    return next_row, next_col