from Model.Base.BaseModel import BaseModel


class ProductModel(BaseModel):
    def __init__(self, connector):
        table_name = "product"
        super().__init__(table_name, connector)

    def create_new_record(self, **data):
        pass

    def update_record(self, pk):
        pass

    def remove_record(self, pk):
        pass
