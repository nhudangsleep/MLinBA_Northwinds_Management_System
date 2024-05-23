from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QMessageBox


class VisualizationDialogService(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Columns for Visualization")
        self.columns = columns
        self.selected_columns = []
        self.layout = QVBoxLayout(self)

        # Add checkboxes for each column
        self.checkboxes = {}
        for col in self.columns:
            checkbox = QCheckBox(col)
            checkbox.stateChanged.connect(self.check_selection)
            self.layout.addWidget(checkbox)
            self.checkboxes[col] = checkbox

        # Add OK and Cancel buttons
        self.button_ok = QPushButton("OK", self)
        self.button_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.button_ok)

        self.button_cancel = QPushButton("Cancel", self)
        self.button_cancel.clicked.connect(self.reject)
        self.layout.addWidget(self.button_cancel)

    def check_selection(self):
        self.selected_columns = [col for col, cb in self.checkboxes.items() if cb.isChecked()]
        if len(self.selected_columns) < 2 or len(self.selected_columns) > 3:
            self.button_ok.setDisabled(True)
        else:
            self.button_ok.setDisabled(False)

    def get_selected_columns(self):
        return self.selected_columns
