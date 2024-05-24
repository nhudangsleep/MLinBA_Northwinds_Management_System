from PyQt6 import QtGui

from Controller.LoginWindowController import LoginWindowController
from Controller.MainWindowController import MainWindowController
from PyQt6.QtWidgets import QApplication, QMainWindow



qApp=QApplication([])
qmainWindow=QMainWindow()
qmainWindow.setWindowIcon(QtGui.QIcon('Images/LLL.png'))
window=LoginWindowController()
window.setupUi(qmainWindow)
window.show()
qApp.exec()

