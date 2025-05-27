import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QHBoxLayout, QWidget, QTableWidgetItem
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

        # 创建左侧窄表格，固定宽度
        left_table = QTableWidget()
        left_table.setColumnCount(2)
        left_table.setRowCount(10)
        left_table.setHorizontalHeaderLabels(['ID', 'Name'])
        left_table.setMinimumWidth(200)  # 最小宽度
        left_table.setMaximumWidth(200)  # 最大宽度，防止调整
        left_table.setSizePolicy(left_table.sizePolicy().horizontalPolicy(), left_table.sizePolicy().verticalPolicy())  # 默认大小策略

        # 创建右侧宽表格
        right_table = QTableWidget()
        right_table.setColumnCount(4)
        right_table.setRowCount(10)
        right_table.setHorizontalHeaderLabels(['Column1', 'Column2', 'Column3', 'Column4'])

        # 添加表格到布局
        layout.addWidget(left_table)
        layout.addWidget(right_table)

        # 设置拉伸因子，使右侧表格占据更多空间
        layout.setStretch(0, 0)  # 左侧表格不拉伸
        layout.setStretch(1, 1)  # 右侧表格拉伸以填充剩余空间

        # 设置表格内容示例
        for row in range(10):
            left_table.setItem(row, 0, QTableWidgetItem(f"ID{row}"))
            left_table.setItem(row, 1, QTableWidgetItem(f"Name{row}"))
            for col in range(4):
                right_table.setItem(row, col, QTableWidgetItem(f"Data{row}-{col}"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())