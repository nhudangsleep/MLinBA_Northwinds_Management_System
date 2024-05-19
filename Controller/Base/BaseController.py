import importlib
import traceback

from PyQt6 import QtCore
from PyQt6.QtCore import QObject
from dotenv import load_dotenv
import os
from Connector.DatabaseConnection import DatabaseConnection
from Service.Base.FilterProxyModel import FilterProxyModel

load_dotenv()


class BaseController:

    def __init__(self):
        self.init_connection()
        self.view = None

    def init_connection(self):
        server = os.getenv('DB_SERVER')
        port = int(os.getenv('DB_PORT'))
        username = os.getenv('DB_USERNAME')
        database = os.getenv('DB_DATABASE')
        password = os.getenv('DB_PASSWORD')

        self.connector = DatabaseConnection(server=server, port=port, username=username, database=database, password=password)
        self.connector.get_connection()

    def connect_table(self, table_name=None, parent=None):
        try:
            self.view.comboBox_filter.clear()
            if table_name:
                module_name = f"Model.{table_name}Model"
                try:
                    model_class = getattr(importlib.import_module(module_name), f"{table_name}Model")

                    self.view.proxy_model = FilterProxyModel(parent)

                    self.view.model = model_class(self.connector)
                    self.view.proxy_model.setSourceModel(self.view.model)
                    self.view.TableView.setModel(self.view.proxy_model)

                    for column in self.view.model.dataframe.columns:
                        self.view.comboBox_filter.addItem(column)

                    self.view.lineEdit_filter.textChanged.connect(self.update_filter)
                    self.view.comboBox_filter.currentIndexChanged.connect(self.update_filter_column)
                except ImportError as e:
                    print(f"Failed to import {module_name}: {e}")
                except AttributeError as e:
                    print(f"Failed to find the model class in {module_name}: {e}")
            else:
                print("No table name provided")
        except:
            traceback.print_exc()

    def update_filter(self, text):
        self.view.proxy_model.setFilterRegularExpression(QtCore.QRegularExpression(text, QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption))

    def update_filter_column(self, index):
        try:
            self.view.proxy_model.setFilterColumn(index)
        except:
            pass