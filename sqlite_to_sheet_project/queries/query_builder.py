from sqlite_to_sheet_project.schema.schema import (
    db,
    column,
    table,
    table_alias,
    column_alias
)


def build_select_clause(column_keys):
    columns = []

    for key in column_keys:
        columns.append(
            f'{column_alias(key)}.{db(key)} AS "{column(key)}"'
        )

    return ",\n    ".join(columns)


def build_query(
    table_key,
    columns,
    joins=None,
    where=None,
    order_by_column=None,
):
    query = f"""
        SELECT
        {build_select_clause(columns)}
        FROM {table(table_key)} {table_alias(table_key)}
    """

    if joins:
        query += "\n" + "\n".join(joins)

    if where:
        query += f"\nWHERE\n    {where}"

    if order_by_column:
        query += (
            f"\nORDER BY "
            f"{column_alias(order_by_column)}."
            f"{db(order_by_column)};"
        )

    return query