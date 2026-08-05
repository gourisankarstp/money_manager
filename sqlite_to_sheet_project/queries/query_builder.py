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
        column_db = db(key)
        alias = column_alias(key)

        # If it's already a SQL expression, inject the table alias
        if any(
            keyword in column_db.upper()
            for keyword in ("CASE", "COALESCE", "IFNULL", "(", "||")
        ):
            column_sql = column_db.replace(
                "NIC_NAME",
                f"{alias}.NIC_NAME",
            )

            columns.append(
                f'{column_sql} AS "{column(key)}"'
            )
        else:
            columns.append(
                f'{alias}.{column_db} AS "{column(key)}"'
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