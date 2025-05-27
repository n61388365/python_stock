############################################
## V1 update
## date: 2025-04-25 周五 股票代码可输入可选择
## date: 2025-04-27 周日 添加回车处理
##                      减成两个单元
## date: 2025-05-05 周一 添加A股全列表
############################################

import json
import sys
import pandas as pd
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QGridLayout, QCheckBox, QComboBox, QAbstractItemView, QCompleter
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QBrush, QColor
import urllib.request
import datetime
import log
import all_stock_2025_05_05


def get_realtime_ticks(stock_code):
    # 深证 0. + 000750，上证 1. + 601568
    stock_code = stock_code.startswith('6') and '1.{}'.format(stock_code) or '0.{}'.format(stock_code)
    url = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secid={}'.format(stock_code)
    with urllib.request.urlopen(url=url) as r:
        data=r.readline().decode().lstrip('data:')
        data_json = json.loads(data)
        log.debug(data_json['data'])
        return data_json['data']


def get_today_ticks(stock_code='000750'):

    if stock_code.startswith('6'):
        stock_code = "1.{}".format(stock_code)
    else:
        stock_code = "0.{}".format(stock_code)
    url='http://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&pos=-0&secid={}'.format(stock_code)
    # get data from eastmoney
    with urllib.request.urlopen(url=url) as r:
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
    df['Type'] = df['Type'].astype(str)
    log.debug(df.dtypes)
    # Convert time from HH:MM:SS to HHMM
    try:
        df['Time'] = df['Time'].str.replace(':', '').astype(int)
    except Exception as e:
        raise ValueError(f"时间格式转换失败: {str(e)}")

    return df


class MyComboBox(QComboBox):

    enterPressed = pyqtSignal()

    def __init__(self):
        super(MyComboBox,self).__init__()
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

    def keyReleaseEvent(self, event):
        # 回车键
        if event.key() == 16777220:
            self.enterPressed.emit()

class IndexedPushButton(QPushButton):
    def init(self, text='', parent=None):
        super(QPushButton, self).init(text, parent=parent)
        self.row = 0
        self.column = 0
        self.text = ""


class TradeBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fallback_data = {
            'Time': [92500, 93000, 93003, 93006, 93009],
            'Price': [3.84, 3.84, 3.85, 3.84, 3.85],
            'Volume': [5368, 1049, 11248, 3251, 2817],
            'Type': ['1', '2', '1', '2', '1']
        }
        self.df = pd.DataFrame(self.fallback_data)
        self.order_book = None
        self.result = None
        self.bid_price = 0
        self.bid_volumn = 0
        self.bid_time = datetime.datetime.now().strftime('%H:%M:%S')

        # Block layout
        self.layout = QVBoxLayout(self)

        # Input and button layout
        self.input_layout = QHBoxLayout()
        self.stock_label_name = QLabel('股票名称')
        self.stock_label_name.setFixedWidth(50)
        self.stock_label_name.setStyleSheet("color: yellow;")
        self.stock_label = QLabel("代码")
        self.stock_label.setFixedWidth(30)
        self.stock_input = MyComboBox()
        self.stock_input.addItems(all_stock_2025_05_05.stock_list)
        self.stock_input.setEditable(True)
        self.stock_input.enterPressed.connect(self.update_data)
        self.label = QLabel("时间")
        self.label.setMinimumWidth(30)
        self.time_input = QLineEdit()
        self.time_input.setFixedWidth(70)
        self.time_input.setPlaceholderText("例如: 150800")
        self.time_input.setText(str(93000))
        self.time_input.returnPressed.connect(self.analyze_data)
        self.price_label = QLabel("挂单价格")
        self.price_label.setFixedWidth(50)
        self.price_input = QLineEdit()
        self.price_input.setFixedWidth(70)
        self.update_button_sell = QPushButton("挂卖单")
        self.update_button_sell.clicked.connect(lambda checked: self.add_bid_table(checked, True))
        self.update_button_buy = QPushButton("挂买单")
        self.update_button_buy.clicked.connect(lambda checked: self.add_bid_table(checked, False))
        self.analyze_button = QPushButton("挂单分析")
        self.analyze_button.clicked.connect(self.analyze_data)
        self.analyze_checkbox = QCheckBox()
        self.analyze_checkbox.setCheckState(Qt.CheckState.Checked)
        self.update_order_book_button = QPushButton("盘口更新")
        self.update_order_book_button.clicked.connect(self.update_order_book)
        self.input_layout.addWidget(self.stock_label_name)
        self.input_layout.addWidget(self.stock_label)
        self.input_layout.addWidget(self.stock_input)
        self.input_layout.addWidget(self.label)
        self.input_layout.addWidget(self.time_input)
        self.input_layout.addWidget(self.price_label)
        self.input_layout.addWidget(self.price_input)
        self.input_layout.addWidget(self.update_button_sell)
        self.input_layout.addWidget(self.update_button_buy)
        self.input_layout.addWidget(self.analyze_button)
        self.input_layout.addWidget(self.update_order_book_button)
        self.input_layout.addWidget(self.analyze_checkbox)
        self.layout.addLayout(self.input_layout)

        # Tables layout (side by side)
        self.tables_layout = QHBoxLayout()

        # 左
        self.left_layout = QVBoxLayout()

        # 挂单列表
        self.bid_table = QTableWidget(0, 7)
        self.bid_table.setHorizontalHeaderLabels(['挂单时间', '挂单价格', '买卖挂单', '挂单数量', '挂单成交', '挂单余额', '挂单移除'])
        self.bid_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.bid_table.setAlternatingRowColors(True)
        self.bid_table.horizontalHeader().setMinimumSectionSize(50)
        self.bid_table.horizontalHeader().setFixedHeight(24)
        self.bid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bid_table.setFixedHeight(113)
        self.bid_table.setMinimumWidth(500)  # Ensure visibility
        self.bid_table.verticalHeader().setVisible(False)
        self.left_layout.addWidget(self.bid_table)

        # Tick data table
        self.result_table = QTableWidget()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['时间', '价格', '成交量', '类型'])
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.horizontalHeader().setFixedHeight(24)
        self.result_table.horizontalHeader().setMinimumSectionSize(50)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.setFixedHeight(139)
        self.result_table.setMinimumWidth(400)  # Ensure visibility
        
        self.left_layout.addWidget(self.result_table)
        self.tables_layout.addLayout(self.left_layout)

        # Order book table
        self.order_book_container = QVBoxLayout()
        self.order_book_sell_table = QTableWidget()
        self.order_book_sell_table.setRowCount(5)
        self.order_book_sell_table.setColumnCount(4)
        self.order_book_sell_table.setHorizontalHeaderLabels(['价格', '总数', '已成交', '待成交'])
        self.order_book_sell_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.order_book_sell_table.setAlternatingRowColors(True)
        self.order_book_sell_table.horizontalHeader().setFixedHeight(24)
        self.order_book_sell_table.horizontalHeader().setMinimumSectionSize(50)
        self.order_book_sell_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_book_sell_table.setFixedHeight(141)
        self.order_book_sell_table.setMinimumWidth(300)
        self.order_book_sell_table.setVerticalHeaderLabels(['卖五', '卖四', '卖三', '卖二', '卖一'])
        self.order_book_sell_table.verticalHeader().setDefaultSectionSize(12)
        # self.order_book_sell_table.setVerticalHeaderLabels(['卖四', '卖三', '卖二', '卖一', '买一', '买二', '买三', '买四'])
        self.order_book_sell_table.setShowGrid(False)

        self.order_book_buy_table = QTableWidget()
        self.order_book_buy_table.setRowCount(5)
        self.order_book_buy_table.setColumnCount(4)
        self.order_book_buy_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.order_book_buy_table.setAlternatingRowColors(True)
        self.order_book_buy_table.setHorizontalHeaderLabels(['价格', '总数', '已成交', '待成交'])
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

        sell_rows = [('f31', 'f32'), ('f33', 'f34'), ('f35', 'f36'), ('f37', 'f38'), ('f39', 'f40')]
        buy_rows = [('f19', 'f20'), ('f17', 'f18'), ('f15', 'f16'),  ('f13', 'f14'), ('f11','f12')]

        for price_col, vol_col in sell_rows:
            price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
            volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
            if price == float(bid_price):
                return volume

        for price_col, vol_col in buy_rows:
            price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
            volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0
            if price == float(bid_price):
                return volume

    def add_bid_table(self, checked, bid_type):
        log.info("I am add bid table function")
        if not self.order_book:
            return
        print(checked, bid_type)
        # 挂单价如果未填，通过挂买单和挂卖单自动填入
        if not self.price_input.text():
            if bid_type:
                self.price_input.setText(str(self.order_book['f39']))
            else:
                self.price_input.setText(str(self.order_book['f19']))
        row_idx = self.bid_table.rowCount()
        self.bid_table.insertRow(row_idx)
        # volumn 0 挂单时间
        timeItem = QTableWidgetItem(self.time_input.text())
        timeItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        timeItem.setBackground(QBrush(QColor(0,0,0)))
        # volumn 1 挂单价格
        priceItem = QTableWidgetItem(self.price_input.text())
        priceItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        priceItem.setBackground(QBrush(QColor(0,0,0)))
        priceItem.setForeground(QBrush(self.price_color_choose(float(self.price_input.text()),self.order_book['f60'])))
        # volumn 2 挂单类型
        sell_or_buy = bid_type and '卖单' or '买单'
        sellOrBuyItem = QTableWidgetItem(sell_or_buy)
        sellOrBuyItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        # volumn 3 挂单数量
        volumnItem = QTableWidgetItem(str(self.get_order_vol_by_price(self.price_input.text())))
        volumnItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        volumnItem.setBackground(QBrush(QColor(0,0,0)))
        volumnItem.setForeground(QBrush(QColor(255,255,0)))
        # volumn 4 成交量
        completedItem = QTableWidgetItem(self.bid_volumn)
        completedItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bid_table.setItem(row_idx,0,timeItem)
        self.bid_table.setItem(row_idx,1,priceItem)
        self.bid_table.setItem(row_idx,2,sellOrBuyItem)
        self.bid_table.setItem(row_idx,3,volumnItem)
        self.bid_table.setItem(row_idx,4,completedItem)
        idxButton = IndexedPushButton("delete")
        idxButton.row = row_idx
        idxButton.column = 6
        idxButton.text = "delete row {}".format(row_idx)
        idxButton.clicked.connect(self.onClick)
        self.bid_table.setCellWidget(row_idx, 6, idxButton)
        self.bid_table.setRowHeight(row_idx, 16)
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
        log.info('no bid price found', bid_price)
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
            self.bid_table.setItem(row_idx, 4, item)
            item = QTableWidgetItem(str(int(bid_vol_left)))
            self.bid_table.setItem(row_idx, 5, item)
        self.bid_table.viewport().update()


    def onClick(self):
        print(self.sender().row, self.sender().column)
        self.bid_table.removeRow(self.sender().row)
        # 重新设置button的row
        for idx in range(self.bid_table.rowCount()):
            self.bid_table.cellWidget(idx, 6).row = idx


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
        # self.result_table.resizeColumnsToContents()
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
            # self.order_book_sell_table.viewport().update()
            # self.order_book_buy_table.viewport().update()
            self.order_book_container.update()
            return

        sell_rows = [('f31', 'f32'), ('f33', 'f34'), ('f35', 'f36'), ('f37', 'f38'), ('f39', 'f40')]
        buy_rows = [('f19', 'f20'), ('f17', 'f18'), ('f15', 'f16'),  ('f13', 'f14'), ('f11','f12')]

        # 昨日收盘价
        yesterday_close = self.order_book['f60']

        self.order_book_sell_table.setRowCount(5)

        # bid_price = self.price_input.text()
        for row_idx, (price_col, vol_col) in enumerate(sell_rows):
            price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
            volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0

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
            # if price == float(bid_price):
            #     item.setForeground(QBrush(QColor(173,216,255)))
            #     item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_sell_table.setItem(row_idx, 0, item)

            # volume color yellow
            item = QTableWidgetItem(str(volume) if volume else "")
            item.setForeground(QBrush(QColor(255,255,0)))
            # if price == float(bid_price):
            #     log.debug("挂单价对比", price, float(bid_price))
            #     item.setForeground(QBrush(QColor(173,216,255)))
            #     item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_sell_table.setItem(row_idx, 1, item)

            item = QTableWidgetItem("我是狼")
            self.order_book_sell_table.setItem(row_idx, 2, item)


        self.order_book_buy_table.setRowCount(5)
        for row_idx, (price_col, vol_col) in enumerate(buy_rows):
            price = float(self.order_book[price_col]) if self.order_book[price_col] else 0
            volume = int(self.order_book[vol_col]) if self.order_book[vol_col] else 0

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
            # if price == float(bid_price):
            #     log.debug("挂单价对比", price, float(bid_price))
            #     item.setForeground(QBrush(QColor(173,216,255)))
            #     item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_buy_table.setItem(row_idx, 0, item)

            # volume color yellow
            item = QTableWidgetItem(str(volume) if volume else "")
            item.setForeground(QBrush(QColor(255,255,0)))
            # if price == float(bid_price):
            #     log.debug("挂单价对比", price, float(bid_price))
            #     item.setForeground(QBrush(QColor(173,216,255)))
            #     item.setBackground(QBrush(QColor(0,0,0)))
            self.order_book_buy_table.setItem(row_idx, 1, item)
            self.order_book_buy_table.setItem(row_idx, 2, QTableWidgetItem("你是羊"))

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
                self.stock_label_name.setText(get_realtime_ticks(stock_code)['f58'])

            
            self.df = get_today_ticks(stock_code)
            log.debug("Debug: eastmoney data fetched")
            log.debug(self.df.head(10))
            required_columns = ['Time', 'Price', 'Volume', 'Type']
            if not all(col in self.df.columns for col in required_columns):
                raise ValueError(f"缺少必要列，实际列: {self.df.columns}")
            self.df = self.df[required_columns].copy()

            if self.df.empty:
                raise ValueError("过滤后数据为空，可能全是中性盘或无有效交易")
            # self.time_input.setText(str(self.df['Time'].iloc[0]).replace(':',''))
            # self.display_raw_data()
            self.label.setText("数据已更新，输入时间")
        except Exception as e:
            self.df = pd.DataFrame(self.fallback_data)
            self.time_input.setText(str(self.df['Time'].iloc[0]))
            # self.display_raw_data()
            self.label.setText(f"更新失败: {str(e)}，已使用默认数据")
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
            self.update_order_book_button.setEnabled(False)
            stock_code = self.stock_input.currentText().strip().split(',')[0]
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # Fetch order book data only
            for attempt in range(3):
                try:
                    self.order_book = get_realtime_ticks(stock_code)
                    # 没有获取到正确数据，比如错误的股票代码
                    if not self.order_book:
                        return
                    break
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < 2:
                        time.sleep(2 ** attempt)
                        continue
                    raise
            log.info("eastmoney order book data fetched")
            log.debug('卖五', self.order_book['f31'])
            # 点盘口更新后价格输入框内容清零
            self.price_input.setText('')
            # 更新股票名称
            self.stock_label_name.setText(self.order_book['f58'])
            # 将数据时间设置为统计开始时间
            self.time_input.setText(datetime.datetime.fromtimestamp(int(self.order_book['f86'])).strftime('%H%M%S'))
            # 更新盘口
            self.display_order_book()
        except Exception as e:
            self.order_book = None
            self.display_order_book()
            log.error(f"Error: Order book update failed. Error: {e.__traceback__()}")
        finally:
            self.update_order_book_button.setEnabled(True)

    def update_order_book_table(self):
        """
        更新盘口表
        """
        if not self.order_book:
            return
        
        # 从表格中获取数据，这样可以直接修改表格内容后分析
        # 0-卖四，1-卖三，2-卖二，3-卖一
        # 0-买一，1-买二，2-买三，3-买四
        bid_price = float(self.price_input.text() and self.price_input.text() or '0')
        for table_row_idx in range(5):
            s_price = float(self.order_book_sell_table.item(table_row_idx, 0).text())
            s_vol = int(self.order_book_sell_table.item(table_row_idx, 1).text())
            if s_price == bid_price:
                self.order_book_sell_table.item(table_row_idx, 0).setForeground(QBrush(QColor(173,216,255)))
                self.order_book_sell_table.item(table_row_idx, 1).setForeground(QBrush(QColor(173,216,255)))
            b_price = float(self.order_book_buy_table.item(table_row_idx, 0).text())
            b_vol = int(self.order_book_buy_table.item(table_row_idx, 1).text())
            if b_price == bid_price:
                self.order_book_buy_table.item(table_row_idx, 0).setForeground(QBrush(QColor(173,216,255)))
                self.order_book_buy_table.item(table_row_idx, 1).setForeground(QBrush(QColor(173,216,255)))
            log.debug('卖一', s_price,s_vol, '买一',b_price, b_vol)
            for row_idx, row_data in self.result.iterrows():
                if row_data['Price'] == s_price:
                    # 主动买入量设置为红色
                    item = QTableWidgetItem(str(int(row_data['buy_vol'])))
                    item.setForeground(QBrush(QColor(255,0,0)))
                    self.order_book_sell_table.setItem(table_row_idx, 2, item)
                    self.order_book_sell_table.setItem(table_row_idx, 3, QTableWidgetItem(str(s_vol - int(row_data['buy_vol']))))
                if row_data['Price'] == b_price:
                    item = QTableWidgetItem(str(int(row_data['sell_vol'])))
                    item.setForeground(QBrush(QColor(0,255,0)))
                    self.order_book_buy_table.setItem(table_row_idx, 2, item)
                    self.order_book_buy_table.setItem(table_row_idx, 3, QTableWidgetItem(str(b_vol - int(row_data['sell_vol']))))


    def analyze_data(self):
        # 是否先更新数据再分析，盘中的时候好用
        if self.analyze_checkbox.isChecked():
            self.update_data()

        try:
            start_time = int(self.time_input.text())
        except ValueError:
            self.result_table.setRowCount(0)
            self.label.setText("有效时间 (HHMM)")
            log.error("Error: Invalid start time input")
            return

        # 初始化买入和卖出量
        filtered_df = self.df[self.df['Time'] >= start_time]
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
        self.result_table.setHorizontalHeaderLabels(['价格', '卖一价成交总量', '买一价成交总量'])
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

        if self.order_book:
            self.update_order_book_table()
        if self.bid_table.rowCount():
            self.update_bid_table()

        self.label.setText(f"分析完成，从{start_time}开始")


class TradeAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票交易分析")
        self.setGeometry(200, 200, 900, 250)  # Wider window for side-by-side tables

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        self.block1 = TradeBlock(self)
        # self.block2 = TradeBlock(self, stock_code='000750', stock_name="国海证券")
        # self.block1 = TradeBlock(self, stock_code='600871', stock_name="石化油服")
        # self.block2 = TradeBlock(self, stock_code='600871', stock_name="石化油服")
        # self.block2 = TradeBlock(self, stock_code='601568', stock_name="北元集团")
        # self.block3 = TradeBlock(self, stock_code='601866', stock_name="中远海发")
        # self.block4 = TradeBlock(self, stock_code='000750', stock_name="国海证券")

        self.layout.addWidget(self.block1)
        # self.layout.addWidget(self.block2, 1, 0)
        # self.layout.addWidget(self.block3, 1, 0)
        # self.layout.addWidget(self.block4, 1, 1)

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
            border: 1px solid #666666;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #666666;
        }
        QPushButton:pressed {
            background-color: #444444;
        }
        QTableWidget {
            background-color: #1A1A1A;
            selection-background-color: #222222;
        }
    """)    
    window = TradeAnalyzer()
    window.show()
    sys.exit(app.exec())