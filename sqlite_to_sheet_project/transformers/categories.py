def map_categories(df, category_uid_dict):
    """
    Maps Category/Subcategory.
    """

    if "ctgUid" not in df.columns:
        return df

    df["Category"] = df["ctgUid"].map(
        lambda x: category_uid_dict.get(x, {}).get("Category", "")
    )

    df["Subcategory"] = df["ctgUid"].map(
        lambda x: category_uid_dict.get(x, {}).get("Subcategory", "")
    )

    return df