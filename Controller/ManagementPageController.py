# ManagementPageController.py
import importlib
import traceback

from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtWidgets import QMessageBox

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController


class ManagementPageController(BaseController):
    def __init__(self, view, dialog):
        super().__init__()
        self.view = view
        self.dialog = dialog
        self.view.pushButton_insert.clicked.connect(self.process_insert)
        self.view.pushButton_delete.clicked.connect(self.process_delete)

    def process_insert(self):
        source_model = self.view.TableView.model.sourceModel()
        self.view.TableView.insert_row()
        last_row = source_model.rowCount()
        last_index = source_model.index(last_row, 0)
        selection_model = self.view.TableView.selectionModel()
        selection_model.setCurrentIndex(last_index,
                                        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        self.view.TableView.scrollTo(last_index)
        current_index = selection_model.currentIndex()
        self.view.TableView.openEditDialog(current_index, is_insert_auto_dialog=True)

    def process_delete(self):
        selection_model = self.view.TableView.selectionModel()
        selected_rows = selection_model.selectedRows()

        if not selected_rows:
            QMessageBox.information(self.dialog, 'Information', 'No record selected. Please select a record to delete.')
            return

        reply = QMessageBox.question(self.dialog, 'Confirmation', 'Are you sure you want to delete the selected record?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.view.TableView.remove_row()
