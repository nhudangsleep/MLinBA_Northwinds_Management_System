import importlib
import pickle
from copy import deepcopy, copy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import traceback

from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtWidgets import QMessageBox, QDialog, QFileDialog

from Model.Base.BaseModel import BaseModel
from Controller.Base.BaseController import BaseController
from Model.Base.FilterProxyModel import FilterProxyModel
from Model.CustomerModel import CustomerModel
from Model.KmeansClusterModel import KmeansClusterModel
from Model.LRFMCModel import LRFMCModel
from Service.Base.KmeansService import KmeansService
from Service.VisualizationDialogService import VisualizationDialogService


class MachineLearningPageController(BaseController):
    def __init__(self, view, dialog):
        super().__init__()
        self.view = view
        self.dialog = dialog

        self.view.pushButton_visualize_model.clicked.connect(self.process_visualize_model_button)
        self.view.pushButton_elbow.clicked.connect(self.process_elbow_button)
        self.view.pushButton_load_model.clicked.connect(self.process_load_model)
        self.view.pushButton_train_model.clicked.connect(self.process_train_model)
        self.view.pushButton_save_model.clicked.connect(self.process_save_model)
        self.view.pushButton_export_to_excel.clicked.connect(self.process_export_to_excel)

        self.view.comboBox_cluster.currentIndexChanged.connect(self.process_cluster_selection)
        self.setup_architecture_dropdown()

    def setup_architecture_dropdown(self):
        self.view.lrfmc_model = LRFMCModel(self.connector)
        self.view.customer_model = CustomerModel(self.connector)
        items = ['RFM', 'LRFMC']
        for item in items:
            self.view.comboBox_model_architecture.addItem(item)

    def process_visualize_model_button(self):
        try:
            if not self.kmeans_service.is_trained:
                QMessageBox.warning(self.dialog, "Model Not Trained or Loaded",
                                    "Please train a model or load an existing model before visualizing.")
                return
        except:
            QMessageBox.warning(self.dialog, "Model Not Trained or Loaded",
                                "Please train a model or load an existing model before visualizing.")
            return
        try:
            columns = self.view.lrfmc_model.dataframe.columns.tolist()
            dialog = VisualizationDialogService(columns, self.dialog)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_columns = dialog.get_selected_columns()
                if len(selected_columns) < 2 or len(selected_columns) > 3:
                    QMessageBox.warning(self.dialog, "Invalid Selection", "Please select between 2 and 3 columns.")
                else:
                    self.visualize_clusters(selected_columns)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while visualizing clusters: {str(e)}")

    def visualize_clusters(self, selected_columns):
        layout = self.view.verticalLayout
        if layout is not None:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

        # Create a matplotlib figure
        fig = Figure()
        canvas = FigureCanvas(fig)

        # Get the data for the selected columns and convert to float
        data = self.view.lrfmc_model.dataframe[selected_columns].astype(float)

        if len(selected_columns) == 3:
            ax = fig.add_subplot(111, projection='3d')
            scatter = ax.scatter(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2], c=self.kmeans_service.model.labels_)
            ax.set_zlabel(selected_columns[2])
        else:
            ax = fig.add_subplot(111)
            scatter = ax.scatter(data.iloc[:, 0], data.iloc[:, 1], c=self.kmeans_service.model.labels_)

        ax.set_title('KMeans Clusters')
        ax.set_xlabel(selected_columns[0])
        ax.set_ylabel(selected_columns[1])

        toolbar = NavigationToolbar(canvas, self.dialog)
        layout.addWidget(toolbar)
        canvas.setParent(self.view.frame)
        layout.addWidget(canvas)
        canvas.draw()

    def process_elbow_button(self):
        try:
            # Determine if the selected architecture is 'RFM'
            selected_architecture = self.view.comboBox_model_architecture.currentText()
            is_rfm = selected_architecture == 'RFM'

            # Create an instance of KmeansService with the dataframe and is_rfm flag
            self.kmeans_alternative_service = KmeansService(self.view.lrfmc_model.dataframe, is_rfm=is_rfm)

            elbow_scores = self.kmeans_alternative_service.calculate_elbow_scores()

            self.plot_elbow_scores(elbow_scores)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while calculating elbow scores: {str(e)}")

    def plot_elbow_scores(self, elbow_scores):
        layout = self.view.verticalLayout
        if layout is not None:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

        # Create a matplotlib figure
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Plot the elbow scores
        ax.plot(list(elbow_scores.keys()), list(elbow_scores.values()), marker='o')
        ax.set_title('Elbow Method for Optimal k')
        ax.set_xlabel('Number of clusters (k)')
        ax.set_ylabel('Inertia')

        # Adjust the figure to fit the frame size
        canvas.setParent(self.view.frame)
        layout.addWidget(canvas)
        canvas.draw()

    def process_load_model(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self.dialog, "Load Model", "", "Pickle Files (*.pkl)")
            if filename:
                with open(filename, 'rb') as file:
                    self.kmeans_service = pickle.load(file)
                self.view.label_model_label.setText(str(filename.split('/')[-1].split('.')[0] + " " + "Model"))
                self.view.kmeans_cluster_model = KmeansClusterModel(self.kmeans_service.summarize_clusters())
                self.view.kmeans_cluster_proxy_model = FilterProxyModel()
                self.view.kmeans_cluster_proxy_model.setSourceModel(self.view.kmeans_cluster_model)
                self.view.TableViewCluster.setModel(self.view.kmeans_cluster_proxy_model)
                self.view.lineEdit_num_cluster.setText(str(self.kmeans_service.num_k))
                self.update_cluster_combo_box(self.kmeans_service.model.labels_)
                self.visualize_clusters(['purchaseFrequency', 'totalSpending', 'recency'])
                QMessageBox.information(self.dialog, "Success", "Model loaded successfully.")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while loading the model: {str(e)}")

    def process_train_model(self):
        try:
            num_k = self.view.lineEdit_num_cluster.text()
            if num_k == '':
                QMessageBox.warning(self.dialog, "Invalid Input",
                                    "Please enter the number of clusters (k) before training the model.")
                return
            num_k = int(num_k)
            selected_architecture = self.view.comboBox_model_architecture.currentText()
            is_rfm = selected_architecture == 'RFM'

            self.kmeans_service = KmeansService(self.view.lrfmc_model.dataframe, num_k=num_k, is_rfm=is_rfm)
            self.kmeans_service.train_model()
            clustered_data = self.kmeans_service.get_clustered_data()
            QMessageBox.information(self.dialog, "Success", "Model trained successfully and clusters created.")

            self.view.kmeans_cluster_model = KmeansClusterModel(self.kmeans_service.summarize_clusters())
            self.view.kmeans_cluster_proxy_model = FilterProxyModel()
            self.view.kmeans_cluster_proxy_model.setSourceModel(self.view.kmeans_cluster_model)
            self.view.TableViewCluster.setModel(self.view.kmeans_cluster_proxy_model)
            self.update_cluster_combo_box(self.kmeans_service.model.labels_)
            self.visualize_clusters(['purchaseFrequency', 'totalSpending', 'recency'])
        except:
            traceback.print_exc()

    def update_cluster_combo_box(self, labels):
        self.view.comboBox_cluster.clear()
        unique_labels = set(labels)
        for label in unique_labels:
            self.view.comboBox_cluster.addItem(f"Cluster {label}")

    def process_cluster_selection(self):
        selected_cluster = self.view.comboBox_cluster.currentText()
        if selected_cluster:
            cluster_label = int(selected_cluster.split()[-1])
            self.filter_customers_by_cluster(cluster_label)

    def filter_customers_by_cluster(self, cluster_label):
        try:
            cluster_mask = self.kmeans_service.model.labels_ == cluster_label
            customer_ids = self.view.lrfmc_model.dataframe.loc[cluster_mask, 'custId'].values
            self.view.customer_proxy_model = FilterProxyModel()
            self.view.temp_customer_model = CustomerModel(self.connector)
            self.view.temp_customer_model.dataframe = self.view.customer_model.dataframe[self.view.customer_model.dataframe['custId'].isin(customer_ids)]
            self.view.customer_proxy_model.setSourceModel(self.view.temp_customer_model)
            self.view.TableView.setModel(self.view.customer_proxy_model)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while filtering customers: {str(e)}")

    def process_save_model(self):
        try:
            # Open a file dialog to select the file path for saving the model
            filename, _ = QFileDialog.getSaveFileName(self.dialog, "Save Model", "", "Pickle Files (*.pkl)")

            if filename:
                with open(filename, 'wb') as file:
                    pickle.dump(self.kmeans_service, file)

                QMessageBox.information(self.dialog, "Success", "Model saved successfully.")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while saving the model: {str(e)}")

    def process_export_to_excel(self):
        try:
            if not self.kmeans_service.is_trained:
                QMessageBox.warning(self.dialog, "Model Not Trained or Loaded",
                                    "Please train a model or load an existing model before exporting to Excel.")
                return
        except:
            QMessageBox.warning(self.dialog, "Model Not Trained or Loaded",
                                "Please train a model or load an existing model before exporting to Excel.")
            return
        try:
            filename, _ = QFileDialog.getSaveFileName(self.dialog, "Export to Excel", "", "Excel Files (*.xlsx)")

            if filename:
                self.view.temp_customer_model.dataframe.to_excel(filename, index=False)
                QMessageBox.information(self.dialog, "Success", "Data exported to Excel successfully.")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self.dialog, "Error", f"An error occurred while exporting to Excel: {str(e)}")

