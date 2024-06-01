from copy import deepcopy

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QAbstractTableModel, QVariant
import pandas as pd


class BaseDataframeTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super().__init__()
        self.dataframe = dataframe
        self.temp = dataframe

    def data(self, index, role):
        if not index.isValid():
            return None

        value = self.dataframe.iloc[index.row(), index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            return str(value)

        if role == Qt.ItemDataRole.BackgroundRole:
            if index.column() == 1 and value == "":
                return QtGui.QColor(Qt.GlobalColor.yellow)

        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 2 and pd.to_numeric(value, errors='coerce') < 100:
                return QtGui.QColor(Qt.GlobalColor.red)

        return None

    def rowCount(self, index):
        return len(self.dataframe)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.dataframe.columns[section]  # Show column names
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return QVariant()
    def columnCount(self, index):
        return len(self.dataframe.columns)

    def reset_dataframe(self):
        self.dataframe = deepcopy(self.temp)
