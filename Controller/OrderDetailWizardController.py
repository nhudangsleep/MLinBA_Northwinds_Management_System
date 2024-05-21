# ManagementPageController.py
import importlib
import traceback

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController


class OrderDetailWizardController(BaseController):
    def __init__(self, view, dialog=None, additional_data=None):
        super().__init__()
        self.view = view
        self.dialog = dialog
        self.additional_data = additional_data
        self.view.pushButton_close.clicked.connect(self.process_close)

        self.preload_data()

    def process_close(self):
        try:
            self.dialog.close()
        except:
            traceback.print_exc()

    def preload_data(self):
        self.connect_table("OrderDetail", self.dialog, self.additional_data)


