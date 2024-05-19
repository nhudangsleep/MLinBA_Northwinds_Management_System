import importlib
import traceback
from copy import deepcopy
import pandas as pd
from Connector.Bridge import DataBridge
from datetime import datetime
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QAbstractTableModel
from Model.Base.BaseException import InvalidTableNameError
from Utils.DataframeUtils import compare_dataframes


class BaseModel(QAbstractTableModel):
    def __init__(self, table_name, connector):
        if self.validate_table_name(table_name, connector):
            self.table_name = table_name
            self.connector = connector
            self.dataframe = None
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
                if column["pk_name"] == "PRIMARY":
                    return column["column_name"]

    def init_bridge(self):
        self.bridge = DataBridge(connector=self.connector, table_name=self.table_name)
        self.dataframe = self.bridge.get_all_records()

        self.parent_data = deepcopy(self.dataframe)
        self.auto_increment_column = next(
            (col["column_name"] for col in
             self.connector.schema_dictionary[self.connector.database][self.table_name] if
             col["is_auto_increment"]), None)

        referenced_table = self.bridge.get_all_referenced_table_and_value()
        self.referenced_pair = {}

        for index, row in referenced_table.iterrows():
            mapping = {
                "employeeterritory": "EmployeeTerritory",
                "orderdetail": "OrderDetail",
                "salesorder": "SalesOrder"
            }
            if row['referenced_table'] in mapping.keys():
                referenced_table_name = mapping[row['referenced_table']]
            else:
                referenced_table_name = row['referenced_table'].title()

            module_name = f"Model.{referenced_table_name}Model"
            model_class = getattr(importlib.import_module(module_name), f"{referenced_table_name}Model")

            self.referenced_pair[row['column_name']] = {
                'referenced_column': row['referenced_column'],
                'model': model_class(self.connector)
            }

    def data(self, index, role):
        try:
            if not index.isValid():
                return None
            if pd.isna(self.dataframe.iloc[int(index.row()), int(index.column())]):
                value = "-"
            elif type(self.dataframe.iloc[int(index.row()), int(index.column())]) is bytes:
                value = self.dataframe.iloc[int(index.row()), int(index.column())].decode('utf-8')
            elif isinstance(self.dataframe.iloc[int(index.row()), int(index.column())], bytearray):
                value = self.dataframe.iloc[int(index.row()), int(index.column())].decode('utf-8')
            else:
                value = str(self.dataframe.iloc[int(index.row()), int(index.column())])
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return value

            if role == Qt.ItemDataRole.BackgroundRole:
                column_name = self.dataframe.columns[index.column()]

                if column_name == self.auto_increment_column:
                    return QtGui.QColor(Qt.GlobalColor.gray)  # Return gray background color for the auto-increment column
        except:
            traceback.print_exc()

    def rowCount(self, index):
        return self.dataframe.shape[0]

    def columnCount(self, index):
        return self.dataframe.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self.dataframe.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)

    def flags(self, index):
        default_flags = super().flags(index)
        column_name = self.dataframe.columns[index.column()]
        if column_name.lower() in ['yesno', 'truefalse']:
            return default_flags | Qt.ItemFlag.ItemIsUserCheckable
        return default_flags & ~Qt.ItemFlag.ItemIsEditable  # Disable editing

    def setData(self, index, value, role):
        try:
            if role == Qt.ItemDataRole.EditRole and index.isValid():
                column_name = self.dataframe.columns[index.column()]
                column_info = next((col for col in self.connector.schema_dictionary[self.connector.database][self.table_name] if col["column_name"] == column_name), None)
                if column_info:
                    data_type = column_info["data_type"]
                    is_nullable = column_info["is_nullable"]
                    if column_info['is_auto_increment'].lower() == "yes":
                        return True
                    max_length = column_info["character_maximum_length"]
                    try:
                        if value is None:
                            value = "-"
                        else:
                            if data_type == "int":
                                value = int(value)
                            elif data_type == "varchar" or data_type == "char" or data_type == "text":
                                value = str(value)
                                if max_length is not None and len(value) > max_length:
                                    print("Value exceeds maximum length for column {}.".format(column_name))
                                    return False
                            elif data_type == "blob":
                                self.dataframe.drop(column_name, axis=1, inplace=True)
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

                    self.dataframe.iloc[index.row(), index.column()] = value
                    return True

                else:
                    print("Column information not found for column {}".format(column_name))
                    return False
            return False
        except:
            traceback.print_exc()

    def update(self):
        try:
            # compare self.parent_data and self.dataframe
            # find all mismatching records
            # if self.dataframe is missing some record in self.parent_data -> means that we need to archive these records
            # if same pk but different value -> means that  we need to update these records
            # if self.dataframe have new records (new_pk)
            archive_data = []
            update_data = []
            new_data = []
            pk_column = BaseModel.find_pk_of_table(table_name=self.table_name, connector=self.connector)
            a = compare_dataframes(self.dataframe, self.parent_data, pk_column)
            print(len(a['matching_rows']))
            print(len(a['mismatching_rows']))
            print(len(a['new_rows']))
            print(len(a['removed_rows']))
        except:
            traceback.print_exc()

    def create_new_record(self, **data):
        pass

    def update_record(self, pk):
        pass

    def remove_record(self, pk):
        pass

