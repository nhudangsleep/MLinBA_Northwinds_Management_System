from Model.Base.BaseModel import BaseModel


class TerritoryModel(BaseModel):
    def __init__(self, connector):
        table_name = "territory"
        super().__init__(table_name, connector)
