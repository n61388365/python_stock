############################################
## update
## 2025-04-25 周五 股票代码可输入可选择
## 2025-04-27 周日 添加回车处理
##                      减成两个单元
## 2025-05-05 周一 添加A股全列表
## 2025-05-06 周二 自动更新
##                      添加盘口表挂单
## 2025-05-10 周六 添加窗口图标
##                      命令行参数
## 2025-05-16 周五 增加减少挂单
##                      调整宽度
## 2025-05-17 周六 起始时间功能
## 2025-05-18 周日 窗口 title 自适应
## 2025-05-20 周二 移除 挂买单 挂卖单 价格 （基本上没用过）
## 2025-05-28 周三 从文件中读取股票列表
## 2025-06-13 周五 【bug fix】涨跌停和收盘时的盘口显示
## 2025-06-21 周六 【new feature】挂单表排序
## 2025-06-24 周二 增加eastmoney timeout
## 2025-06-26 周四 【bug fix】删除更新错误在排序后
## 2025-10-10 周五 【new feature】添加 proxy 选项
## 2025-10-14 周二 【new feature】两个 api 独立设置 proxy 选项
############################################

# import subprocess
import json
import sys
import pandas as pd
import time
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QHeaderView,
    QGridLayout,
    QCheckBox,
    QComboBox,
    QAbstractItemView,
    QCompleter,
    QMessageBox
)
from PyQt6.QtCore import (Qt, pyqtSignal, QSortFilterProxyModel, QTimer, QEvent)
from PyQt6.QtGui import (QBrush, QColor, QIcon)
import urllib.request as urlrequest
import datetime
import log
import compiled_resources
from utils import file_utils
import traceback


log.setLevel(20) # 10 debug 20 info


# CREATE_NO_WINDOW = 0x08000000
default_proxy_host = 'localhost:7789'
global_timer = 4000
sell_rows = [('f31', 'f32'), ('f33', 'f34'), ('f35', 'f36'), ('f37', 'f38'), ('f39', 'f40')]
buy_rows = [('f19', 'f20'), ('f17', 'f18'), ('f15', 'f16'),  ('f13', 'f14'), ('f11','f12')]


