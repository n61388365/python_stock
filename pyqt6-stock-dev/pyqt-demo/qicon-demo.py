# https://muzing.top/posts/75a2283d/#%E4%BD%BF%E7%94%A8-rcc-%E7%BC%96%E8%AF%91%E8%B5%84%E6%BA%90
# rcc编译资源文件

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuitka 示例")
        self.setWindowIcon(QIcon(".\stock.ico"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
