import traceback
from copy import deepcopy

from Connector.Bridge import DataBrige
import pandas as pd
from datetime import datetime
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from Model.BaseException import InvalidTableNameError
from Utils.DataframeUtils import compare_dataframes


class BaseModel(QAbstractTableModel):
    def __init__(self, table_name, connector):
        if self.validate_table_name(table_name, connector):
            self.table_name = table_name
            self.connector = connector
            self.data = None
            self.init_bridge()
            super().__init__()
        else: 
            raise InvalidTableNameError(f"Invalid table name: {table_name}")

    @staticmethod
    def validate_table_name(table_name, connector):
        if table_name not in connector.table_names:
            return False
        return True

    @staticmethod
    def find_pk_of_table(table_name, connector):
        if BaseModel.validate_table_name(table_name, connector):
            for column in connector.schema_dictionary[connector.database][table_name]:
                print(column)
                if column["pk_name"] == "PRIMARY":
                    return column["column_name"]

    def init_bridge(self):
        self.bridge = DataBrige(connector=self.connector, table_name=self.table_name)
        self.data = self.bridge.get_all_records()
        self.parent_data = deepcopy(self.data)
        self.auto_increment_column = next(
                (col["column_name"] for col in
                 self.connector.schema_dictionary[self.connector.database][self.table_name] if
                 col["is_auto_increment"]), None)



    def data(self, index, role):

        if not index.isValid():
            return None

        value = str(self.data.iloc[int(index.row()), int(index.column())])

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return value

        if role == Qt.ItemDataRole.BackgroundRole:
            column_name = self.data.columns[index.column()]

            # Check if the column is the auto-increment column
            if column_name == self.auto_increment_column:
                return QtGui.QColor(Qt.GlobalColor.gray)  # Return gray background color for the auto-increment column

    def rowCount(self, index):
        return self.data.shape[0]

    def columnCount(self, index):
        return self.data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self.data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        column_name = self.data.columns[index.column()]
        if column_name == self.auto_increment_column:
            return super().flags(index)
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role):
        try:
            if role == Qt.ItemDataRole.EditRole and index.isValid():
                column_name = self.data.columns[index.column()]
                column_info = next((col for col in self.connector.schema_dictionary[self.connector.database][self.table_name] if col["column_name"] == column_name), None)
                if column_info:
                    data_type = column_info["data_type"]
                    is_nullable = column_info["is_nullable"]
                    if column_info['is_auto_increment'].lower() == "yes":
                        return True
                    max_length = column_info["character_maximum_length"]
                    try:
                        if data_type == "int":
                            value = int(value)
                        elif data_type == "varchar" or data_type == "char" or data_type == "text":
                            value = str(value)
                            if max_length is not None and len(value) > max_length:
                                print("Value exceeds maximum length for column {}.".format(column_name))
                                return False
                        elif data_type == "blob":
                            self.data.drop(column_name, axis=1, inplace=True)
                            self.layoutChanged.emit()
                            return True
                        elif data_type == "datetime":
                            try:
                                value = datetime.strptime(value, "%Y-%m-%d")
                            except ValueError:
                                print("Invalid value for datetime column {}.".format(column_name))
                                return False
                        elif data_type == "decimal":
                            try:
                                value = float(value)
                            except ValueError:
                                print("Invalid value for decimal column {}.".format(column_name))
                                return False
                        elif data_type == "smallint":
                            try:
                                value = int(value)
                            except ValueError:
                                print("Invalid value for smallint column {}.".format(column_name))
                                return False


                    except ValueError:
                        print("Invalid data type for column {}.".format(column_name))
                        return False

                    if not is_nullable and (value is None or value == ""):
                        print("Value cannot be null for column {}.".format(column_name))
                        return False

                    self.data.iloc[index.row(), index.column()] = value
                    self.dataChanged.emit(index, index, [role])
                    return True

                else:
                    print("Column information not found for column {}".format(column_name))
                    return False
            return False
        except:
            traceback.print_exc()

    def insertRow(self, row, rows=1, index=QModelIndex()):
        try:
            self.beginInsertRows(QModelIndex(), row, row + rows - 1)
            new_data = {}
            for column in self.data.columns:
                column_info = [col for col in self.connector.schema_dictionary[self.connector.database][self.table_name] if col["column_name"] == column]
                data_type = column_info[0]["data_type"]
                is_nullable = column_info[0]["is_nullable"]

                new_data[column] = "-"

                if data_type == "int":
                    if column_info[0]['is_auto_increment'].lower() == 'yes':
                        max_value = self.data[column].max() if not self.data.empty else 0
                        new_data[column] = max_value + 1
                    else:
                        new_data[column] = 0
                elif data_type in ["varchar", "char", "text"]:
                    new_data[column] = ""
                elif data_type == "datetime":
                    new_data[column] = datetime.now()
                elif data_type == "decimal":
                    new_data[column] = 0.0
                elif data_type == "smallint":
                    new_data[column] = 0
                else:
                    new_data[column] = ""
            row_list = []
            for idx, new_row in self.data.iterrows():
                row_list.append(new_row)

            new_data_df = pd.DataFrame(new_data, index=[row])
            for idx, new_row in new_data_df.iterrows():
                row_list.append(new_row)
            self.data = pd.DataFrame(row_list)
            self.endInsertRows()
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def removeRow(self, row, rows=1, index=QModelIndex()):
        try:
            self.beginRemoveRows(QModelIndex(), row, row + rows - 1)
            self.data = self.data.drop(self.data.index[row:row + rows])
            self.endRemoveRows()
            return True
        except Exception as e:
            print("Error removing row:", e)
            return False

    def update(self):
        try:
            # compare self.parent_data and self.data
            # find all mismatching records
            # if self.data is missing some record in self.parent_data -> means that we need to archive these records
            # if same pk but different value -> means that  we need to update these records
            # if self.data have new records (new_pk)
            archive_data = []
            update_data = []
            new_data = []
            pk_column = BaseModel.find_pk_of_table(table_name=self.table_name, connector=self.connector)
            a= compare_dataframes(self.data, self.parent_data, pk_column)
            print(len(a['matching_rows']))
            print(len(a['mismatching_rows']))
            print(len(a['new_rows']))
            print(len(a['removed_rows']))
        except:
            traceback.print_exc()
