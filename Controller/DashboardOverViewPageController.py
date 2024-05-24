import traceback
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QWidget
from Controller.Base.BaseController import BaseController
from Model.CategoryModel import CategoryModel
from Model.OrderDetailModel import OrderDetailModel
from Model.ProductModel import ProductModel
from Model.SalesOrderModel import SalesOrderModel
from Service.KPICardService import KPIData, KPICard
from View.DashboardOverviewPage import Ui_DashboardOverviewPage  # Make sure this import is correct
from dotenv import load_dotenv
import os


load_dotenv()


class DashboardOverViewPageController(BaseController):
    def __init__(self, view, dialog):
        super().__init__()
        self.view = view
        self.dialog = dialog

        self.sales_order_model = SalesOrderModel(self.connector)
        self.order_detail_model = OrderDetailModel(self.connector)
        self.product_model = ProductModel(self.connector)
        self.category_model = CategoryModel(self.connector)
        self.kpi_cards = {}
        self.setup_ui()

    def setup_ui(self):
        self.load_data()
        self.plot_sales_comparison()
        self.plot_top_sales_by_product()
        self.calculate_metrics()

    def load_data(self):
        try:
            merged_self_df = pd.merge(self.sales_order_model.dataframe, self.order_detail_model.dataframe, on='orderId')
            merged_self_df['orderDate'] = pd.to_datetime(merged_self_df['orderDate'])
            merged_self_df['totalSales'] = merged_self_df['unitPrice'] * merged_self_df['quantity'] * (1 - merged_self_df['discount'])

            merged_self_df['Month-Year'] = merged_self_df['orderDate'].dt.to_period('M')
            monthly_sales = merged_self_df.groupby('Month-Year').agg({'totalSales': 'sum'}).reset_index()

            monthly_sales_shifted = monthly_sales.copy()
            monthly_sales_shifted['Month-Year'] = (
                        monthly_sales_shifted['Month-Year'].dt.to_timestamp() + pd.DateOffset(years=1)).dt.to_period('M')

            # Rename columns for clarity
            monthly_sales.rename(columns={'totalSales': 'Current Sales'}, inplace=True)
            monthly_sales_shifted.rename(columns={'totalSales': 'Last Year Sales'}, inplace=True)
            self.comparison_df = pd.merge(monthly_sales, monthly_sales_shifted, on='Month-Year', how='outer').dropna(subset=['Current Sales'])
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while loading data: {str(e)}")

    def plot_sales_comparison(self):
        try:
            fig, ax = plt.subplots()
            self.comparison_df['Month-Year'] = self.comparison_df['Month-Year'].dt.to_timestamp()

            ax.plot(self.comparison_df['Month-Year'], self.comparison_df['Current Sales'], label='Current Sales')
            ax.plot(self.comparison_df['Month-Year'], self.comparison_df['Last Year Sales'], label='Last Year Sales')
            ax.set_xlabel('Month-Year')
            ax.set_ylabel('Sales')
            ax.set_title('Monthly Sales Comparison')
            ax.legend()

            # Clear the layout before adding the new plot
            for i in reversed(range(self.view.verticalLayout_visualize.count())):
                self.view.verticalLayout_visualize.itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, self.dialog)

            self.view.verticalLayout_visualize.addWidget(toolbar)
            self.view.verticalLayout_visualize.addWidget(canvas)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while plotting sales comparison: {str(e)}")

    def plot_top_sales_by_product(self):
        try:
            # Merge necessary dataframes
            merged_df = pd.merge(self.order_detail_model.dataframe, self.product_model.dataframe, on='productId')
            merged_df['totalSales'] = merged_df['unitPrice_x'] * merged_df['quantity'] * (1 - merged_df['discount'])

            # Ensure totalSales is numeric
            merged_df['totalSales'] = pd.to_numeric(merged_df['totalSales'], errors='coerce')

            # Group by product and sum the total sales
            product_sales = merged_df.groupby('productName').agg({'totalSales': 'sum'}).reset_index()

            # Ensure totalSales is numeric after grouping
            product_sales['totalSales'] = pd.to_numeric(product_sales['totalSales'], errors='coerce')

            # Get the top 15 products by total sales
            top_products = product_sales.nlargest(15, 'totalSales')

            fig, ax = plt.subplots()
            ax.bar(top_products['productName'], top_products['totalSales'])
            ax.set_xlabel('Product')
            ax.set_ylabel('Total Sales')
            ax.set_title('Top 15 Products by Sales')
            ax.tick_params(axis='x', rotation=45)

            # Clear the layout before adding the new plot
            for i in reversed(range(self.view.verticalLayout_visualize_2.count())):
                self.view.verticalLayout_visualize_2.itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, self.dialog)

            self.view.verticalLayout_visualize_2.addWidget(toolbar)
            self.view.verticalLayout_visualize_2.addWidget(canvas)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while plotting top sales by product: {str(e)}")
    def calculate_metrics(self):
        try:
            # Calculate TotalSales
            total_sales = self.order_detail_model.dataframe['unitPrice'] * self.order_detail_model.dataframe['quantity'] * (1 - self.order_detail_model.dataframe['discount'])
            self.order_detail_model.dataframe['totalSales'] = total_sales
            total_sales_amount = total_sales.sum()/1000
            rounded_total_sales_amount = round(total_sales_amount, 2)

            # Calculate Number of Orders
            number_of_orders = self.sales_order_model.dataframe['orderId'].nunique()

            # Calculate Total Quantity Sold
            total_quantity_sold = self.order_detail_model.dataframe['quantity'].sum()

            # Calculate Fulfillment Rate
            merged_df = pd.merge(self.sales_order_model.dataframe, self.order_detail_model.dataframe, on='orderId')
            merged_df['orderDate'] = pd.to_datetime(merged_df['orderDate'])
            merged_df['shippedDate'] = pd.to_datetime(merged_df['shippedDate'])
            on_time_orders = merged_df[merged_df['shippedDate'] <= merged_df['requiredDate']]
            fulfillment_rate = len(on_time_orders) / len(merged_df) * 100
            rounded_fulfillment_rate = round(fulfillment_rate, 2)
            # Update KPI cards
            self.view.frame_kpis_01.update_kpi(KPIData(value=rounded_total_sales_amount, unit='Total Sales (K) USD', icon_path = os.getenv('TOTAL_SALES_ICON')))
            self.view.frame_kpis_02.update_kpi(KPIData(value=number_of_orders, unit='Number of Orders', icon_path = os.getenv('TOTAL_ORDER_ICON')))
            self.view.frame_kpis_03.update_kpi(KPIData(value=total_quantity_sold, unit='Total Quantity Units', icon_path = os.getenv('TOTAL_QUANTITY_ICON')))
            self.view.frame_kpis_04.update_kpi(KPIData(value=rounded_fulfillment_rate, unit='Fulfillment Rate %', icon_path = os.getenv('FULFILLMENT_ICON')))

        except Exception as e:
            traceback.print_exc()
