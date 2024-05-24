from copy import deepcopy
from Utils.DataframeUtils import compare_dataframes

class CRUDAPI:
    def __init__(self, connector, table_name, pk_column, dataframe, parent_data):
        self.connection = connector
        self.table_name = table_name
        self.pk_column = pk_column
        self.dataframe = dataframe
        self.parent_data = parent_data

    def commit_changes(self):
        comparison = compare_dataframes(self.dataframe, self.parent_data, self.pk_column)
        self.update(comparison['updated_rows'])
        self.create(comparison['new_rows'])
        self.destroy(comparison['removed_rows'])
        return deepcopy(self.dataframe)

    def update(self, mismatching_rows):
        """
        Handle updated rows
        """
        cursor = self.connection._conn.cursor()
        for row in mismatching_rows:
            set_clause = ', '.join([f"{col} = %s" for col in row.keys() if col != self.pk_column])
            update_query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} = %s"
            values = tuple(row[col] for col in row.keys() if col != self.pk_column) + (row[self.pk_column],)
            try:
                print(f"Executing UPDATE: {update_query} with values {values}")
                cursor.execute(update_query, values)
            except Exception as e:
                print(f"Failed to update row {row[self.pk_column]}: {e}")
        self.connection._conn.commit()
        cursor.close()

    def create(self, new_rows):
        """
        Handle new rows
        """
        cursor = self.connection._conn.cursor()
        for row in new_rows:
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['%s'] * len(row))
            insert_query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            values = tuple(row.values())
            try:
                print(f"Executing INSERT: {insert_query} with values {values}")
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"Failed to insert row {row[self.pk_column]}: {e}")
        self.connection._conn.commit()
        cursor.close()

    def destroy(self, removed_rows):
        """
        Handle removed rows
        """
        cursor = self.connection._conn.cursor()
        for row in removed_rows:
            delete_query = f"DELETE FROM {self.table_name} WHERE {self.pk_column} = %s"
            try:
                print(f"Executing DELETE: {delete_query} with value {row[self.pk_column]}")
                cursor.execute(delete_query, (row[self.pk_column],))
            except Exception as e:
                print(f"Failed to delete row {row[self.pk_column]}: {e}")
        self.connection._conn.commit()
        cursor.close()