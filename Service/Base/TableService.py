import traceback

from PyQt6.QtWidgets import QTableView, QDialog, QVBoxLayout, QLineEdit, QPushButton, QApplication, QDateTimeEdit
from PyQt6.QtCore import Qt, QModelIndex

from Service.Base.TableDialogService import EditDialog, NonEditDialog


class TableViewService(QTableView):
    def __init__(self, parent=None, is_sales=None):
        super().__init__(parent)
        self.is_sales = is_sales
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)  # Disable direct editing
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)  # Limit selection to single row
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.doubleClicked.connect(self.openEditDialog)
        self.model = None

    def setModel(self, model):
        super().setModel(model)
        self.model = model

    def openEditDialog(self, index, is_insert_auto_dialog=False):
        try:
            source_index = self.model.mapToSource(index)

            row = source_index.row()
            column = source_index.column()
            model = self.model.sourceModel()

            column_data = model.dataframe.iloc[row].to_dict()
            column_info = {col["column_name"]: col for col in
                           model.connector.schema_dictionary[model.connector.database][model.table_name]}
            if not self.is_sales:
                dialog = EditDialog(column_data, column_info, model.referenced_pair)

            else:
                dialog = NonEditDialog(column_data, column_info, model.referenced_pair)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                if is_insert_auto_dialog:
                    self.remove_last_row()
            else:
                new_data = dialog.fields
                mapped_data = {}

                for col, line_edit in new_data.items():
                    value = line_edit.text()
                    col_info = column_info.get(col)
                    if col_info:
                        mapped_data[col] = {
                            'value': value,
                            'data_type': col_info['data_type'],
                            'is_nullable': col_info['is_nullable'],
                            'character_maximum_length': col_info['character_maximum_length'],
                            'pk_name': col_info['pk_name'],
                            'is_auto_increment': col_info['is_auto_increment']
                        }
                new_data = self.model.sourceModel().bridge.schema_handler.map_data_from_line_edit(mapped_data)
                self.model.sourceModel().insert_model_record(new_data, row)
                self.model.sourceModel().commit()
        except:
            traceback.print_exc()

    def get_current_row_data(self):
        try:
            selected_indexes = self.selectionModel().selectedIndexes()
            if not selected_indexes:
                return None  # No row is currently selected

            index = selected_indexes[0]
            source_index = self.model.mapToSource(index)
            row = source_index.row()
            model = self.model.sourceModel()

            row_data = model.dataframe.iloc[row].to_dict()
            return row_data
        except:
            return None

    def remove_row(self):
        try:
            selected_indexes = self.selectionModel().selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0]
                source_index = self.model.mapToSource(index)
                row = source_index.row()
                pk_column = self.model.sourceModel().find_pk_of_table(self.model.sourceModel().table_name,
                                                                      self.model.sourceModel().connector)
                pk_value = self.model.sourceModel().dataframe.iloc[row][pk_column]
                self.model.sourceModel().remove_row(row, 1, QModelIndex())
                self.model.sourceModel().remove_record(pk_value)
                self.model.sourceModel().commit()
                print(f"Record with primary key {pk_value} removed successfully.")
        except:
            traceback.print_exc()

    def insert_row(self):
        try:
            source_model = self.model.sourceModel()
            row_count = source_model.rowCount()  # Get the current number of rows in the DataFrame

            # Insert the new row at the end of the DataFrame
            source_model.insert_row(row_count, 1, QModelIndex())

            # Get the index of the newly inserted row
            last_index = self.model.sourceModel().index(row_count, 0, QModelIndex())

            # Ensure the new row is visible and selected
            self.setCurrentIndex(last_index)
            self.scrollTo(last_index, self.ScrollHint.PositionAtBottom)
        except:
            traceback.print_exc()

    def remove_last_row(self):
        try:
            source_model = self.model.sourceModel()
            row_count = source_model.rowCount()
            if row_count > 0:
                last_row_index = row_count - 1
                pk_column = source_model.find_pk_of_table(source_model.table_name, source_model.connector)
                pk_value = source_model.dataframe.iloc[last_row_index][pk_column]
                source_model.remove_row(last_row_index, 1, QModelIndex())
                source_model.remove_record(pk_value)
        except:
            traceback.print_exc()
