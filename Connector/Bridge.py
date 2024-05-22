import pandas as pd
from Utils.SchemaHandler import SchemaHandler
from copy import copy
from pandas.api.types import is_datetime64_any_dtype as is_datetime



class DataBridge:
    """
    referenced_dict: {
        "Column name": [
            "referenced column id":
            "value":
        ]
    }
    """
    def __init__(self, connector, table_name):
        self.connector = connector
        self.table_name = table_name
        self.column_dict = None
        self.referenced_dict = None
        self.schema_handler = None
        self.get_table_structure()

    def get_table_structure(self, table_name=None):
        if not table_name:
            table_name = self.table_name
        column_names = ['column_name', 'data_type']
        sql_script = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}';
        """
        cursor = self.connector._conn.cursor()
        cursor.execute(sql_script)
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=column_names)
        table_dict = {}
        for index, row in df.iterrows():
            table_dict[str(row['column_name'])] = str(row['data_type'])
        self.schema_handler = SchemaHandler(table_dict)

    def get_all_referenced_table_and_value(self):
        column_names = ['table_name', 'column_name', 'referenced_table', 'referenced_column']
        sql_script = f"""
        
        SELECT 
                TABLE_NAME AS table_name,
                COLUMN_NAME AS column_name,
                REFERENCED_TABLE_NAME AS referenced_table,
                REFERENCED_COLUMN_NAME AS referenced_column
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE 
            TABLE_NAME = '{self.table_name}'
            AND REFERENCED_TABLE_SCHEMA = '{self.connector.database}'
            AND REFERENCED_TABLE_NAME IS NOT NULL;
        """

        cursor = self.connector._conn.cursor()
        cursor.execute(sql_script)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=column_names)
        return df

    def get_all_records(self, table_name=None):
        if not table_name:
            table_name = copy(self.table_name)
        self.get_table_structure(table_name)
        column_names = [column['column_name'] for column in self.connector.schema_dictionary[self.connector.database][table_name]]
        data_sql = f"""
                   SELECT * FROM {table_name};
                   """

        cursor = self.connector._conn.cursor()
        cursor.execute(data_sql)
        raw_data = cursor.fetchall()
        data = []
        for row in raw_data:
            converted_row = []
            for item in row:
                if isinstance(item, bytearray):
                    converted_row.append(item.decode('utf-8'))
                else:
                    converted_row.append(item)
            data.append(converted_row)

        df = pd.DataFrame(data, columns=column_names)
        df = df.map(DataBridge.bytes_to_str)
        for column in df.columns:
            python_data_type = self.schema_handler.get_python_data_type(column)
            if python_data_type:
                df[column] = df[column].astype(python_data_type)

        date_columns = [column for column in df.columns if is_datetime(df[column])]

        for column in date_columns:
            df[column] = pd.to_datetime(df[column]).dt.strftime('%d-%b-%Y')
        return df

    def archive_records(self, list_pk):
        pass

    def update_records(self, list_records):
        pass

    def insert_records(self, list_records):
        pass

    @staticmethod
    def bytes_to_str(x):
        if isinstance(x, bytes):
            return x.decode('utf-8')
        return x
