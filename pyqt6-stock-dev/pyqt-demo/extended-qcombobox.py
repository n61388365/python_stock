from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QApplication, QCompleter
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtCore import QSortFilterProxyModel, Qt, pyqtSignal
import sys

# 带搜索功能的下拉框
class ExtendedComboBox(QComboBox):

    enterPressed = pyqtSignal(object)

    def keyReleaseEvent(self, event):
        # 回车键
        if event.key() == 16777220:
            self.enterPressed.emit(self)

    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)
        # self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # 添加筛选器模型来筛选匹配项
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # 大小写不敏感
        self.pFilterModel.setSourceModel(self.model())

        # 添加一个使用筛选器模型的QCompleter
        self.completer = QCompleter(self.pFilterModel, self)
        # 始终显示所有(过滤后的)补全结果
        self.completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # 不区分大小写
        self.setCompleter(self.completer)

        # Qcombobox编辑栏文本变化时对应的槽函数3
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # 当在Qcompleter列表选中候，下拉框项目列表选择相应的子项目
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            # self.activated[str].emit(self.itemText(index))

    # 在模型更改时，更新过滤器和补全器的模型
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # 在模型列更改时，更新过滤器和补全器的模型列
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)

    # 回应回车按钮事件
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return:
            text = self.currentText()
            index = self.findText(text, Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive)
            self.setCurrentIndex(index)
            self.hidePopup()
            super(ExtendedComboBox, self).keyPressEvent(e)
        else:
            super(ExtendedComboBox, self).keyPressEvent(e)

    def eventFilter(self, a0, a1):
        print('a0:', a0, 'a1:', a1)
        return super().eventFilter(a0, a1)


def run():
    app = QApplication(sys.argv)
    win = ExtendedComboBox()
    win.enterPressed.connect(enterPressed)
    l = ["", "1aew","2asd","3ewqr","3ewqc","2wqpu","1kjijhm", "4kjndw", "5ioijb","6eolv", "11ofmsw"]
    input_file = 'pyqt-demo\A股_with_pinyin.csv'
    with open(input_file, 'r', encoding="utf-8") as f:
        l = [line.rstrip() for line in f]
        print(l)
    win.addItems(l)
    win.show()
    sys.exit(app.exec())

def enterPressed(self :ExtendedComboBox):
    print(self.sender().currentText())


if __name__ == '__main__':
    run()