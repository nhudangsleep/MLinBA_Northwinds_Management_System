from Model.Base.BaseModel import BaseModel


class SupplierModel(BaseModel):
    def __init__(self, connector):
        table_name = "supplier"
        super().__init__(table_name, connector)

    def create_new_record(self, **data):
        pass

    def update_record(self, pk):
        pass

    def remove_record(self, pk):
        pass
