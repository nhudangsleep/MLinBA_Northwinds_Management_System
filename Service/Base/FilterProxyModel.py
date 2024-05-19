import traceback
from PyQt6.QtCore import QSortFilterProxyModel, Qt


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_column = -1

    def setFilterColumn(self, column):
        self.filter_column = column

    def filterAcceptsRow(self, source_row, source_parent):
        try:
            if self.filter_column < 0:
                return super().filterAcceptsRow(source_row, source_parent)

            index = self.sourceModel().index(source_row, self.filter_column, source_parent)
            data = self.sourceModel().data(index, Qt.ItemDataRole.DisplayRole)
            reg_exp = self.filterRegularExpression()

            if data is None:
                return False

            return reg_exp.match(data).hasMatch()
        except:
            traceback.print_exc()
            return False
