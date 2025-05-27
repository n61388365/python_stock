import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QStyleFactory, QHBoxLayout
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Two Tables Layout")
        self.setMinimumSize(800, 400)

        # 创建主窗口的中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.bar_yesterday = QProgressBar()
        self.bar_yesterday.setMaximum(50)
        self.bar_yesterday.setMinimum(0)
        self.bar_yesterday.setValue(50)
        self.bar_yesterday.setFormat('%v')
        self.bar_yesterday.setStyle(QStyleFactory.create('windowsvista'))

        self.bar_today = QProgressBar()
        self.bar_today.setMaximum(200)
        self.bar_today.setMinimum(0)
        self.bar_today.setValue(40)
        self.bar_today.setFormat('%v')
        self.bar_today.setStyle(QStyleFactory.create('windowsvista'))

        layout.addWidget(self.bar_yesterday)
        layout.addWidget(self.bar_today)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())