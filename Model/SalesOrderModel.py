from Model.Base.BaseModel import BaseModel


class SalesOrderModel(BaseModel):
    def __init__(self, connector):
        table_name = "salesorder"
        super().__init__(table_name, connector)

        print(self.referenced_pair)


    def create_new_record(self, **data):
        pass

    def update_record(self, pk):
        pass

    def remove_record(self, pk):
        pass

