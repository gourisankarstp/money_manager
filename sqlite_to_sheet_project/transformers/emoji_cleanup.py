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

# Remove invisible Unicode characters left behind by emojis
_INVISIBLE_PATTERN = re.compile(r"[\u200B\u200C\u200D\uFE0E\uFE0F]+")


def remove_emojis(df, column_key):
    """
    Remove emojis and invisible Unicode characters from the specified column.

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
            .str.replace(_INVISIBLE_PATTERN, "", regex=True)
            .str.replace("\u00A0", " ", regex=False)  # Replace non-breaking spaces
            .str.replace(r"\s+", " ", regex=True)     # Collapse multiple whitespace
            .str.strip()
        )

    return df