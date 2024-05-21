from PyQt6 import QtCore, QtGui, QtWidgets

from Controller.ManagementPageController import ManagementPageController
from Controller.SalesPageController import SalesPageController
from View.ManagementPage import Ui_WizardManagementPage
from Service.Base.Dropbox import DropdownButton
from View.SalesPage import Ui_WizardSalesPage


# UI class using DropdownButton
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(610, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.frame_app_name = QtWidgets.QFrame(self.centralwidget)
        self.frame_app_name.setGeometry(QtCore.QRect(10, 10, 591, 51))
        self.frame_app_name.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_app_name.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_app_name.setObjectName("frame_app_name")

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.frame_app_name)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(-1, 0, 591, 43))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")

        self.frame_app_name_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.frame_app_name_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_app_name_layout.setObjectName("frame_app_name_layout")

        self.label_app_name = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Sylfaen")
        font.setPointSize(20)
        self.label_app_name.setFont(font)
        self.label_app_name.setStyleSheet("background-color: rgb(64, 102, 219); color: rgb(255, 255, 255)")
        self.label_app_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_app_name.setObjectName("label_app_name")
        self.frame_app_name_layout.addWidget(self.label_app_name)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 60, 591, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Dropdown Buttons Setup
        self.pushButton_dashboard = DropdownButton("Dashboard", self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.pushButton_dashboard)

        self.pushButton_sales = DropdownButton("Sales", self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.pushButton_sales)

        self.pushButton_operation = DropdownButton("Operation", self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.pushButton_operation)

        self.pushButton_catalog = DropdownButton("Catalog", self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.pushButton_catalog)

        self.pushButton_predictive_model = DropdownButton("ML Model", self.horizontalLayoutWidget)
        self.horizontalLayout.addWidget(self.pushButton_predictive_model)

        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(10, 100, 590, 270))
        self.stackedWidget.setObjectName("stackedWidget")

        self.page_dashboard = QtWidgets.QWidget()
        self.page_dashboard.setObjectName("page_dashboard")
        self.stackedWidget.addWidget(self.page_dashboard)

        self.page_management = QtWidgets.QWidget()
        self.page_management.setObjectName("page_management")
        self.stackedWidget.addWidget(self.page_management)
        self.wizard_page_ui = Ui_WizardManagementPage()
        self.wizard_page_ui.setupUi(self.page_management)
        self.management_page_controller = ManagementPageController(self.wizard_page_ui, MainWindow)

        self.page_sales = QtWidgets.QWidget()
        self.page_sales.setObjectName("page_sales")
        self.stackedWidget.addWidget(self.page_sales)
        self.wizard_sales_ui = Ui_WizardSalesPage()
        self.wizard_sales_ui.setupUi(self.page_sales)
        self.sales_page_controller = SalesPageController(self.wizard_sales_ui, MainWindow)

        self.page_predictive_model = QtWidgets.QWidget()
        self.page_predictive_model.setObjectName("page_predictive_model")
        self.stackedWidget.addWidget(self.page_predictive_model)

        self.line = QtWidgets.QFrame(parent=self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 85, 590, 16))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 610, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_app_name.setText(_translate("MainWindow", "Northwind Management System"))

