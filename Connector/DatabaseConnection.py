import mysql.connector
import traceback
import pandas as pd
from Utils.SchemaHandler import SchemaHandler
import sqlalchemy


class DatabaseConnection:
    _instance = None
    _conn = None
    schema_dictionary = None  # Class level attribute to hold schemas

    def __new__(cls, server, port, username, database, password):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls.server = server
            cls.port = port
            cls.username = username
            cls.database = database
            cls.password = password
            try:
                cls._conn = mysql.connector.connect(
                    host=server,
                    port=port,
                    user=username,
                    database=database,
                    password=password,
                    auth_plugin='mysql_native_password'
                )
                cls.update_schemas()  # Initialize/update schemas upon successful connection
            except Exception as e:
                cls._conn = None
                print(f"Connection failed: {e}")
        return cls._instance

    @classmethod
    def get_connection(cls):
        return cls._conn

    @classmethod
    def update_schemas(cls):
        if cls._conn is not None:
            try:
                sql = f"""SELECT 
                            c.TABLE_SCHEMA AS schema_name,
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
                                                                        AND c.TABLE_SCHEMA = '{cls.database}'
                                                                        AND kcu.CONSTRAINT_NAME = 'PRIMARY'
                        WHERE 
                            c.TABLE_SCHEMA = '{cls.database}'
                        ORDER BY 
                            c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION;
                        """
                cursor = cls._conn.cursor()
                cursor.execute(sql)
                lst = cursor.fetchall()
                lst_schemas = SchemaHandler.schemas_prettier(lst)
                cls.table_names = list(lst_schemas[cls.database].keys())

                cls.schema_dictionary = lst_schemas
                print(cls.schema_dictionary)
            except Exception as e:
                print(f"Failed to fetch schemas: {e}")

    @classmethod
    def close_connection(cls):
        if cls._conn is not None:
            cls._conn.close()
            cls._conn = None
            cls._instance = None  # Optionally reset the instance

    @classmethod
    def is_connected(cls):
        if cls._conn is not None:
            return cls._conn.is_connected()
        return False
