import pandas as pd

def compare_dataframes(df1, df2, unique_column):
    """
    Compares two dataframes based on a unique column to find matching rows, mismatching rows, new rows, and removed rows.

    Args:
    df1 (pd.DataFrame): First dataframe.
    df2 (pd.DataFrame): Second dataframe.
    unique_column (str): Column name to base the comparison on.

    Returns:
    dict: A dictionary with lists of matching rows, mismatching rows, new rows in df2, and removed rows from df1.
    """
    # Validate that the unique column exists in both dataframes
    if unique_column not in df1.columns or unique_column not in df2.columns:
        raise ValueError(f"The unique column '{unique_column}' must be present in both dataframes.")

    # Set the unique column as index for easier comparison
    df1.set_index(unique_column, inplace=True, drop=False)
    df2.set_index(unique_column, inplace=True, drop=False)

    # Identify common and unique keys
    common_keys = df1.index.intersection(df2.index)
    new_keys_in_df2 = df2.index.difference(df1.index)
    removed_keys_from_df1 = df1.index.difference(df2.index)

    # Matching and mismatching rows
    matching_rows = []
    mismatching_rows = []
    for key in common_keys:
        row_df1 = df1.loc[key]
        row_df2 = df2.loc[key]
        if row_df1.equals(row_df2):
            matching_rows.append(row_df2.to_dict())
        else:
            mismatching_rows.append({
                "df1": row_df1.to_dict(),
                "df2": row_df2.to_dict()
            })

    # New rows in df2
    new_rows = [df2.loc[key].to_dict() for key in new_keys_in_df2]
    # Removed rows from df1
    removed_rows = [df1.loc[key].to_dict() for key in removed_keys_from_df1]

    return {
        "matching_rows": matching_rows,
        "mismatching_rows": mismatching_rows,
        "new_rows": new_rows,
        "removed_rows": removed_rows
    }

# Example dataframes to test the function
# These will be commented out for development purposes
# df1 = pd.DataFrame({
#     'ID': [1, 2, 3, 5],
#     'Name': ['Alice', 'Bob', 'Charlie', 'Eve'],
#     'Age': [25, 30, 35, 28]
# })

# df2 = pd.DataFrame({
#     'ID': [1, 2, 4],
#     'Name': ['Alice', 'Bob', 'David'],
#     'Age': [25, 32, 40]
# })

# compare_dataframes_by_rows_with_removals(df1, df2, 'ID')
