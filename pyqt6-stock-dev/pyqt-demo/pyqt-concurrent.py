## https://www.pythonguis.com/tutorials/multithreading-pyqt6-applications-qthreadpool/

import time

from PyQt6.QtCore import (
    QTimer,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

        layout = QVBoxLayout()

        self.label = QLabel("Start")
        button_start = QPushButton('Start')
        button_start.pressed.connect(self.timer_start)
        button_stop = QPushButton('Stop')
        button_stop.pressed.connect(self.timer_stop)
        button = QPushButton("DANGER!")
        button.pressed.connect(self.oh_no)

        layout.addWidget(self.label)
        layout.addWidget(button_start)
        layout.addWidget(button_stop)
        layout.addWidget(button)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.show()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)

    def oh_no(self):
        time.sleep(5)

    def timer_start(self):
        self.timer.start()

    def timer_stop(self):
        self.timer.stop()

    def recurring_timer(self):
        self.counter += 1
        self.label.setText(f"Counter: {self.counter}")

app = QApplication([])
window = MainWindow()
app.exec()