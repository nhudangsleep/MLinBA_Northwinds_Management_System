# ManagementPageController.py
import importlib
import traceback

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController


class ManagementPageController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view

