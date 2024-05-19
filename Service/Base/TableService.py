import traceback

from PyQt6.QtWidgets import QTableView, QDialog, QVBoxLayout, QLineEdit, QPushButton, QApplication, QDateTimeEdit
from PyQt6.QtCore import Qt

from Service.Base.TableDialogService import EditDialog


class TableViewService(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)  # Disable direct editing
        self.doubleClicked.connect(self.openEditDialog)
        self.model = None

    def setModel(self, model):
        super().setModel(model)
        self.model = model

    def openEditDialog(self, index):
        try:
            if not index.isValid():
                return

            row = index.row()
            column = index.column()
            model = self.model.sourceModel()
            column_data = model.dataframe.iloc[row].to_dict()
            column_info = {col["column_name"]: col for col in
                           model.connector.schema_dictionary[model.connector.database][model.table_name]}
            dialog = EditDialog(column_data, column_info, model.referenced_pair)
            if dialog.exec():
                new_data = dialog.fields
                self.setData(self.index(row, self.model.data.columns.get_loc(col)), value, Qt.ItemDataRole.EditRole)

        except:
            traceback.print_exc()
