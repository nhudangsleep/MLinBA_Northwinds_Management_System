import traceback
import bcrypt
from PyQt6 import QtGui
from PyQt6.QtWidgets import QMessageBox, QMainWindow

from Controller.Base.BaseController import BaseController
from Controller.MainWindowController import MainWindowController
from Model.AccountModel import AccountModel
from View.LoginWindow import Ui_LoginWindow


class LoginWindowController(Ui_LoginWindow, BaseController):
    def __init__(self):
        super().__init__()
        BaseController.__init__(self)
        self.account_model = AccountModel(self.connector)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.pushButtonLogin.clicked.connect(self.processLogin)

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    def processLogin(self):
        user_name = self.lineEditUserName.text()
        password = self.lineEditPassword.text()
        hashed_password = str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
        is_correct = False
        if user_name in self.account_model.dataframe['username'].values:
            stored_hashed_password = self.account_model.dataframe.loc[
                self.account_model.dataframe['username'] == user_name, 'password'
            ].values[0]

            # Check if the stored hashed password matches the input hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                is_correct = True

        if is_correct:
            QMessageBox.information(self.MainWindow, "Login Successful", "You have successfully logged in.")
            window = QMainWindow()
            window.setWindowIcon(QtGui.QIcon('Images/LLL.png'))

            self.UserUi = MainWindowController()
            self.UserUi.setupUi(window)
            self.UserUi.show()
            self.MainWindow.close()
        else:
            QMessageBox.warning(self.MainWindow, "Login Failed", "Incorrect username or password. Please try again.")

    def show(self):
        self.MainWindow.show()