class MyComboBox(QComboBox):

    # enterPressed = pyqtSignal()

    def __init__(self):
        super().__init__()
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
        self.installEventFilter(self)
    # 当在Qcompleter列表选中候，下拉框项目列表选择相应的子项目
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            # self.activated[str].emit(self.itemText(index))

    # 在模型更改时，更新过滤器和补全器的模型
    def setModel(self, model):
        super(MyComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # 在模型列更改时，更新过滤器和补全器的模型列
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(MyComboBox, self).setModelColumn(column)

    # 回应回车按钮事件
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return:
            text = self.currentText()
            index = self.findText(text, Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive)
            self.setCurrentIndex(index)
            self.hidePopup()
            super(MyComboBox, self).keyPressEvent(e)
        else:
            super(MyComboBox, self).keyPressEvent(e)


class IndexedPushButton(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.row = 0
        self.column = 0
        self.price = 0


class TradeBlock(QWidget):
    def __init__(self, parent=None, stock=""):
        super().__init__(parent)
        self.fallback_data = {
            'Time': [92500, 93000, 93003, 93006, 93009],
            'Price': [3.84, 3.84, 3.85, 3.84, 3.85],
            'Metric': [1,2,3,4,5],
            'Volume': [5368, 1049, 11248, 3251, 2817],
            'Type': ['1', '2', '4', '2', '1']
        }
        self.df = pd.DataFrame(self.fallback_data)
        self.order_book = None
        self.result = None
        self.bid_price = 0
        self.bid_volumn = 0
        self.bid_time = datetime.datetime.now().strftime('%H:%M:%S')

        self.analyze_timer = QTimer()
        self.analyze_timer.setInterval(global_timer)
        self.analyze_timer.timeout.connect(self.analyze_data)

        self.order_book_timer = QTimer()
        self.order_book_timer.setInterval(global_timer)
        self.order_book_timer.timeout.connect(self.update_order_book)

        # Block layout
        self.layout = QVBoxLayout(self)

        # Input and button layout
        self.input_layout = QHBoxLayout()
        self.stock_label_name = QLabel('股票名称')
        self.stock_label_name.setFixedWidth(48)
        self.stock_label_name.setStyleSheet("color: yellow;")
        if stock:
            self.stock_label_name.setText(stock.split(',')[1])
        self.stock_input = MyComboBox()
        self.stock_input.addItems(file_utils.get_combobox_list())
        self.stock_input.setCurrentText(stock)
        self.stock_input.setEditable(True)
        self.stock_input.setMinimumWidth(80)
        self.stock_input.currentIndexChanged.connect(self.combobox_index_changed)
        # QComboBox 的 QLineEdit
        self.stock_input_line_edit = self.stock_input.lineEdit()
        # 安装 event filter
        self.stock_input_line_edit.installEventFilter(self)

        # 挂间时间
        self.label = QLabel("实时")
        self.label.setMidLineWidth(25)
        self.time_input = QLineEdit()
        self.time_input.mousePressEvent = self.line_edit_select_all_and_copy
        self.time_input.setMinimumWidth(50)
        self.time_input.setPlaceholderText("例如: 150800")
        self.time_input.setText(str(93000))
        # 使用代理
        self.proxy_checkbox_label = QLabel('代理')
        self.proxy_checkbox = QCheckBox()
        self.proxy_checkbox.setCheckState(Qt.CheckState.Unchecked)        
        self.proxy_port_label = QLabel("端口")
        self.proxy_port_label.setMinimumWidth(25)
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setFixedWidth(50)
        # 成交汇总 + 挂单分析
        self.analyze_button = QPushButton("挂单分析")
        self.analyze_button.setCheckable(True)
        self.analyze_button.clicked.connect(self.analyze_data_timer)
        # 自动更新
        self.analyze_checkbox_label = QLabel('自动')
        self.analyze_checkbox = QCheckBox()
        self.analyze_checkbox.setCheckState(Qt.CheckState.Unchecked)
        # 盘口更新按钮
        self.update_order_book_button = QPushButton("盘口更新")
        self.update_order_book_button.setCheckable(True)
        self.update_order_book_button.clicked.connect(self.update_order_book_timer)

        self.input_layout.addWidget(self.stock_label_name)
        self.input_layout.addWidget(self.stock_input)
        self.input_layout.addWidget(self.label)
        self.input_layout.addWidget(self.time_input)
        self.input_layout.addWidget(self.proxy_checkbox_label)
        self.input_layout.addWidget(self.proxy_checkbox)
        self.input_layout.addWidget(self.proxy_port_label)
        self.input_layout.addWidget(self.proxy_port_input)
        self.input_layout.addWidget(self.analyze_button)
        self.input_layout.addWidget(self.update_order_book_button)
        self.input_layout.addWidget(self.analyze_checkbox_label)
        self.input_layout.addWidget(self.analyze_checkbox)
        self.layout.addLayout(self.input_layout)

        # Tables layout (side by side)
        self.tables_layout = QHBoxLayout()

        # Tables layout 左布局
        self.left_layout = QVBoxLayout()

        # Tables layout 左上 挂单列表
        self.bid_table = QTableWidget(0, 9)
        self.bid_table.setHorizontalHeaderLabels(['时间', '价格', '买卖', '数量', '成交', '余额', '盘口', '撤单', '删除'])
        self.bid_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.bid_table.setAlternatingRowColors(True)
        self.bid_table.horizontalHeader().setMinimumSectionSize(50)
        self.bid_table.horizontalHeader().setFixedHeight(24)
        self.bid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bid_table.setFixedHeight(118)
        self.bid_table.setMinimumWidth(450)  # Ensure visibility
        self.bid_table.verticalHeader().setVisible(False)
        self.bid_table.setSortingEnabled(True)
        self.bid_table.sortItems(0,Qt.SortOrder.AscendingOrder)
        self.left_layout.addWidget(self.bid_table)

        # Tables layout 左中 水平而已 时间输入
        self.summary_time_layout = QHBoxLayout()
        self.summary_status_label = QLabel('无数据')
        self.summary_status_label.setMinimumWidth(240)
        self.start_time_label = QLabel('起')
        self.start_time_input = QLineEdit()
        self.start_time_input.returnPressed.connect(self.analyze_data)
        self.start_time_input.mousePressEvent = self.start_time_input_mouse_pressed
        self.end_time_label = QLabel('止')
        self.end_time_input = QLineEdit()
        self.end_time_input.returnPressed.connect(self.analyze_data)
        self.end_time_input.mousePressEvent = self.end_time_input_mouse_pressed
        self.summary_time_layout.addWidget(self.summary_status_label)
        self.summary_time_layout.addWidget(self.start_time_label)
        self.summary_time_layout.addWidget(self.start_time_input)
        self.summary_time_layout.addWidget(self.end_time_label)
        self.summary_time_layout.addWidget(self.end_time_input)
        self.left_layout.addLayout(self.summary_time_layout)

        # Tables layout 左下
        self.result_layout = QHBoxLayout()
        # Tables layout 左下左 汇总 data table
        self.result_table = QTableWidget()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['时间', '价格', '成交量', '类型'])
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.horizontalHeader().setFixedHeight(24)
        self.result_table.horizontalHeader().setMinimumSectionSize(50)
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.result_table.setColumnWidth(0, 50)
        self.result_table.setFixedHeight(118)
        self.result_table.setMinimumWidth(200)  # Ensure visibility
        self.result_layout.addWidget(self.result_table)
        # Tables layout 左下右
        self.detail_table = QTableWidget()
        self.detail_table.setRowCount(0)
        self.detail_table.setColumnCount(4)
        self.detail_table.setFixedHeight(118)
        self.detail_table.setHorizontalHeaderLabels(['时间', '价格', '数量', '买卖'])
        self.detail_table.horizontalHeader().setFixedHeight(0)
        self.detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.detail_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.detail_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.detail_table.setColumnWidth(0, 50)
        self.detail_table.setColumnWidth(3, 50)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.result_layout.addWidget(self.detail_table)
        self.left_layout.addLayout(self.result_layout)
        self.left_layout.setSpacing(4)
        self.tables_layout.addLayout(self.left_layout)

        # Tables layout 右 Order book table
        self.order_book_container = QVBoxLayout()
        # Tables layout 右上 卖盘列表
        self.order_book_sell_table = QTableWidget()
        self.order_book_sell_table.setRowCount(5)
        self.order_book_sell_table.setColumnCount(3)
        self.order_book_sell_table.setHorizontalHeaderLabels(['价格', '总数','挂单'])
        self.order_book_sell_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.order_book_sell_table.setAlternatingRowColors(True)
        self.order_book_sell_table.horizontalHeader().setFixedHeight(24)
        self.order_book_sell_table.horizontalHeader().setMinimumSectionSize(50)
        self.order_book_sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_book_sell_table.setFixedHeight(141)
        self.order_book_sell_table.setMinimumWidth(200)
        self.order_book_sell_table.setVerticalHeaderLabels(['卖五', '卖四', '卖三', '卖二', '卖一'])
        self.order_book_sell_table.verticalHeader().setDefaultSectionSize(12)
        self.order_book_sell_table.setShowGrid(False)
        # Tables layout 右下 买盘列表
        self.order_book_buy_table = QTableWidget()
        self.order_book_buy_table.setRowCount(5)
        self.order_book_buy_table.setColumnCount(3)
        self.order_book_buy_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.order_book_buy_table.setAlternatingRowColors(True)
        self.order_book_buy_table.setHorizontalHeaderLabels(['价格', '总数','挂单'])
        self.order_book_buy_table.horizontalHeader().setFixedHeight(0)
        self.order_book_buy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_book_buy_table.setFixedHeight(117)
        self.order_book_buy_table.setVerticalHeaderLabels(['买一', '买二', '买三', '买四', '买五'])
        self.order_book_container.addWidget(self.order_book_sell_table)
        self.order_book_container.addWidget(self.order_book_buy_table)
        self.tables_layout.addLayout(self.order_book_container)

        self.layout.addLayout(self.tables_layout)

        # Display initial data
        self.display_raw_data()
        self.display_order_book()

    def get_realtime_ticks(self, stock_code):
        log.info('loading trading details')
        # 深证 0. + 000750，上证 1. + 601568
        stock_code = stock_code.startswith('6') and '1.{}'.format(stock_code) or '0.{}'.format(stock_code)
        url = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secid={}'.format(stock_code)
        req = urlrequest.Request(url)
        if self.proxy_checkbox.isChecked():
            proxy_port = self.proxy_port_input.text()
            proxy_host = default_proxy_host
            if proxy_port:
                proxy_host = f"localhost:{proxy_port}"
            log.info(f'set proxy to port {proxy_host}')
            req.set_proxy(proxy_host, 'http')
            
        with urlrequest.urlopen(req,timeout=3) as r:
            data = r.readline().decode().lstrip('data:')
            data_json = json.loads(data)
            log.debug(data_json['data'])
            return data_json['data']


    def get_today_ticks(self, stock_code='000750'):

        if stock_code.startswith('6'):
            stock_code = "1.{}".format(stock_code)
        else:
            stock_code = "0.{}".format(stock_code)
        url='http://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&pos=-0&secid={}'.format(stock_code)
        # get data from eastmoney
        log.info('loading 盘口')

        req = urlrequest.Request(url)
        if self.proxy_checkbox.isChecked():
            proxy_port = self.proxy_port_input.text()
            proxy_host = default_proxy_host
            if proxy_port:
                proxy_host = f"localhost:{proxy_port}"
            log.info(f'set proxy to port {proxy_host}')
            req.set_proxy(proxy_host, 'http')        

        with urlrequest.urlopen(req,timeout=3) as r:
            data=r.readline().decode().lstrip('data:')
            data_json = json.loads(data)
            log.debug(data_json['data']['details'])
        # Convert data to DataFrame
        df = pd.DataFrame([row.split(',') for row in data_json['data']['details']], 
                        columns=['Time', 'Price', 'Volume', 'Metric', 'Type'])
        # Convert columns to appropriate types
        df['Time'] = df['Time'].map(lambda x: str(x).zfill(6))
        df['Price'] = df['Price'].astype(float)
        df['Volume'] = df['Volume'].astype(int)
        df['Metric'] = df['Metric'].astype(int)
        df['Type'] = df['Type'].astype(str)
        log.debug(df.dtypes)

        # Convert time from HH:MM:SS to HHMM
        try:
            df['Time'] = df['Time'].str.replace(':', '').astype(int)
        except Exception as e:
            raise ValueError(f"时间格式转换失败: {str(e)}")

        return df


    def combobox_lineedit_enter_pressed(self):
        print(self.stock_input_line_edit.text())

    def start_time_input_mouse_pressed(self, event):
        self.start_time_input.selectAll()

    def end_time_input_mouse_pressed(self, event):
        self.end_time_input.selectAll()

    def combobox_index_changed(self):
        if not self.stock_input.currentText():
            log.error('股票代码不能为空')
            self.stock_label_name.setText('股票名称')
            return
        stock_name = self.stock_input.currentText().split(',')[1]
        self.stock_label_name.setText(stock_name)
        # 股票更新后重新设置窗口标题
        stock_name_list = [ trade_block.stock_label_name.text() for trade_block in self.parent().parent().children()[1].children()[1:]]
        self.parent().parent().setWindowTitle(" ".join(stock_name_list))
        self.update_data()

    def eventFilter(self, obj, event):
        # 捕获 QLineEdit 的鼠标按下事件
        if obj == self.stock_input_line_edit and event.type() == QEvent.Type.MouseButtonPress:
            # 全选文本
            self.stock_input_line_edit.selectAll()
            return True  # 表示事件已处理
        return super().eventFilter(obj, event)

    def line_edit_select_all_and_copy(self, event):
        self.time_input.selectAll()
        if self.time_input.selectedText():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.time_input.selectedText())
            msg = QMessageBox(self)
            msg.setWindowTitle('郑重提示')
            msg.setText('时间已复制到剪贴板！')
            msg.setIconPixmap(QIcon(':icons/Icons/information.png').pixmap(16,16))
            msg.exec()

    def update_detail_table_view(self):
        self.detail_table.setColumnCount(4)
        self.detail_table.setRowCount(len(self.df.tail(5)))
        for row_idx, row in enumerate(self.df.tail(5).iterrows()):
            str_time = str(row[1]['Time']).zfill(5)
            itemTime = QTableWidgetItem(f"{str_time[:2]}:{str_time[2:4]}")
            itemPrice = QTableWidgetItem(f"{row[1]['Price']:.2f}")
            if self.order_book:
                itemPrice.setForeground(QBrush(self.price_color_choose(row[1]['Price'],self.order_book['f60'])))
            if row[1]['Type'] == '1':
                itemVol = QTableWidgetItem(str(row[1]['Volume'])+' 🠋')
                itemVol.setForeground(QBrush(QColor(0,255,0)))
            if row[1]['Type'] == '2':
                itemVol = QTableWidgetItem(str(row[1]['Volume'])+' 🠉')
                itemVol.setForeground(QBrush(QColor(255,0,0)))
            if row[1]['Type'] == '4':
                itemVol = QTableWidgetItem(str(row[1]['Volume'])+' 🢀')
                itemVol.setForeground(QBrush(QColor(100,100,100)))
            
            itemVol.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            itemMetric = QTableWidgetItem(str(row[1]['Metric']))
            itemMetric.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            itemMetric.setForeground(QBrush(QColor(125,125,255)))
            self.detail_table.setItem(row_idx, 0, itemTime)
            self.detail_table.setItem(row_idx, 1, itemPrice)
            self.detail_table.setItem(row_idx, 2, itemVol)
            self.detail_table.setItem(row_idx, 3, itemMetric)
            self.detail_table.setRowHeight(row_idx, 9)
        self.detail_table.viewport().update()

    def update_order_book_timer(self):
        if not self.analyze_checkbox.isChecked():
            self.update_order_book_button.setChecked(False)
            self.update_order_book()
            self.order_book_timer.stop()
            return
        if self.update_order_book_button.isChecked():
            self.update_order_book()
            self.order_book_timer.start()
        else:
            self.order_book_timer.stop()

    def analyze_data_timer(self):
        if not self.analyze_checkbox.isChecked():
            self.analyze_button.setChecked(False)
            self.analyze_data()
            self.analyze_timer.stop()
            return
        if self.analyze_button.isChecked():
            self.analyze_data()
            self.analyze_timer.start()
        else:
            self.analyze_timer.stop()

    def get_volume_by_price_type(self, bid_price, bid_type):
        try:
            if bid_type: # 卖单
                for price_idx, volume_idx in sell_rows:
                    if float(self.order_book[price_idx]) == bid_price:
                        return self.order_book[volume_idx]
                return "0"
            for price_idx, volume_idx in buy_rows:
                if float(self.order_book[price_idx]) == bid_price:
                    return self.order_book[volume_idx]
        except:
            traceback.format_exc()
        return "0"

    def update_bid_table_order_volume(self):
        '''
        实时更新挂单价盘口委买卖量
        '''
        #### 遍历 bid table ####
        if not self.bid_table.rowCount():
            log.info("No bid record in talbe")
            return
        for row_idx in range(self.bid_table.rowCount()):
            bid_price = float(self.bid_table.item(row_idx,1).text())
            bid_type = self.bid_table.item(row_idx,2).text() == '卖单' # 1-卖单 0-买单
            item = QTableWidgetItem(str(self.get_volume_by_price_type(bid_price, bid_type)))
            item.setForeground(QBrush(bid_type and QColor(255,0,0) or QColor(0,255,0)))
            self.bid_table.setItem(row_idx, 6, item)
        self.bid_table.viewport().update()

    def price_color_choose(self,price_current, price_yesterday_close):
        # 等于昨天收盘价，白色
        if price_current == price_yesterday_close:
            return QColor(255,255,255)
        # 高于昨天收盘价，红色
        if price_current > price_yesterday_close:
            return QColor(255,0,0)
        # 低于昨天收盘价，绿色
        if price_current < price_yesterday_close:
            return QColor(0,255,0)

    def get_order_vol_by_price(self, bid_price):

        for price_col, vol_col in sell_rows:
            try:
                price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
                volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
                if price == float(bid_price):
                    return volume
            except:
                continue
        for price_col, vol_col in buy_rows:
            try:
                price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
                volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
                if price == float(bid_price):
                    return volume
            except:
                continue
        return 0

    def add_bid_table(self, checked, bid_type, price):
        '''
        params: bid_type 1 卖单 0 买单
        '''
        log.info("I am add bid table function")
        self.bid_table.setSortingEnabled(False)
        if not self.order_book:
            return
        row_idx = self.bid_table.rowCount()
        self.bid_table.insertRow(row_idx)
        # volumn 0 挂单时间
        timeItem = QTableWidgetItem(self.time_input.text())
        timeItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        timeItem.setBackground(QBrush(QColor(0,0,0)))
        # volumn 1 挂单价格
        priceItem = QTableWidgetItem(price)
        priceItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # priceItem.setBackground(QBrush(QColor(0,0,0)))
        priceItem.setForeground(QBrush(self.price_color_choose(float(price),self.order_book['f60'])))
        # volumn 2 挂单类型
        sell_or_buy = bid_type and '卖单' or '买单'
        color = bid_type and QColor(255,0,0) or QColor(0,255,0)
        sellOrBuyItem = QTableWidgetItem(sell_or_buy)
        sellOrBuyItem.setForeground(QBrush(color))
        sellOrBuyItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # volumn 3 挂单数量
        volumnItem = QTableWidgetItem(str(self.get_order_vol_by_price(price)))
        volumnItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # volumnItem.setBackground(QBrush(QColor(0,0,0)))
        volumnItem.setForeground(QBrush(QColor(255,255,0)))
        # volumn 4 成交量
        completedItem = QTableWidgetItem(str(self.bid_volumn))
        completedItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bid_table.setItem(row_idx,1,priceItem)
        self.bid_table.setItem(row_idx,2,sellOrBuyItem)
        self.bid_table.setItem(row_idx,3,volumnItem)
        self.bid_table.setItem(row_idx,4,completedItem)
        reduceVolumeButton = IndexedPushButton("更新")
        reduceVolumeButton.row = row_idx
        reduceVolumeButton.column = 7
        reduceVolumeButton.clicked.connect(self.onReduceVolumeClick)
        self.bid_table.setCellWidget(row_idx, 7, reduceVolumeButton)
        idxButton = IndexedPushButton("删除")
        idxButton.row = row_idx
        idxButton.column = 8
        idxButton.text = "delete row {}".format(row_idx)
        idxButton.clicked.connect(self.onClick)
        self.bid_table.setCellWidget(row_idx, 8, idxButton)
        self.bid_table.setItem(row_idx,0,timeItem)
        self.bid_table.setRowHeight(row_idx, 16)
        self.bid_table.setSortingEnabled(True)
        self.bid_table.viewport().update()

    def get_completed_vol(self, bid_time, bid_price, bid_type):
        # 根据挂单时间汇总数据
        filtered_df = self.df[self.df['Time'] >= bid_time]
        filtered_df['buy_vol'] = 0
        filtered_df['sell_vol'] = 0
        filtered_df.loc[filtered_df['Type'] == '2', 'buy_vol'] = filtered_df['Volume']
        filtered_df.loc[filtered_df['Type'] == '1', 'sell_vol'] = filtered_df['Volume']
        summary = filtered_df.groupby('Price')[['buy_vol', 'sell_vol']].sum().sort_values('Price',ascending=False).reset_index()

        # 遍历汇总
        for row_idx, row_data in summary.iterrows():
            if row_data['Price'] == bid_price:
                return bid_type and row_data['buy_vol'] or row_data['sell_vol']
        log.info('no bid price {} found'.format(bid_price))
        return 0

    def update_bid_table(self):
        '''
        根据交易明细统计成交量，并计算挂单余额
        '''
        #### 遍历 bid table ####
        if not self.bid_table.rowCount():
            log.info("No bid record in talbe")
            return
        for row_idx in range(self.bid_table.rowCount()):
            bid_time = int(self.bid_table.item(row_idx,0).text())
            bid_price = float(self.bid_table.item(row_idx,1).text())
            bid_type = self.bid_table.item(row_idx,2).text() == '卖单'
            bid_vol = int(self.bid_table.item(row_idx,3).text())
            bid_completed = self.get_completed_vol(bid_time, bid_price, bid_type)
            bid_vol_left = bid_vol - bid_completed
            item = QTableWidgetItem(str(int(bid_completed)))
            item.setForeground(QBrush(bid_type and QColor(255,0,0) or QColor(0,255,0)))
            item.setBackground(QBrush(QColor(0,0,0)))
            self.bid_table.setItem(row_idx, 4, item)
            item = QTableWidgetItem(str(int(bid_vol_left)))
            item.setBackground(QBrush(QColor(0,0,0)))
            self.bid_table.setItem(row_idx, 5, item)
        self.bid_table.viewport().update()

    def onReduceVolumeClick(self):
        try:
            # row = self.sender().row
            row = self.sender().parent().parent().currentRow()
            completed_volume = int(self.bid_table.item(row, 4).text())
            left_volume = int(self.bid_table.item(row, 5).text())
            realtime_order_volume = int(self.bid_table.item(row, 6).text())
            # 实时盘口的委托量低于剩余量，说明有撤单，需要更新挂单数量
            if realtime_order_volume < left_volume:
                self.bid_table.item(row, 3).setText(str(realtime_order_volume+completed_volume))
        except Exception as e:
            log.error(f"Failed to update order volume in bid table. {e}")


    def onClick(self):
        # print(self.sender().row, self.sender().column)
        row = self.sender().parent().parent().currentRow()
        self.bid_table.removeRow(row)
        # 重新设置button的row
        # for idx in range(self.bid_table.rowCount()):
        #     self.bid_table.cellWidget(idx,8).row = idx
        #     self.bid_table.cellWidget(idx,7).row = idx

    def onOrderBookSellClick(self):
        # print(self.sender().row, self.sender().column)
        self.add_bid_table(False, True, f"{self.sender().price:.2f}")

    def onOrderBookBuyClick(self):
        # print(self.sender().row, self.sender().column)
        self.add_bid_table(False, False, f"{self.sender().price:.2f}")

    def display_raw_data(self):
        """Display the raw transaction data in the table (up to 100 rows)."""
        if self.df.empty:
            self.result_table.setRowCount(0)
            self.label.setText("数据为空，请尝试更新")
            log.debug("Debug: DataFrame is empty")
            return

        # Sort data by time ascending and limit to 100 rows
        sorted_df = self.df.sort_values(by='Time')

        # Set table for raw data
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['时间', '价格', '成交量', '类型'])
        self.result_table.setRowCount(len(sorted_df))

        # Populate table with raw data
        for row_idx, row_data in sorted_df.iterrows():
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['Time'])))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(f"{row_data['Price']:.2f}"))
            self.result_table.setItem(row_idx, 2, QTableWidgetItem(str(int(row_data['Volume']))))
            self.result_table.setItem(row_idx, 3, QTableWidgetItem(row_data['Type']))
            self.result_table.setRowHeight(row_idx, 12)

        # Adjust column widths and refresh
        self.result_table.viewport().update()
        log.debug(f"Debug: Displayed {len(sorted_df)} rows in table")

    def display_order_book(self):
        """Display sell 5 to buy 5 order book data."""
        if self.order_book is None:
            for row in range(5):
                item = QTableWidgetItem(str(row))
                item.setBackground(QBrush(QColor(0,0,0)))
                self.order_book_sell_table.setItem(row, 0, item)
                item = QTableWidgetItem(str(row))
                item.setBackground(QBrush(QColor(0,0,0)))
                self.order_book_sell_table.setItem(row, 1, item)
                self.order_book_sell_table.setItem(row, 2, QTableWidgetItem("我是狼"))
                self.order_book_sell_table.setRowHeight(row, 12)
                item = QTableWidgetItem(str(row))
                item.setBackground(QBrush(QColor(0,0,0)))
                self.order_book_buy_table.setItem(row, 0, item)
                item = QTableWidgetItem(str(row))
                item.setBackground(QBrush(QColor(0,0,0)))
                self.order_book_buy_table.setItem(row, 1, item)
                self.order_book_buy_table.setItem(row, 2, QTableWidgetItem("你是羊"))
                self.order_book_buy_table.setRowHeight(row, 12)
            self.order_book_container.update()
            return

        # 昨日收盘价
        yesterday_close = self.order_book['f60']

        self.order_book_sell_table.setRowCount(5)

        # bid_price = self.price_input.text()
        for row_idx, (price_col, vol_col) in enumerate(sell_rows):
            try:
                price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
                volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
            except:
                item = QTableWidgetItem("")
                self.order_book_sell_table.setItem(row_idx,0,item)
                item = QTableWidgetItem("")
                self.order_book_sell_table.setItem(row_idx,1,item)
                item = QTableWidgetItem("")
                self.order_book_sell_table.setItem(row_idx,2,item)
                continue
            # set price color
            item = QTableWidgetItem(f"{price:.2f}" if price else "")
            if price > yesterday_close:
                item.setForeground(QBrush(QColor(255,0,0)))
                item.setBackground(QBrush(QColor(0,0,0)))
            if price == yesterday_close:
                item.setForeground(QBrush(QColor(255,255,255)))
                item.setBackground(QBrush(QColor(0,0,0)))
            if price < yesterday_close:
                item.setForeground(QBrush(QColor(0,255,0)))
                item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_sell_table.setItem(row_idx, 0, item)

            # volume color yellow
            item = QTableWidgetItem(str(volume) if volume else "")
            item.setForeground(QBrush(QColor(255,255,0)))
            self.order_book_sell_table.setItem(row_idx, 1, item)

            idx_button = IndexedPushButton('挂卖单')
            idx_button.row = row_idx
            idx_button.column = 2
            idx_button.price = price
            idx_button.pressed.connect(self.onOrderBookSellClick)
            self.order_book_sell_table.setCellWidget(row_idx, 2, idx_button)

        self.order_book_buy_table.setRowCount(5)
        for row_idx, (price_col, vol_col) in enumerate(buy_rows):
            try:
                price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
                volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
            except:
                item = QTableWidgetItem("")
                self.order_book_buy_table.setItem(row_idx,0,item)
                item = QTableWidgetItem("")
                self.order_book_buy_table.setItem(row_idx,1,item)
                item = QTableWidgetItem("")
                self.order_book_buy_table.setItem(row_idx,2,item)
                continue
            # set price color
            item = QTableWidgetItem(f"{price:.2f}" if price else "")
            if price > yesterday_close:
                item.setForeground(QBrush(QColor(255,0,0)))
                item.setBackground(QBrush(QColor(0,0,0)))
            if price == yesterday_close:
                item.setForeground(QBrush(QColor(255,255,255)))
                item.setBackground(QBrush(QColor(0,0,0)))
            if price < yesterday_close:
                item.setForeground(QBrush(QColor(0,255,0)))
                item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_buy_table.setItem(row_idx, 0, item)

            # volume color yellow
            item = QTableWidgetItem(str(volume) if volume else "")
            item.setForeground(QBrush(QColor(255,255,0)))
            self.order_book_buy_table.setItem(row_idx, 1, item)
            idx_button = IndexedPushButton('挂买单')
            idx_button.row = row_idx
            idx_button.column = 2
            idx_button.price = price
            idx_button.pressed.connect(self.onOrderBookBuyClick)
            self.order_book_buy_table.setCellWidget(row_idx, 2, idx_button)
        # adjust row and column
        for row in range(4):
            self.order_book_sell_table.setRowHeight(row, 16)
            self.order_book_buy_table.setRowHeight(row, 16)

        self.order_book_container.update()
        log.info("Displayed order book")

    def update_data(self):
        try:
            stock_code = self.stock_input.currentText().strip().split(',')[0]
            if not stock_code:
                raise ValueError("股票代码不能为空")
            try:
                self.stock_label_name.setText(self.stock_input.currentText().strip().split(',')[1])
            except:
                self.stock_label_name.setText(self.get_realtime_ticks(stock_code)['f58'])

            self.df = self.get_today_ticks(stock_code)
            log.debug("Debug: eastmoney data fetched")
            log.debug(self.df.head(10))
            required_columns = ['Time', 'Price', 'Metric', 'Volume', 'Type']
            if not all(col in self.df.columns for col in required_columns):
                raise ValueError(f"缺少必要列，实际列: {self.df.columns}")
            self.df = self.df[required_columns].copy()

            if self.df.empty:
                raise ValueError("过滤后数据为空，可能全是中性盘或无有效交易")
            self.summary_status_label.setText("数据已更新，输入时间")
        except Exception as e:
            self.df = pd.DataFrame(self.fallback_data)
            self.time_input.setText(str(self.df['Time'].iloc[0]))
            self.summary_status_label.setText(f"更新失败: {str(e)}，已使用默认数据")
            log.error(f"Error: Update failed, using fallback data. Error: {str(e)}")

    def update_order_book(self):
        '''
        获取实时盘口数据，并显示
        '''
        # 股票代码为空
        if not self.stock_input.currentText():
            log.error('股票代码不能为空')
            return
        try:
            # self.update_order_book_button.setEnabled(False)
            stock_code = self.stock_input.currentText().strip().split(',')[0]
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # Fetch order book data only
            for attempt in range(3):
                try:
                    self.order_book = self.get_realtime_ticks(stock_code)
                    # 没有获取到正确数据，比如错误的股票代码
                    if not self.order_book:
                        return
                    log.info("eastmoney order book data fetched")
                    # # 最后三分钟锁单，数据不更新
                    # if self.order_book['f31'] == '-':
                    #     return
                    break
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < 2:
                        time.sleep(2)
                        continue
                    raise
            log.debug('卖五', self.order_book['f31'])
            # 更新股票名称
            self.stock_label_name.setText(self.order_book['f58'])
            # 将数据时间设置为统计开始时间
            self.time_input.setText(datetime.datetime.fromtimestamp(int(self.order_book['f86'])).strftime('%H%M%S'))
            # 更新盘口
            self.display_order_book()
            # 更新 bid table
            self.update_bid_table_order_volume()
        except Exception as e:
            self.order_book = None
            self.display_order_book()
            log.error(f"Error: Order book update failed. Error: {traceback.format_exc()}")

    def analyze_data(self):
        # 先更新数据再分析，盘中的时候好用
        self.update_data()
        self.update_detail_table_view()

        try:
            start_time = int(self.start_time_input.text())
        except:
            start_time = 93000
            self.result_table.setRowCount(0)
            self.summary_status_label.setText("有效时间 (HHMMSS)")
            self.start_time_input.setText('93000')
            log.error("Error: Invalid start time input")

        try:
            end_time = int(self.end_time_input.text())
        except:
            end_time = 150000
            self.result_table.setRowCount(0)
            self.summary_status_label.setText("有效时间 (HHMMSS)")
            self.end_time_input.setText('150000')
            log.error("Error: Invalid end time input")           

        # 初始化买入和卖出量
        filtered_df = self.df[(self.df['Time'] >= start_time) & (self.df['Time'] <= end_time)]
        filtered_df['buy_vol'] = 0
        filtered_df['sell_vol'] = 0
        filtered_df.loc[filtered_df['Type'] == '2', 'buy_vol'] = filtered_df['Volume']
        filtered_df.loc[filtered_df['Type'] == '1', 'sell_vol'] = filtered_df['Volume']
        # 按价格汇总
        self.result = filtered_df.groupby('Price')[['buy_vol', 'sell_vol']].sum().sort_values('Price',ascending=False).reset_index()
        # 更新汇总表
        self.result_table.setColumnCount(3)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setHorizontalHeaderLabels(['价格', '卖一成交', '买一成交'])
        self.result_table.setRowCount(len(self.result))
        for row_idx, row_data in self.result.iterrows():
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(f"{row_data['Price']:.2f}"))
            # 卖一价成交是主动买入，设置为红色，称为外盘
            item = QTableWidgetItem(str(int(row_data['buy_vol'])))
            item.setForeground(QBrush(QColor(255,0,0)))
            self.result_table.setItem(row_idx, 1, item)
            # 买一价成交是主动卖出，设置为绿色，称为内盘
            item = QTableWidgetItem(str(int(row_data['sell_vol'])))
            item.setForeground(QBrush(QColor(0,255,0)))
            self.result_table.setItem(row_idx, 2, item)
        # adjust row and column
        for row in range(self.result.__len__()):
            self.result_table.setRowHeight(row, 16)
        # self.result_table.resizeColumnsToContents()
        self.result_table.viewport().update()
        log.debug(f"Debug: Analysis completed, displayed {len(self.result)} rows")

        if self.bid_table.rowCount():
            self.update_bid_table()

        self.summary_status_label.setText(f"分析完成，从{start_time}开始")


