from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QGridLayout
from PyQt6.QtCore import Qt


class IndexedPushButton(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.row = 0
        self.column = 0
        self.text = ""


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setGeometry(700, 200, 600, 450)    #set up window
        self.setWindowTitle('Cast list')
        grid = QGridLayout()                    # and layout
        # create an empty 3-column table, no grid lines or vertical header
        self.castTable = QTableWidget(0, 4, self)
#        self.castTable.verticalHeader().setVisible(False)                   #
        self.castTable.setShowGrid(False)
        # table headers
        grid.addWidget(self.castTable, 0, 0, 5, 1)
        columns = ["Frname", "Lname", "Role", "Delete"]
        self.castTable.setHorizontalHeaderLabels(columns)
        # self.castTable.horizontalHeader().font()
        # column widths

        self.castTable.setColumnWidth(0, 100)
        self.castTable.setColumnWidth(1, 150)
        self.castTable.setColumnWidth(2, 150)
        self.castTable.setColumnWidth(3, 50)

        # add 3 rows
        names = ["Edwin", "Rodridguez", "Marco"]
        self.loadTable(0, names)
        names = ["Mike", "Costantino", "Guiseppe"]
        self.loadTable(1, names)
        names = ["John", "Matilaine", "Don Alhambra"]
        self.loadTable(2, names)

        # set the layout and show the table
        self.setLayout(grid) 
        
        for row in range(self.castTable.rowCount()):                        # 
            print(f'row={row}, rowHeight={self.castTable.rowHeight(row)}')  # 
        
    def loadTable(self, row, names):
        row = self.castTable.rowCount()
        riter = iter(names)
        self.castTable.insertRow(row)
        #self.castTable.verticalHeader().setDefaultSectionSize(8)

        self.castTable.setItem(row, 0, QTableWidgetItem(next(riter)))
        self.castTable.setItem(row, 1, QTableWidgetItem(next(riter)))
        self.castTable.setItem(row, 2, QTableWidgetItem(next(riter)))
        idxButton = IndexedPushButton("delete")
        idxButton.row = row
        idxButton.column = 3
        idxButton.text = "delete row {}".format(row)
        idxButton.clicked.connect(self.onClick)
        self.castTable.setCellWidget(row, 3, idxButton)
        
        print(f'row = {(row+1) * 8}')                                        # 
        self.castTable.setRowHeight(row, (row+1) * 8)                        # +++
#        setRowHeight
#        self.castTable.resizeRowsToContents()                               # ---

    def onClick(self):
        print(self.sender().row, self.sender().column)
        self.castTable.removeRow(self.sender().row)
        # 重新设置button的row
        for idx in range(self.castTable.rowCount()):
            self.castTable.cellWidget(idx, 3).row = idx


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')                                                   # +++
    Form = MainWindow() 
    Form.show()
    sys.exit(app.exec())