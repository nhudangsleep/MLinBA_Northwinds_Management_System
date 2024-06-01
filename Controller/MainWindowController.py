import traceback

from Controller.Base.BaseController import BaseController
from View.MainWindow import Ui_MainWindow


class MainWindowController(Ui_MainWindow, BaseController):
    def __init__(self):
        super().__init__()
        BaseController.__init__(self)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.setup_navigation_bar()
        self.process_dashboard_overview()

    def setup_navigation_bar(self):
        self.sales_dropdown_buttons = {
            "Customers": self.process_customers,
            "Orders": self.process_orders
        }
        self.pushButton_sales.setup_actions(self.sales_dropdown_buttons)

        self.operation_dropdown_buttons = {
            "Employees": self.process_employees,
            "Suppliers": self.process_suppliers,
            "Shippers": self.process_shippers
        }
        self.pushButton_operation.setup_actions(self.operation_dropdown_buttons)

        self.catalog_dropdown_buttons = {
            "Products": self.process_products,
            "Categories": self.process_categories
        }
        self.pushButton_catalog.setup_actions(self.catalog_dropdown_buttons)

        self.predictive_model_dropdown_buttons = {
            "Clustering": self.process_clustering_model
        }
        self.pushButton_predictive_model.setup_actions(self.predictive_model_dropdown_buttons)

        self.dashboard_dropdown_buttons = {
            "Overview": self.process_dashboard_overview, 
            "Detail": self.process_detail
        }
        self.pushButton_dashboard.setup_actions(self.dashboard_dropdown_buttons)

    def process_customers(self):
        self.stackedWidget.setCurrentIndex(3)
        self.sales_page_controller.connect_table("Customer")

    def process_orders(self):
        self.stackedWidget.setCurrentIndex(3)
        self.sales_page_controller.connect_table("SalesOrder")

    def process_employees(self):
        self.stackedWidget.setCurrentIndex(2)
        self.management_page_controller.connect_table("Employee")

    def process_suppliers(self):
        self.stackedWidget.setCurrentIndex(2)
        self.management_page_controller.connect_table("Supplier")

    def process_shippers(self):
        self.stackedWidget.setCurrentIndex(2)
        self.management_page_controller.connect_table("Shipper")

    def process_products(self):
        self.stackedWidget.setCurrentIndex(2)
        self.management_page_controller.connect_table("Product")

    def process_categories(self):
        self.stackedWidget.setCurrentIndex(2)
        self.management_page_controller.connect_table("Category")

    def process_clustering_model(self):
        self.stackedWidget.setCurrentIndex(4)

    def process_dashboard_overview(self):
        self.stackedWidget.setCurrentIndex(0)

    def process_detail(self):
        self.stackedWidget.setCurrentIndex(1)

    def show(self):
        self.MainWindow.show()
