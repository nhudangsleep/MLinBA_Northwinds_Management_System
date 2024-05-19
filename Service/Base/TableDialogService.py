from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLineEdit,
    QPushButton, QDateTimeEdit, QLabel, QFrame, QDateEdit, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox, QCompleter
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from Service.Base.HoverComboBox import HoverComboBox
from PyQt6.QtCore import QDateTime, QDate
from datetime import datetime


class EditDialog(QDialog):
    def __init__(self, column_data, column_info, referenced_pair, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Record")
        self.referenced_pair = referenced_pair
        self.column_data = column_data
        self.column_info = column_info
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.form_layout = QGridLayout()
        self.fields = {}

        col = 0
        row = 0
        for col_name, col_value in self.column_data.items():
            if col_name not in self.column_info:
                continue

            col_type = self.column_info[col_name]["data_type"]
            is_primary = self.column_info[col_name].get("pk_name") == "PRIMARY"

            if col_name in self.referenced_pair.keys():
                referenced_model = self.referenced_pair[col_name]['model']
                referenced_column = self.referenced_pair[col_name]['referenced_column']
                referenced_data = referenced_model.dataframe[referenced_column].astype(str)
                tooltips = []
                for item in referenced_data:
                    tooltip_data = referenced_model.dataframe[referenced_model.dataframe[referenced_column] == int(item)].to_dict(
                        orient='records')[0]
                    tooltip = ""
                    for k, v in tooltip_data.items():
                        tooltip += "{}: {}\n".format(k, v)
                    tooltips.append(tooltip)

                field = HoverComboBox(tooltips, self)
                completer = QCompleter(referenced_data, self)
                field.setCompleter(completer)
                field.addItems(referenced_data)
                field.setCurrentText(str(col_value))
            else:
                if col_type == "int":
                    field = QLineEdit(self)
                    field.setValidator(QIntValidator())
                    field.setText(str(col_value))
                elif col_type == "float":
                    field = QLineEdit(self)
                    field.setValidator(QDoubleValidator())
                    field.setText(str(col_value))
                elif col_type == "date" or col_type == "datetime":
                    field = QDateEdit()
                    field.setDisplayFormat("d-MMM-yyyy")
                    field.setCalendarPopup(True)
                    col_value = QDate(col_value.year, col_value.month, col_value.day)
                    field.setDate(col_value)
                else:  # For strings and other types
                    field = QLineEdit(self)
                    field.setText(str(col_value))

                if is_primary:
                    field.setReadOnly(True)

            self.fields[col_name] = field

            # Add label and field to the grid layout
            self.form_layout.addWidget(QLabel(col_name), row, col * 2)
            self.form_layout.addWidget(field, row, col * 2 + 1)

            if col == 0:
                col = 1
            else:
                col = 0
                row += 1

            # Add a horizontal line separator between columns
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(separator)

        # Add Save and Cancel buttons in one row
        self.button_layout = QHBoxLayout()
        self.button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        # Add button layout to the bottom of the main layout
        self.layout.addStretch()
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def save(self):
        new_data = {}
        for col, field in self.fields.items():
            if isinstance(field, QDateTimeEdit):
                new_data[col] = field.dateTime().toString("yyyy-MM-dd")
            elif isinstance(field, QComboBox):
                new_data[col] = field.currentText()
            else:
                new_data[col] = field.text()
        print("Updated data:", new_data)
        self.accept()
