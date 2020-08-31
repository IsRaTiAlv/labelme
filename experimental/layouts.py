from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QGroupBox, QHBoxLayout, QVBoxLayout
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect


class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "QPushButton"
        self.left = 500
        self.top = 200
        self.width = 400
        self.height = 100
        self.iconName = "icon.png"
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(self.iconName))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.CreateLayout()
        vbox = QVBoxLayout()
        vbox.addWidget(self.groupbox)
        self.setLayout(vbox)
        self.show()

    def CreateLayout(self):
        self.groupbox = QGroupBox("What is your favorite sport")
        hboxlayout = QHBoxLayout()
        hboxlayout.addWidget(self.PushButton('futball', 'Soccer'))
        hboxlayout.addWidget(self.PushButton('Tennis', 'Court field'))
        hboxlayout.addWidget(self.PushButton('bascketball', 'Coliseum'))

        self.groupbox.setLayout(hboxlayout)

    def PushButton(self, name, tip):
        button = QPushButton(name, self)
        button.setIcon(QtGui.QIcon("icon.png"))
        button.setIconSize(QtCore.QSize(40, 40))
        button.setToolTip(tip)
        return button


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
