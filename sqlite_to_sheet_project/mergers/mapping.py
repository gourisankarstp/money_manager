def get_transaction_column(key):
    return EXPORT_MAPPING[key]["transaction_column"]


def get_transfer_column(key):
    return EXPORT_MAPPING[key]["transfer_column"]


def get_title(key):
    return EXPORT_MAPPING[key]["title"]
EXPORT_COLUMNS = [
    "note",
    "date",
    "account",
    "amount",
    "description",
    "category",
    "subcategory",
    "transaction_type",
    "to_account",
]
EXPORT_MAPPING = {
    "note": {
        "title": "Note",
        "transaction_column": "Note",
        "transfer_column": "Note",
        "default": "",
    },
    "date": {
        "title": "Date",
        "transaction_column": "Date",
        "transfer_column": "Date",
        "default": "",
    },
    "account": {
        "title": "Account",
        "transaction_column": "Account",
        "transfer_column": "From Account",
        "default": "",
    },
    "amount": {
        "title": "Amount",
        "transaction_column": "Amount",
        "transfer_column": "Amount",
        "default": 0,
    },
    "description": {
        "title": "Description",
        "transaction_column": "Description",
        "transfer_column": "Description",
        "default": "",
    },
    "category": {
        "title": "Category",
        "transaction_column": "Category",
        "transfer_column": None,
        "default": "",
    },
    "subcategory": {
        "title": "Subcategory",
        "transaction_column": "Subcategory",
        "transfer_column": None,
        "default": "",
    },
    "transaction_type": {
        "title": "Transaction Type",
        "transaction_column": "Transaction Type",
        "transfer_column": "Transaction Type",
        "default": "",
    },
    "to_account": {
        "title": "To Account",
        "transaction_column": None,
        "transfer_column": "To Account",
        "default": "",
    },
}