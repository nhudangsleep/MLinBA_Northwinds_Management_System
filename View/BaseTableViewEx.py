from PyQt6 import QtCore, QtGui, QtWidgets
from functools import partial
import traceback
from PyQt6.QtWidgets import QTableView, QMainWindow, QMenu
from PyQt6.QtCore import Qt, QModelIndex
from functools import partial
from Connector.Connector import Connector
from Utils.InsertBehavior import InsertBehavior


class BaseTableViewEx:
    def __init__(self):
        self.tableView = QtWidgets.QTableView()

    def config_table_menu(self):
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.custom_context_menu_request)

    def custom_context_menu_request(self, pos):
        try:
            index = self.tableView.indexAt(pos)
            menu = QMenu()

            if index.isValid():
                insertLast = menu.addAction("Insert")
                removeSelected = menu.addAction("Remove Selected row")

                insertLast.triggered.connect(partial(self.process_insert, InsertBehavior.INSERT_LAST))
                removeSelected.triggered.connect(self.process_delete)

                menu.addAction(insertLast)
                menu.addSeparator()
                menu.addAction(removeSelected)

                menu.exec(self.tableView.viewport().mapToGlobal(pos))
                menu.close()
            else:
                insertNew = menu.addAction("Insert New Record")
                insertNew.triggered.connect(partial(self.process_insert, InsertBehavior.INSERT_LAST))
                menu.exec(self.tableView.viewport().mapToGlobal(pos))
                menu.close()

        except Exception as e:
            traceback.print_exc()

    def process_insert(self, behavior=InsertBehavior.INSERT_FIRST):
        indexes = self.tableView.selectionModel().selectedIndexes()
        if behavior == InsertBehavior.INSERT_FIRST:
            row = 0
        elif behavior == InsertBehavior.INSERT_LAST:
            row = self.tableView.model().rowCount(QModelIndex()) + 1
        else:
            if indexes:
                index = indexes[0]
                row = index.row()
                if behavior == InsertBehavior.INSERT_ABOVE:
                    row = max(row, 0)
                else:
                    size = self.tableView.model().rowCount(QModelIndex())
                    row = min(row + 1, size)
        self.tableView.model().insertRow(row, 1, QModelIndex())
        last_index = self.tableView.model().index(row, 0, QModelIndex())
        self.tableView.setCurrentIndex(last_index)
        self.tableView.scrollTo(last_index, QTableView.ScrollHint.PositionAtBottom)

    def process_delete(self):
        try:
            indexes = self.tableView.selectionModel().selectedIndexes()
            if indexes:
                index = indexes[0]
                row = index.row()
                self.tableView.model().removeRow(row, 1, QModelIndex())
        except Exception as e:
            print(e)