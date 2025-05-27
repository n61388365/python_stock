import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDial,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QSpinBox,
)


class MyComboBox(QComboBox):

    enterPressed = pyqtSignal()

    def __init__(self):
        super(MyComboBox,self).__init__()

    def keyReleaseEvent(self, event):
        # 回车键
        if event.key() == 16777220:
            self.enterPressed.emit()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        widget = MyComboBox()
        widget.addItems(["One", "Two", "Three"])

        # Sends the current index (position) of the selected item.
        widget.currentIndexChanged.connect( self.index_changed )

        # There is an alternate signal to send the text.
        widget.currentTextChanged.connect( self.text_changed )

        widget.enterPressed.connect(self.hello)

        self.setCentralWidget(widget)


    def index_changed(self, i): # i is an int
        print(i)

    def text_changed(self, s): # s is a str
        print(s)
    
    def hello(self):
        print("I am here waiting for you")


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()