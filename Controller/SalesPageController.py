# ManagementPageController.py
import traceback

from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController
from View.OrderDetailWindow import Ui_WizardPage


class SalesPageController(BaseController):
    def __init__(self, view, parent_widget):
        super().__init__()
        self.view = view
        self.parent_widget = parent_widget
        # Connect actions
        self.view.pushButton_view_items.clicked.connect(self.process_view_items)
        self.view.pushButton_view_items.setVisible(False)

    def connect_table(self, table_name):
        super().connect_table(table_name)
        if table_name == "Customer":
            self.view.pushButton_view_items.setVisible(False)
        else:
            self.view.pushButton_view_items.setVisible(True)

    def process_view_items(self):
        selected_indexes = self.view.TableView.selectionModel().selectedIndexes()
        self.show_order_detail_window()

    def show_order_detail_window(self):
        try:
            self.order_detail_window = QDialog()
            data = self.view.TableView.get_current_row_data()
            if data:
                self.ui = Ui_WizardPage(data)
                self.ui.setupUi(self.order_detail_window)
                self.order_detail_window.show()
            else:
                QMessageBox.warning(self.parent_widget, "No Selection", "Please select a row or column to view details.")

        except:
            traceback.print_exc()

