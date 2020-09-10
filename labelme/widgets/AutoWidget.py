from PyQt5.QtWidgets import QWidget, QButtonGroup, QPushButton, QDialog, QMainWindow, QApplication, QGroupBox, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel, QSlider
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5"
        self.top = 100
        self.left = 100
        self.width = 400
        self.height = 300
        self.iconName = "/home/israel/repos/labelme/experimental/icon.png"
        self.initWindow()

    def initWindow(self):
        # self.setWindowIcon(QtGui.QIcon(self.iconName))
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        # self.createButtons()
        # self.label.setFont(QtGui.QFont('Sanserif',15))


        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.buttonsbox = QGroupBox("Predict:")
        self.buttongroup = QButtonGroup()
        # self.buttongroup.buttonClicked[int].connect(self.on_button_clicked)
        but1 = self.buttons('Classification')
        but2 = self.buttons('BoudingBox')
        but3 = self.buttons('Segmentation',True)
        self.buttongroup.addButton(but1, 1)
        self.buttongroup.addButton(but2, 2)
        self.buttongroup.addButton(but3, 3)
        hbox.addWidget(but1)
        hbox.addWidget(but2)
        hbox.addWidget(but3)
        self.buttonsbox.setLayout(hbox)
        vbox.addWidget(self.buttonsbox)


        self.settingsbox = QGroupBox("Settings:")
        vbox_settings = QVBoxLayout()
        self.slider_object1 = class_Slider('Threshold')
        self.slider_object2 = class_Slider('Threshold2', 20, 1, 10)

        vbox_settings.addLayout(self.slider_object1.group())
        vbox_settings.addLayout(self.slider_object2.group())
        self.settingsbox.setLayout(vbox_settings)
        vbox.addWidget(self.settingsbox)

        self.btn = QPushButton('Predict')
        self.btn.clicked.connect(self.inference)
        vbox.addWidget(self.btn)

        self.setLayout(vbox)

        self.label = QLabel()
        vbox.addWidget(self.label)

        self.show()


    def buttons(self, text, is_checked = False):
        button = QRadioButton(text, self)
        button.setChecked(is_checked)
        # button.setIcon(QtGui.QIcon("icon.png"))
        button.setToolTip("This is click me button")
        return button

    def inference(self):
        print('The following configuration has been chosen\n')
        print('Label type: ' + str(self.buttongroup.checkedId()))
        print('Th1: '+ str(self.slider_object1.slider.value()))
        print('Th2: '+ str(self.slider_object2.slider.value()))

class class_Slider(QSlider, QLabel):
    def __init__(self, label, max=100, min=0, value=50):
        super(class_Slider, self).__init__()
        self.slider = QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        # self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.setTickInterval((max-min)/10)
        self.slider.setMaximum(max)
        self.slider.setMinimum(min)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self.change)
        self.label_slider = QLabel(label)
        self.value_slider = QLabel("{:.2f}".format((self.slider.value()/100)))
        self.value_slider.setAlignment(Qt.AlignCenter)

    def change(self):
        size = self.slider.value()/100
        self.value_slider.setText("{:.2f}".format(size))

    def group(self):
        set1 = QHBoxLayout()
        # self.slider_object = class_Slider()
        set1.addWidget(self.label_slider)
        set1.addWidget(self.slider)
        set1.addWidget(self.value_slider)
        self.value_slider.setAlignment(Qt.AlignCenter)
        return set1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
