from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        title = "QPushButton"
        left = 500
        top = 200
        width = 300
        height = 250
        iconName = "icon.png"

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iconName))
        self.setGeometry(left, top, width, height)
        self.UiComponets()
        self.show()

    def UiComponets(self):
        button = QPushButton("Click me", self)
        # button.move(50, 50)
        button.setGeometry(QRect(100, 100, 111, 50))
        button.setIcon(QtGui.QIcon("icon.png"))
        button.setIcon(QtGui.QIcon('icon.png'))
        button.setIconSize(QtCore.QSize(40, 40))
        button.setToolTip("This is click me button")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
