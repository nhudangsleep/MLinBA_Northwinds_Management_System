import mysql.connector
import traceback
import pandas as pd
from Utils.SchemaHandler import SchemaHandler
import sqlalchemy


class Connector:
    def __init__(self, server=None, port=None, username=None, database=None, password=None):
        self.server = server
        self.port = port
        self.username = username
        self.database = database
        self.password = password
        self.conn = None
        self.schema_dictionary = None
        self.table_names = []

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.server,
                port=self.port,
                user=self.username,
                database=self.database,
                password=self.password,
                auth_plugin='mysql_native_password')

            self.get_all_schemas()
            return self.conn
        except:
            self.conn = None
            traceback.print_exc()
        return None

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()

    def get_all_schemas(self):
        try:
            sql = f"""SELECT 
                            c.TABLE_NAME AS table_name,
                            c.COLUMN_NAME AS column_name,
                            c.DATA_TYPE AS data_type,
                            c.IS_NULLABLE AS is_nullable,
                            c.CHARACTER_MAXIMUM_LENGTH AS character_maximum_length,
                            kcu.CONSTRAINT_NAME AS pk_name,
                            CASE 
                                WHEN extra = 'auto_increment' THEN 'YES'
                                ELSE 'NO'
                            END AS is_auto_increment
                        FROM 
                            INFORMATION_SCHEMA.COLUMNS c
                        LEFT JOIN 
                            INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu ON c.TABLE_SCHEMA = kcu.TABLE_SCHEMA 
                                                                        AND c.TABLE_NAME = kcu.TABLE_NAME 
                                                                        AND c.COLUMN_NAME = kcu.COLUMN_NAME 
                                                                        AND c.TABLE_SCHEMA = '{self.database}'
                                                                        AND kcu.CONSTRAINT_NAME = 'PRIMARY'
                        WHERE 
                            c.TABLE_SCHEMA = '{self.database}'
                        ORDER BY 
                            c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION;
                    """
            cursor = self.conn.cursor()
            cursor.execute(sql)
            lst = cursor.fetchall()
            lst_schemas = SchemaHandler.schemas_prettier(lst)
            self.schema_dictionary = lst_schemas
            self.table_names = list(lst_schemas[self.database].keys())
            return self.schema_dictionary

        except Exception as e:
            traceback.print_exc()




