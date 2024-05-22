import importlib
import traceback

from PyQt6 import QtCore
from PyQt6.QtCore import QObject, QThread
from dotenv import load_dotenv
import os
from Connector.DatabaseConnection import DatabaseConnection
from Controller.Worker.DataLoadWorker import DataLoadWorker
from Model.Base.FilterProxyModel import FilterProxyModel

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

    def connect_table(self, table_name=None, parent=None, additional_data=None):
        try:
            if table_name:
                self.view.proxy_model = FilterProxyModel(parent)
                self.additional_data = additional_data
                self.worker = DataLoadWorker(self.connector, table_name, additional_data)
                self.worker_thread = QThread()
                self.worker.moveToThread(self.worker_thread)
                self.worker.data_loaded.connect(self.on_data_loaded)
                self.worker.error_occurred.connect(self.on_error_occurred)
                self.worker_thread.started.connect(self.worker.load_data)
                self.worker_thread.start()

            else:
                print("No table name provided")
        except:
            traceback.print_exc()

    def update_filter(self, text):
        self.view.proxy_model.setFilterRegularExpression(QtCore.QRegularExpression(text, QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption))

    def update_filter_column(self, index):
        self.view.proxy_model.setFilterColumn(index)

    def on_data_loaded(self, model):
        self.view.model = model
        self.view.proxy_model.setSourceModel(self.view.model)
        self.view.TableView.setModel(self.view.proxy_model)
        try:
            self.view.comboBox_filter.clear()
            have_combobox = True
        except:
            have_combobox = False

        if have_combobox:
            for column in self.view.model.dataframe.columns:
                self.view.comboBox_filter.addItem(column)
            self.view.comboBox_filter.currentIndexChanged.connect(self.update_filter_column)
            self.view.lineEdit_filter.textChanged.connect(self.update_filter)

        self.worker_thread.quit()
        self.worker_thread.wait()

        try:
            self.calculate_total()
        except:
            pass

    def on_error_occurred(self, error_message):
        print(f"Error loading data: {error_message}")
        self.worker_thread.quit()
        self.worker_thread.wait()

    def calculate_total(self):
        dataframe = self.view.TableView.model.sourceModel().dataframe
        dataframe['Total'] = (dataframe['unitPrice'] * dataframe['quantity']) * (1 - dataframe['discount'])
        total_sum = round(dataframe['Total'].sum(), 2) + self.additional_data['freight']

        self.view.lineEdit_total.setText(str(total_sum))
