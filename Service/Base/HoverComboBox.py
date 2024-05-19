from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox
)


class HoverComboBox(QComboBox):
    def __init__(self, tooltips, parent=None):
        super().__init__(parent)
        self.tooltips = tooltips

    def showPopup(self):
        for i in range(self.count()):
            self.setItemData(i, self.tooltips[i], role=Qt.ItemDataRole.ToolTipRole)
        super().showPopup()
