from copy import deepcopy

from PyQt6.QtCore import Qt
import pandas as pd
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QWidget
from PyQt6.QtCore import QDate
from Controller.Base.BaseController import BaseController
from Model.Base.FilterProxyModel import FilterProxyModel
from Model.CategoryModel import CategoryModel
from Model.OrderDetailModel import OrderDetailModel
from Model.ProductModel import ProductModel
from Model.SalesOrderModel import SalesOrderModel
from Service.KPICardService import KPIData, KPICard
from View.DashboardOverviewPage import Ui_DashboardOverviewPage  # Make sure this import is correct
from Model.Base.BaseDataframeModel import BaseDataframeTableModel
from Model.RevenueDiffModel import RevenueDiffModel
from dotenv import load_dotenv
import os

load_dotenv()


class DashboardDetailPageController(BaseController):
    def __init__(self, view, dialog):
        super().__init__()
        self.view = view
        self.dialog = dialog
        self.sales_order_model = SalesOrderModel(self.connector)
        self.order_detail_model = OrderDetailModel(self.connector)
        self.product_model = ProductModel(self.connector)
        self.category_model = CategoryModel(self.connector)
        self.kpi_cards = {}

        self.sales_merged_compair = None
        self.filter_proxy_model = FilterProxyModel()

        self.setup_ui()

    def setup_ui(self):
        self.load_data()
        self.setup_comboboxes()
        # self.plot_sales_comparison()
        # self.calculate_metrics()

    def setup_comboboxes(self):
        current_year = 2009
        self.view.comboBox.addItems([str(year) for year in range(current_year - 2, current_year)])
        self.view.comboBox.setCurrentText(str(current_year))

        self.view.comboBox_2.addItems(['Q1', 'Q2', 'Q3', 'Q4'])
        current_quarter = (QDate.currentDate().month() - 1) // 3 + 1
        self.view.comboBox_2.setCurrentText(f'Q{current_quarter}')

        self.view.comboBox.currentIndexChanged.connect(self.update_dashboard)
        self.view.comboBox_2.currentIndexChanged.connect(self.update_dashboard)

    def get_selected_year_and_quarter(self):
        selected_year = self.view.comboBox.currentText()
        selected_quarter = self.view.comboBox_2.currentText()
        if selected_year and selected_quarter:
            return int(selected_year), selected_quarter
        else:
            return None, None

    def update_dashboard(self):
        selected_year, selected_quarter = self.get_selected_year_and_quarter()
        self.plot_sales_comparison(selected_year, selected_quarter)
        self.calculate_metrics(selected_year, selected_quarter)

    def load_data(self):
        try:
            merged_df = pd.merge(self.sales_order_model.dataframe, self.order_detail_model.dataframe, on='orderId')
            merged_df['orderDate'] = pd.to_datetime(merged_df['orderDate'])
            merged_df['totalSales'] = merged_df['unitPrice'] * merged_df['quantity'] * (1 - merged_df['discount'])

            merged_df['Month-Year'] = merged_df['orderDate'].dt.to_period('M')
            monthly_sales = merged_df.groupby('Month-Year').agg({'totalSales': 'sum'}).reset_index()

            monthly_sales_shifted = monthly_sales.copy()
            monthly_sales_shifted['Month-Year'] = (
                        monthly_sales_shifted['Month-Year'].dt.to_timestamp() + pd.DateOffset(years=1)).dt.to_period(
                'M')

            monthly_sales.rename(columns={'totalSales': 'Current Sales'}, inplace=True)
            monthly_sales_shifted.rename(columns={'totalSales': 'Last Year Sales'}, inplace=True)

            comparison_df = pd.merge(monthly_sales, monthly_sales_shifted, on='Month-Year', how='outer').dropna(
                subset=['Current Sales'])
            self.sales_merged_compair = RevenueDiffModel(comparison_df)

            self.filter_proxy_model.setSourceModel(self.sales_merged_compair)
            self.view.TableView.setModel(self.filter_proxy_model)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while loading data: {str(e)}")

    def plot_sales_comparison(self, selected_year=None, selected_quarter=None):
        if not selected_year or not selected_quarter:
            QMessageBox.critical(self.dialog, "Error", "Selected year or quarter is not valid.")
            return

        try:
            # Define the start and end months based on the selected quarter
            quarter_to_months = {
                'Q1': (1, 3),
                'Q2': (4, 6),
                'Q3': (7, 9),
                'Q4': (10, 12),
            }
            start_month, end_month = quarter_to_months[selected_quarter]
            start_date = f'{selected_year}-{start_month:02d}'
            end_date = f'{selected_year}-{end_month:02d}'

            # Filter the data based on the selected date range
            self.sales_merged_compair.filter_month_year(start_date, end_date)

            # Plotting the filtered data
            temp = deepcopy(self.sales_merged_compair.dataframe)
            fig, ax = plt.subplots()
            temp['Month-Year'] = temp['Month-Year'].apply(lambda x: x.to_timestamp())
            ax.plot(temp['Month-Year'], temp['Current Sales'], label='Current Sales')
            ax.plot(temp['Month-Year'], temp['Last Year Sales'], label='Last Year Sales')
            ax.set_xlabel('Month-Year')
            ax.set_ylabel('Sales')
            ax.set_title('Monthly Sales Comparison')
            ax.legend()

            # Clear the previous plot before adding the new one
            for i in reversed(range(self.view.verticalLayout_visualize.count())):
                self.view.verticalLayout_visualize.itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, self.dialog)

            self.view.verticalLayout_visualize.addWidget(toolbar)
            self.view.verticalLayout_visualize.addWidget(canvas)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while plotting sales comparison: {str(e)}")

    def calculate_metrics(self, selected_year=None, selected_quarter=None):
        if not selected_year or not selected_quarter:
            QMessageBox.critical(self.dialog, "Error", "Selected year or quarter is not valid.")
            return

        try:
            # Access the current dataframe from the model
            current_dataframe = self.sales_merged_compair.dataframe

            total_sales_amount = current_dataframe['Current Sales'].sum() / 1000
            rounded_total_sales_amount = round(total_sales_amount, 2)

            # Calculate Number of Orders
            number_of_orders = len(current_dataframe)

            # Calculate Total Quantity Sold
            total_quantity_sold = current_dataframe['Current Sales'].count()

            # Calculate Fulfillment Rate
            # Assuming `orderDate` and `shippedDate` columns are available in the current dataframe
            merged_df = pd.merge(self.sales_order_model.dataframe, self.order_detail_model.dataframe, on='orderId')
            merged_df['orderDate'] = pd.to_datetime(merged_df['orderDate'])
            merged_df['shippedDate'] = pd.to_datetime(merged_df['shippedDate'])
            on_time_orders = merged_df[merged_df['shippedDate'] <= merged_df['requiredDate']]
            fulfillment_rate = len(on_time_orders) / len(merged_df) * 100
            rounded_fulfillment_rate = round(fulfillment_rate, 2)

            # Update KPI cards
            self.view.frame_kpis_01.update_kpi(KPIData(value=rounded_total_sales_amount, unit='Total Sales (K) USD',
                                                       icon_path=os.getenv('TOTAL_SALES_ICON')))
            self.view.frame_kpis_02.update_kpi(
                KPIData(value=number_of_orders, unit='Number of Orders', icon_path=os.getenv('TOTAL_ORDER_ICON')))
            self.view.frame_kpis_03.update_kpi(KPIData(value=total_quantity_sold, unit='Total Quantity Units',
                                                       icon_path=os.getenv('TOTAL_QUANTITY_ICON')))
            self.view.frame_kpis_04.update_kpi(KPIData(value=rounded_fulfillment_rate, unit='Fulfillment Rate %',
                                                       icon_path=os.getenv('FULFILLMENT_ICON')))
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while calculating metrics: {str(e)}")

