import pandas as pd


class DataBrige:
    def __init__(self, connector, table_name): 
        self.connector = connector
        self.table_name = table_name

    def get_all_referenced_table_and_value(self):
        pass

    def get_all_records(self):
        column_names = [column['column_name'] for column in self.connector.schema_dictionary[self.connector.database][self.table_name]]
        data_sql = f"""
                   SELECT * FROM {self.table_name};
                   """

        cursor = self.connector.conn.cursor()
        cursor.execute(data_sql)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=column_names)
        return df

    def archive_records(self, list_pk):
        pass 

    def update_records(self, list_records):
        pass

    def insert_records(self, list_records): 
        pass 
