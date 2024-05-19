import datetime
import traceback


class SchemaHandler:
    def __init__(self, schema):
        self.schema = schema
        self.type_mapping = {
            'int': 'Int64',
            'smallint': 'Int16',
            'tinyint': 'Int8',
            'bigint': 'Int64',
            'varchar': 'string',  # Using Pandas' string type which is nullable
            'text': 'string',
            'char': 'string',
            'nchar': 'string',
            'nvarchar': 'string',
            'datetime': 'datetime64[ns]',  # Using NumPy's datetime64 type
            'date': 'datetime64[ns]',
            'time': 'timedelta64[ns]',  # Using NumPy's timedelta64 type for time
            'timestamp': 'datetime64[ns]',
            'decimal': 'Float64',  # Using Pandas' nullable float type
            'numeric': 'Float64',
            'float': 'Float64',
            'real': 'Float64',
            'binary': 'string',  # bytes type remains unchanged
            'varbinary': 'string',
            'blob': 'string',
            'bit': 'boolean',  # Using Pandas' nullable boolean type
            'boolean': 'boolean'
        }
        # self.type_mapping = {
        #     'int': int,
        #     'smallint': int,
        #     'tinyint': int,
        #     'bigint': int,
        #     'varchar': str,
        #     'text': str,
        #     'char': str,
        #     'nchar': str,
        #     'nvarchar': str,
        #     'datetime': datetime.datetime,
        #     'date': datetime.date,
        #     'time': datetime.time,
        #     'timestamp': datetime.datetime,
        #     'decimal': float,
        #     'numeric': float,
        #     'float': float,
        #     'real': float,
        #     'binary': bytes,
        #     'varbinary': bytes,
        #     'blob': bytes,
        #     'bit': bool,
        #     'boolean': bool
        # }

    def get_python_data_type(self, field):
        sql_type = self.schema.get(field, None)
        return self.type_mapping.get(sql_type, None)

    @staticmethod
    def schemas_prettier(data):
        prettified_schema = {}
        for row in data:
            schema_name, table_name, column_name, data_type, is_nullable, character_maximum_length, pk_name, is_auto_increment = row
            if schema_name not in prettified_schema:
                prettified_schema[schema_name] = {}
            if table_name not in prettified_schema[schema_name]:
                prettified_schema[schema_name][table_name] = []

            try:
                data_type = data_type.decode('utf-8')
            except:
                pass

            column_info = {
                "column_name": column_name,
                "data_type": data_type,
                "is_nullable": is_nullable,
                "character_maximum_length": character_maximum_length,
                "pk_name": pk_name,
                "is_auto_increment": is_auto_increment
            }
            prettified_schema[schema_name][table_name].append(column_info)
        return prettified_schema
