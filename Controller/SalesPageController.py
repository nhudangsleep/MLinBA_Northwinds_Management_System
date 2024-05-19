# ManagementPageController.py

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController


class SalesPageController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
