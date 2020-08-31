from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
import sys
from PyQt5 import QtGui, QtCore


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 Events and Signals"
        self.top = 100
        self.left = 100
        self.width = 400
        self.height = 300
        self.initWindow()

    def initWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.UiComponets()
        self.show()

    def UiComponets(self):
        button = QPushButton("Close", self)
        button.move(50, 50)
        button.setIcon(QtGui.QIcon("icon.png"))
        # button.setIconSize(QtCore.QSize(40, 40))
        button.setToolTip("This is click me button")
        button.clicked.connect(self.Clickme)

    def Clickme(self):
        sys.exit()
        # print("Hello world")


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec_())
