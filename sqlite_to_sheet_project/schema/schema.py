TABLE_SCHEMA = {
    "transaction": {
        "name": "INOUTCOME",
        "alias": "I",
    },
    "from_asset": {
        "name": "ASSETS",
        "alias": "FA",
    },
    "to_asset": {
        "name": "ASSETS",
        "alias": "TA",
    },
    "category": {
        "name": "ZCATEGORY",
        "alias": "C",
    },
        "parent_category": {
        "name": "ZCATEGORY",
        "alias": "P",
    },
}

COLUMN_SCHEMA = {
    "note": {
        "table": "transaction",
        "db": "ZCONTENT",
        "column": "Note",
        "title": "Note",
    },
    "date": {
        "table": "transaction",
        "db": "ZDATE",
        "column": "Date",
        "title": "Date",
    },
    "account_id": {
        "table": "transaction",
        "db": "assetUid",
        "column": "Account ID",
        "title": "Account ID",
    },
    "account": {
        "table": "from_asset",
        "db": "TRIM(NIC_NAME)",
        "column": "Account",
        "title": "Account",
    },
    "from_account": {
        "table": "from_asset",
        "db": "TRIM(NIC_NAME)",
        "column": "From Account",
        "title": "From Account",
    },
    "to_account": {
        "table": "to_asset",
        "db": "TRIM(NIC_NAME)",
        "column": "To Account",
        "title": "To Account",
    },
    "to_account_id": {
        "table": "transaction",
        "db": "toAssetUid",
        "column": "To Account ID",
        "title": "To Account ID",
    },
    "category_id": {
        "table": "transaction",
        "db": "ctgUid",
        "column": "Category ID",
        "title": "Category ID",
    },
    "category": {
        "table": "category",
        "db":   """
            CASE
                WHEN P.uid IS NULL THEN C.NAME
                ELSE P.NAME
            END
            """,
        "column": "Category",
        "title": "Category",
    },
    "subcategory": {
        "table": "category",
        "db": """
                CASE
                    WHEN P.uid IS NULL THEN ''
                    ELSE C.NAME
                END
                """,
        "column": "Subcategory",
        "title": "Subcategory",
    },
    "amount": {
        "table": "transaction",
        "db": "ZMONEY",
        "column": "Amount",
        "title": "Amount",
    },
    "description": {
        "table": "transaction",
        "db": "ZDATA",
        "column": "Description",
        "title": "Description",
    },
    "transaction_type": {
        "table": "transaction",
        "db": "DO_TYPE",
        "column": "Transaction Type",
        "title": "Transaction Type",
    },
    "transaction_id": {
        "table": "transaction",
        "db": "txUidTrans",
        "column": "Transaction ID",
        "title": "Transaction ID",
    },
}

    



def db(key):
    return COLUMN_SCHEMA[key]["db"]


def column(key):
    return COLUMN_SCHEMA[key]["column"]


def title(key):
    return COLUMN_SCHEMA[key]["title"]


def table(table_key):
    return TABLE_SCHEMA[table_key]["name"]


def column_table(column_key):
    return COLUMN_SCHEMA[column_key]["table"]


def table_alias(table_key):
    return TABLE_SCHEMA[table_key]["alias"]


def column_alias(column_key):
    return table_alias(column_table(column_key))