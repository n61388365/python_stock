import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox
from PyQt6.QtCore import QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QComboBox 输入框点击全选并复制 + Enter 信号")
        self.resize(300, 100)

        # 创建 QComboBox 并设置为可编辑
        self.combo_box = QComboBox(self)
        self.combo_box.setGeometry(50, 30, 200, 30)
        self.combo_box.setEditable(True)  # 必须设置为可编辑
        self.combo_box.addItems(["选项1", "选项2", "选项3"])  # 添加下拉选项
        self.combo_box.setCurrentText("示例文本")  # 设置默认文本

        # 获取 QComboBox 的 QLineEdit
        self.stock_input = self.combo_box.lineEdit()

        # 安装事件过滤器以捕获鼠标点击
        self.stock_input.installEventFilter(self)

        # 连接 Enter 键信号
        self.stock_input.returnPressed.connect(self.update_data)

    def eventFilter(self, obj, event):
        # 捕获 QLineEdit 的鼠标按下事件
        if obj == self.stock_input and event.type() == QEvent.Type.MouseButtonPress:
            # 全选文本
            self.stock_input.selectAll()
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            if self.stock_input.selectedText():  # 仅复制非空文本
                clipboard.setText(self.stock_input.selectedText())
                QMessageBox.information(self, "提示", "文本已复制到剪贴板！")
            return True  # 表示事件已处理
        return super().eventFilter(obj, event)

    def update_data(self):
        # 处理 Enter 键按下的逻辑
        text = self.stock_input.text()
        QMessageBox.information(self, "Enter 按下", f"输入内容: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())