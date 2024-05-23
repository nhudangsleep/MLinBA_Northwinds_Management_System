import traceback
from PyQt6.QtCore import Qt, QAbstractTableModel, QVariant
import pandas as pd


class KmeansClusterModel(QAbstractTableModel):
    def __init__(self, dataframe):
        self.dataframe = dataframe
        super().__init__()

    def data(self, index, role):
        try:
            if not index.isValid():
                return None
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                value = self.dataframe.iloc[index.row(), index.column()]
                if pd.isna(value):
                    return "-"
                elif isinstance(value, bytes):
                    return value.decode('utf-8')
                elif isinstance(value, bytearray):
                    return value.decode('utf-8')
                else:
                    return str(value)

            if role == Qt.ItemDataRole.BackgroundRole:
                column_name = self.dataframe.columns[index.column()]
                # Custom background color logic (if any)
                # For example, different background for different clusters
                # You can implement logic here based on column_name or other conditions
                return None  # Return a QColor object if needed
        except Exception as e:
            traceback.print_exc()
        return None

    def rowCount(self, index=None):
        return self.dataframe.shape[0]

    def columnCount(self, index=None):
        return self.dataframe.shape[1]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.dataframe.columns[section]  # Show column names
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        default_flags = super().flags(index)
        column_name = self.dataframe.columns[index.column()]
        if column_name.lower() in ['yesno', 'truefalse']:
            return default_flags | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable
        return default_flags

    def setData(self, index, value, role):
        try:
            if role == Qt.ItemDataRole.EditRole and index.isValid():
                self.dataframe.iloc[index.row(), index.column()] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                return True
            else:
                return False
        except Exception as e:
            traceback.print_exc()
        return False
