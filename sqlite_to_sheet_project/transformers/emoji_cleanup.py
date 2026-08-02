import re

from sqlite_to_sheet_project.schema.schema import column

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "]+",
    flags=re.UNICODE,
)


def remove_emojis(df, column_key):
    """
    Remove emojis from the specified column.

    Args:
        df: DataFrame
        column_key: COLUMN_SCHEMA key (e.g. "category", "subcategory")
    """

    column_name = column(column_key)

    if column_name in df.columns:
        df[column_name] = (
            df[column_name]
            .fillna("")
            .str.replace(_EMOJI_PATTERN, "", regex=True)
            .str.strip()
        )

    return df