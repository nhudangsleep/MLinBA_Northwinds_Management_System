import traceback
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QTableView, QMainWindow, QMenu
from PyQt6.QtCore import Qt, QModelIndex
from functools import partial
from Connector.Connector import Connector
from Model.BaseModel import BaseModel
from View.BaseTableViewEx import BaseTableViewEx
from View.MainWindow import Ui_MainWindow


class MainWindowEx(Ui_MainWindow, BaseTableViewEx):
    def __init__(self):
        super().__init__()
        self.init_connection()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.pushButtonCustomer.clicked.connect(self.process_customer)
        self.pushButtonProduct.clicked.connect(self.process_product)
        self.pushButtonEmployee.clicked.connect(self.process_employee)
        self.pushButtonSales.clicked.connect(self.process_sales)
        self.config_table_menu()

    def init_connection(self):
        self.connector = Connector()
        self.connector.server = "127.0.0.1"
        self.connector.port = 3306
        self.connector.username = "root"
        self.connector.database = "northwind"
        self.connector.password = "Nhudangstudy123."
        self.connector.connect()

    def process_customer(self):
        try:
            self.model = BaseModel(table_name="customer", connector=self.connector)
            self.tableView.setModel(self.model)
        except:
            traceback.print_exc()

    def process_employee(self):
        try:
            self.model = BaseModel(table_name="employee", connector=self.connector)
            self.tableView.setModel(self.model)
        except:
            traceback.print_exc()
        pass

    def process_product(self):
        try:
            self.model = BaseModel(table_name="product", connector=self.connector)
            self.tableView.setModel(self.model)
        except:
            traceback.print_exc()

    def process_sales(self):
        self.model.update()

    def show(self):
        self.MainWindow.show()