import sys
import traceback
from PyQt6 import QtCore, QtGui, QtWidgets


class DropdownButton(QtWidgets.QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.menu = QtWidgets.QMenu(parent)
        self.setMenu(self.menu)

    def setup_actions(self, actions):
        for action_title, action_handler in actions.items():
            self.menu.addAction(action_title, action_handler)
