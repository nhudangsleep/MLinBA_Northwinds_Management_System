from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QToolBar
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import traceback


class FullScreenChartService(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Full Screen Chart")
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Create a central widget and set it as the central widget of the main window
        central_widget = self.centralWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Create a figure and canvas for the plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Create a toolbar and add actions
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self.action_exit = QAction("Exit Full Screen", self)
        self.action_exit.triggered.connect(self.exit_full_screen)
        self.toolbar.addAction(self.action_exit)

    def exit_full_screen(self):
        self.close()
