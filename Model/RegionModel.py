from Model.Base.BaseModel import BaseModel


class RegionModel(BaseModel):
    def __init__(self, connector):
        table_name = "region"
        super().__init__(table_name, connector)
