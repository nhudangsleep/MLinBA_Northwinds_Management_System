from Model.Base.BaseModel import BaseModel


class EmployeeTerritoryModel(BaseModel):
    def __init__(self, connector):
        table_name = "employeeterritory"
        super().__init__(table_name, connector)

