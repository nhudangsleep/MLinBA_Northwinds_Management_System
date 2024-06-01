import pandas as pd

from Model.Base.BaseDataframeModel import BaseDataframeTableModel


class RevenueDiffModel(BaseDataframeTableModel):
    def __init__(self, dataframe):
        super().__init__(dataframe)
        self.original_dataframe = dataframe.copy()

    def filter_month_year(self, start_date, end_date):
        # Convert start_date and end_date to Period objects
        start_period = pd.Period(start_date, freq='M')
        end_period = pd.Period(end_date, freq='M')
        self.dataframe = self.original_dataframe[
            (self.original_dataframe['Month-Year'] >= start_period) &
            (self.original_dataframe['Month-Year'] <= end_period)
        ]
        self.layoutChanged.emit()

    def reset_to_original(self):
        self.dataframe = self.original_dataframe.copy()
        self.layoutChanged.emit()
