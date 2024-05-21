import pandas as pd

def compare_dataframes(df1, df2, unique_column):
    """
    Compares two dataframes based on a unique column to find matching rows, mismatching rows, new rows, and removed rows.

    Args:
    df1 (pd.DataFrame): First dataframe (new dataframe).
    df2 (pd.DataFrame): Second dataframe (old dataframe).
    unique_column (str): Column name to base the comparison on.

    Returns:
    dict: A dictionary with lists of new rows, updated rows, and removed rows.
    """
    # Validate that the unique column exists in both dataframes
    if unique_column not in df1.columns or unique_column not in df2.columns:
        raise ValueError(f"The unique column '{unique_column}' must be present in both dataframes.")

    # Set the unique column as index for easier comparison
    df1.set_index(unique_column, inplace=True)
    df2.set_index(unique_column, inplace=True)

    # Identify common and unique keys
    common_keys = df1.index.intersection(df2.index)
    new_keys_in_df1 = df1.index.difference(df2.index)
    removed_keys_from_df2 = df2.index.difference(df1.index)

    # Initialize lists for new, updated, and removed rows
    new_rows = df1.loc[new_keys_in_df1].reset_index().to_dict(orient='records')
    removed_rows = df2.loc[removed_keys_from_df2].reset_index().to_dict(orient='records')
    updated_rows = []

    # Check for mismatched rows (updated rows)
    for key in common_keys:
        if not df1.loc[key].equals(df2.loc[key]):
            temp_dict = df1.loc[key].to_dict()
            temp_dict[unique_column] = key
            updated_rows.append(
                temp_dict
            )

    # Reset index to original state
    df1.reset_index(inplace=True)
    df2.reset_index(inplace=True)
    print({
        "new_rows": new_rows,
        "updated_rows": updated_rows,
        "removed_rows": removed_rows
    })
    return {
        "new_rows": new_rows,
        "updated_rows": updated_rows,
        "removed_rows": removed_rows
    }

# Example dataframes to test the function
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

# result = compare_dataframes(df1, df2, 'ID')
# print(result)