class TradeAnalyzer(QMainWindow):
    def __init__(self, stock_list):
        super().__init__()
        self.setWindowTitle("股票交易分析")
        self.setGeometry(200, 200, 700, 250)  # Wider window for side-by-side tables

        self.central_widget = QWidget()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        for idx, stock in enumerate(stock_list):
            block = TradeBlock(self, stock=stock)
            self.layout.addWidget(block, idx, 0)
        # self.block1 = TradeBlock(self, stock='000750,国海证券,GHZQ')
        # self.block2 = TradeBlock(self, stock='601568,北元集团,BYJT')
        # self.block2 = TradeBlock(self, stock='600871,石化油服,SHYF')
        # self.block4 = TradeBlock(self, stock='601866,中远海发,ZYHF')

        # self.layout.addWidget(self.block1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # self.layout.addWidget(self.block2, 1, 0)


def get_stock_list_from_command_line():
    if len(sys.argv) == 1:
        return [''], ['']
    stock_list = []
    stock_name_list = []
    for arg in sys.argv[1:]:
        stock_str = [stock for stock in file_utils.get_combobox_list() if arg in stock][0]
        stock_list.append(stock_str)
        stock_name_list.append(stock_str.split(',')[1])
    return stock_list, stock_name_list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #2E2E2E;
            color: #E0E0E0;
        }
        QMainWindow {
            background-color: #111111;
        }
        QLineEdit {
            background-color: #3A3A3A;
            color: #E0E0E0;
            border: 1px solid #555555;
            padding: 2px;
        }
        QPushButton {
            background-color: #555555;
            color: #E0E0E0;
            border: 1px solid #aaaaaa;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #666666;
        }
        QPushButton:pressed {
            background-color: #444444;
        }
        QPushButton:checked {
            background-color: #2A2A2A;
        }
        QTableWidget {
            background-color: #1A1A1A;
            selection-background-color: #222222;
        }
    """)
    stock_list, stock_name_list = get_stock_list_from_command_line()
    window = TradeAnalyzer(stock_list)
    if stock_name_list[0]:
        window.setWindowTitle(' '.join(stock_name_list))
    else:
        window.setWindowTitle('股票交易分析器')
    icon = QIcon(":/icons/Icons/stock.ico")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())