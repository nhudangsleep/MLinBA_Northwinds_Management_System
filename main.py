from Controller.MainWindowController import MainWindowController
from PyQt6.QtWidgets import QApplication, QMainWindow


app = QApplication([])
myWindow = MainWindowController()
myWindow.setupUi(QMainWindow())
myWindow.show()
app.exec()
