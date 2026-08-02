from sqlite_to_sheet_project.mergers.mapping import (
    get_transaction_column,
    get_transfer_column,
)


def map_accounts(df, asset_uid_dict):
    if "assetUid" in df.columns:
        df[get_transaction_column("account")] = df["assetUid"].map(asset_uid_dict)

    return df


def map_transfer_accounts(df, asset_uid_dict):
    if "assetUid" in df.columns:
        df[get_transfer_column("account")] = df["assetUid"].map(asset_uid_dict)

    if "toAssetUid" in df.columns:
        df[get_transfer_column("to_account")] = df["toAssetUid"].map(asset_uid_dict)

    return df