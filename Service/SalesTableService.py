import traceback

from PyQt6.QtWidgets import QMenu

from Service.Base.TableService import TableViewService
from PyQt6.QtCore import Qt, QModelIndex


class SalesTableService(TableViewService):
    """
    This table service will provide 2 actions which are:
    - alter header info
    - alter products in one order
    """
    def __init__(self, **ui_dictionary):
        super().__init__()
        self.config_table_menu()

    def config_table_menu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_context_menu)

    def custom_context_menu(self, pos):
        try:
            index = self.indexAt(pos)
            menu = QMenu(self)

            if index.isValid():
                alter_order_header = self.addAction("Edit Order Header")
                alter_order_products = self.addAction("Edit Order Product")

                alter_order_header.triggered.connect(self.process_alter_order_header)
                alter_order_products.triggered.connect(self.process_alter_order_products)

                menu.addAction(alter_order_header)
                menu.addAction(alter_order_products)

                menu.exec(self.viewport().mapToGlobal(pos))
                menu.close()
            else:
                print("index is not valid")
        except:
            traceback.print_exc()

    def process_alter_order_header(self):
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
        # get value in the curent table
        # open dialog

    def process_alter_order_products(self):
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
        # Open Dialog

        pass

    def insert_row(self):
        # insert 1 row into the table view
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            self.model().insertRow(row, 1, QModelIndex())
            last_index = self.model().index(row, 0, QModelIndex())
            self.setCurrentIndex(last_index)
            self.scrollTo(last_index, self.ScrollHint.PositionAtBottom)

    def remove_row(self):
        # Remove 1 row from the table view
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            self.model().removeRow(row, 1, QModelIndex())
