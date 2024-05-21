import importlib
from PyQt6.QtCore import QObject, pyqtSignal


class DataLoadWorker(QObject):
    data_loaded = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, connector, table_name, additional_data=None):
        super().__init__()
        self.connector = connector
        self.table_name = table_name
        self.additional_data = additional_data

    def load_data(self):
        try:
            module_name = f"Model.{self.table_name}Model"
            model_class = getattr(importlib.import_module(module_name), f"{self.table_name}Model")
            model = model_class(self.connector)
            if self.additional_data:
                model.filter_collection_data(self.additional_data)
            self.data_loaded.emit(model)
        except Exception as e:
            self.error_occurred.emit(str(e))
