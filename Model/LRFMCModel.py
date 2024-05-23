import pandas as pd
from Model.Base.BaseModel import BaseModel


class LRFMCModel:
    def __init__(self, connector):
        self.connector = connector
        self.query = """
                WITH MaxDate AS (
                    SELECT MAX(orderDate) AS maxOrderDate
                    FROM salesorder
                ),
                
                LRFMC AS (
                    SELECT 
                        c.custId,
                        c.companyName,
                        MIN(so.orderDate) AS firstPurchaseDate,
                        MAX(so.orderDate) AS lastPurchaseDate,
                        DATEDIFF(MAX(so.orderDate), MIN(so.orderDate)) AS relationshipLength,
                        COUNT(so.orderId) AS purchaseFrequency,
                        SUM(od.unitPrice * od.quantity * (1 - od.discount)) AS totalSpending,
                        AVG(od.discount) * 100 AS avgDiscountPercent,  -- Calculate average discount percentage
                        DATEDIFF((SELECT maxOrderDate FROM MaxDate), MAX(so.orderDate)) AS recency
                    FROM 
                        customer c
                        JOIN salesorder so ON c.custId = so.custId
                        JOIN orderdetail od ON so.orderId = od.orderId
                    GROUP BY 
                        c.custId, c.companyName
                )
                SELECT *
                FROM LRFMC;
            """
        self.query_dataframe()

    def query_dataframe(self):
        data = self.connector.execute_query(self.query)

        col_names = ['custId', 'companyName', 'firstPurchaseDate', 'lastPurchaseDate', 'relationshipLength', 'purchaseFrequency', 'totalSpending', 'avgDiscountPercent', 'recency']
        selected_cols = ['custId', 'relationshipLength', 'purchaseFrequency', 'totalSpending', 'avgDiscountPercent', 'recency']
        self.dataframe = pd.DataFrame(data, columns=col_names)[selected_cols]


