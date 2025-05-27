##################################
# created: 2025-05
# update: 
#  2025-05-27 周二 seperate 最高 最低
#  2025-05-30 周五 bug fix 


import json
import time
import xueqiu_api
from PyQt6.QtWidgets import (
  QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
  QWidget, QLabel, QTableWidget, QTableWidgetItem,
  QHeaderView, QPushButton
  )
from PyQt6.QtGui import QBrush, QColor, QIcon, QFont
from PyQt6.QtCore import (Qt, QTimer)
import sys
import pandas as pd
import log
import compiled_resources


class JsonDecoder:
  def __init__(self, d) -> None:
    # print(type(d))  ## <class 'dict'>
    self.__dict__ = d

time_pause = 10000 # 10秒

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("两市成交额分析")
        self.setGeometry(200,200,400,200)

        # 数据自动从雪球更新
        self.analyze_timer = QTimer()
        self.analyze_timer.setInterval(time_pause)
        self.analyze_timer.timeout.connect(self.analyze_data_on_timer)

        # 加载昨日数据
        self.yesterday_data = self.load_last_data()

        self.xueqiu_api_is_running = False

        self.init_ui()

    def init_ui(self):
        self.top = QHBoxLayout()
        self.label_time = QLabel("{} : {} minutes".format(time.strftime("%H:%M:%S",time.localtime()), 0))
        self.label_time.setMinimumWidth(240)
        self.auto_update_button = QPushButton('自动刷新')
        self.auto_update_button.setCheckable(True)
        self.auto_update_button.clicked.connect(self.set_analyze_timer)
        self.save_data_button = QPushButton('保存数据')
        self.save_data_button.clicked.connect(self.save_data)
        self.top.addWidget(self.label_time)
        self.top.addWidget(self.auto_update_button)
        self.top.addWidget(self.save_data_button)
        # self.top.setSpacing(50)
        # 两市成交分析表
        self.sh_sz_amount_total_table = QTableWidget()
        self.sh_sz_amount_total_table.setColumnCount(5)
        self.sh_sz_amount_total_table.setRowCount(0)
        self.sh_sz_amount_total_table.setMinimumWidth(350)
        self.sh_sz_amount_total_table.setMinimumHeight(100)
        self.sh_sz_amount_total_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Fixed)
        self.sh_sz_amount_total_table.setColumnWidth(0,40)
        self.sh_sz_amount_total_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.sh_sz_amount_total_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        self.sh_sz_amount_total_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeMode.Stretch)
        self.sh_sz_amount_total_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeMode.Stretch)
        self.sh_sz_amount_total_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sh_sz_amount_total_table.setHorizontalHeaderLabels(['时间','成交差额','增量','今日成交','昨日成交'])

        # 最大最小值
        my_font = QFont("SimSun & NSimSun", 11)
        self.layout_max_min_volume = QHBoxLayout()
    
        self.label_high = QLabel('最高')
        self.label_high.setStyleSheet("color: rgb(255,255,0);")
        self.label_high.setFixedWidth(30)
        self.label_high.setFont(my_font)
        self.label_max_volume = QLabel("I am here")
        self.label_max_volume.setFont(my_font)
        self.label_max_time = QLabel('时间 00:00')
        self.label_max_time.setFont(my_font)
    
        self.label_low = QLabel('最低')
        self.label_low.setStyleSheet("color: rgb(255,255,0);")
        self.label_low.setFont(my_font)
        self.label_min_volume = QLabel("I am here")
        self.label_min_volume.setFont(my_font)
        self.label_min_time = QLabel('时间 00:00')
        self.label_min_time.setFont(my_font)
        self.layout_max_min_volume.addWidget(self.label_high)
        self.layout_max_min_volume.addWidget(self.label_max_volume)
        self.layout_max_min_volume.addWidget(self.label_max_time)
        self.layout_max_min_volume.addWidget(self.label_low)
        self.layout_max_min_volume.addWidget(self.label_min_volume)
        self.layout_max_min_volume.addWidget(self.label_min_time)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addLayout(self.top)
        layout.addWidget(self.sh_sz_amount_total_table)
        layout.addLayout(self.layout_max_min_volume)

        # layout.setSpacing(2)  # No spacing between top and bottom layouts
        # layout.setContentsMargins(0, 0, 0, 0)  # No margins

    def set_analyze_timer(self):
        if self.auto_update_button.isChecked():
            self.analyze_data_on_timer()
            self.analyze_timer.start()
        else:
            self.analyze_timer.stop()

    def analyze_data_on_timer(self):
        '''
            timestamp      amount_total  sh_sz_amount_total  sh_sz_amount_total_change  sh_sz_amount_total_change_diff  sh_sz_amount_total_last
        0   1747963800000  1.564259e+10              443.87                     -48.95                            0.00                   492.83
        1   1747963860000  2.304827e+10              645.67                     -78.15                          -29.20                   723.82
        2   1747963920000  2.941971e+10              810.92                     -93.65                          -15.49                   904.56
        3   1747963980000  3.504681e+10              964.19                    -110.15                          -16.50                  1074.33
        4   1747964040000  3.991333e+10             1094.96                    -121.92                          -11.78                  1216.88
        ..            ...           ...                 ...                        ...                             ...                      ...
        64  1747967640000  1.898564e+11             4851.77                    -287.99                           -1.66                  5139.76
        65  1747967700000  1.911214e+11             4882.49                    -293.92                           -5.93                  5176.42
        66  1747967760000  1.926492e+11             4917.96                    -294.05                           -0.13                  5212.01
        67  1747967820000  1.940517e+11             4950.79                    -298.12                           -4.07                  5248.91
        68  1747967880000  1.946411e+11             4964.41                    -317.00                          -18.88                  5281.41
        '''
        print("I am here waiting for you")
        # 确认调用
        if self.xueqiu_api_is_running:
            log.info("xueqiu api is running")
            return
        self.xueqiu_api_is_running = True
        try:
            sh_sz_calculated = self.calculate_data()
        except:
            self.xueqiu_api_is_running = False
            return
        print(sh_sz_calculated)
        # 最大最小增量 未收盘之前最后一项数据保持变化，计算最大最小值时不用
        if len(sh_sz_calculated) == 1:
            log.info('等待开盘')
            return
        # 最后一条数据上头条
        last_row = sh_sz_calculated.iloc[-1]
        self.label_time.setText("{} {} minutes {}亿 {}亿".format(time.strftime("%H:%M:%S",time.localtime(float(str(last_row[0])[0:10]))), len(sh_sz_calculated)-1, last_row[3], last_row[4]))
        # 两条记录，单独处理
        if len(sh_sz_calculated) == 2:
            return
        is_lunch_break = len(sh_sz_calculated) == 121 and int(time.strftime('%H%M%S',time.localtime())) > 113000
        is_end_of_day_transaction = len(sh_sz_calculated) == 242 and int(time.strftime('%H%M%S',time.localtime())) > 150200
        if is_lunch_break or is_end_of_day_transaction:
            change_max_volume = sh_sz_calculated['sh_sz_amount_total_change'][1:].max()
            change_min_volume = sh_sz_calculated['sh_sz_amount_total_change'][1:].min()
        else:
            change_max_volume = sh_sz_calculated[0:-1]['sh_sz_amount_total_change'][1:].max()
            change_min_volume = sh_sz_calculated[0:-1]['sh_sz_amount_total_change'][1:].min()
        change_max_timestamp = sh_sz_calculated[sh_sz_calculated.sh_sz_amount_total_change == change_max_volume].iloc[0].timestamp
        change_max_time = stampToTime(change_max_timestamp)
        change_min_timestamp = sh_sz_calculated[sh_sz_calculated.sh_sz_amount_total_change == change_min_volume].iloc[0].timestamp
        change_min_time = stampToTime(change_min_timestamp)
        self.label_max_volume.setText("{:+.2f} 亿".format(change_max_volume))
        self.label_max_time.setText("时间 {}".format(change_max_time))
        if change_max_volume > 0:
            self.label_max_volume.setStyleSheet("color: rgb(255,0,0);background-color: rgb(20,20,20)")
        else:
            self.label_max_volume.setStyleSheet("color: rgb(0,255,0);background-color: rgb(20,20,20)")
        self.label_min_volume.setText(f"{change_min_volume}亿")
        self.label_min_time.setText(f"时间 {change_min_time}")
        if change_min_volume > 0:
            self.label_min_volume.setStyleSheet("color: rgb(255,0,0);background-color: rgb(20,20,20)")
        else:
            self.label_min_volume.setStyleSheet("color: rgb(0,255,0);background-color: rgb(20,20,20)")
        print(f"最高 {change_max_time}:{change_max_volume} 亿,最低 {change_min_time}:{change_min_volume} 亿")
        self.sh_sz_amount_total_table.setRowCount(0)
        # 遍历
        for idx, row_data in sh_sz_calculated.iterrows():
            # 最后一行
            if idx == len(sh_sz_calculated) - 1 and len(sh_sz_calculated) != 242 and len(sh_sz_calculated) != 121:
                break
            self.sh_sz_amount_total_table.insertRow(idx)
            # 列1 时间
            item_timestamp = QTableWidgetItem(stampToTime(row_data[0]))
            self.sh_sz_amount_total_table.setItem(idx, 0, item_timestamp)
            # 列2 增量
            item_change = QTableWidgetItem(str(f"{row_data[3]:.2f}"))
            item_change.setForeground(QBrush(row_data[3]>0 and QColor(255,0,0) or QColor(0,255,0)))
            item_change.setBackground(QBrush(QColor(0,0,0)))
            item_change.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.sh_sz_amount_total_table.setItem(idx, 1, item_change)
            # 列3 分钟增减
            if row_data[4] > 0:
                item_diff = QTableWidgetItem(f"{row_data[4]:.2f} 🠉")
                item_diff.setForeground(QBrush(QColor(255,0,0)))
            if row_data[4] < 0:
                item_diff = QTableWidgetItem(f"{row_data[4]:.2f} 🠋")
                item_diff.setForeground(QBrush(QColor(0,255,0)))
            if row_data[4] == 0:
                item_diff = QTableWidgetItem(f"{row_data[4]:.2f} 🢀")
            item_diff.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.sh_sz_amount_total_table.setItem(idx,2,item_diff)
            # 列4 今日成交
            item_today = QTableWidgetItem(f"{row_data[2]:.2f}")
            item_today.setForeground(QBrush(QColor(255,255,0)))
            self.sh_sz_amount_total_table.setItem(idx,3,item_today)
            # 列5 昨日成交
            item_yesterday = QTableWidgetItem(f"{row_data[5]:.2f}")
            self.sh_sz_amount_total_table.setItem(idx,4,item_yesterday)
            # 设置行高
            self.sh_sz_amount_total_table.setRowHeight(idx, 16)
        self.sh_sz_amount_total_table.scrollToBottom()
        self.sh_sz_amount_total_table.viewport().update()

    def load_last_data(self):
        with open("last_data_demo.json") as f:
            raw_data = json.load(f)
        df_sh000001 = pd.DataFrame((json.loads(raw_data["sh000001"])['data']['items']), columns=['timestamp', 'amount_total'])
        df_sz399001 = pd.DataFrame((json.loads(raw_data["sz399001"])['data']['items']), columns=['timestamp', 'amount_total'])
        df_sh000016 = pd.DataFrame((json.loads(raw_data["sh000016"])['data']['items']), columns=['timestamp', 'amount_total'])
        return df_sh000001, df_sz399001, df_sh000016

    def get_today_data(self):
        sh000001 = xueqiu_api.get_realtime_data_from_xueqiu("sh000001")
        sz399001 = xueqiu_api.get_realtime_data_from_xueqiu("sz399001")
        sh000016 = xueqiu_api.get_realtime_data_from_xueqiu("sh000016")
        sh000300 = xueqiu_api.get_realtime_data_from_xueqiu("sh000300")

        df_sh000001 = pd.DataFrame((json.loads(sh000001)['data']['items']), columns=['timestamp', 'amount_total'])
        df_sz399001 = pd.DataFrame((json.loads(sz399001)['data']['items']), columns=['timestamp', 'amount_total'])
        df_sh000016 = pd.DataFrame((json.loads(sh000016)['data']['items']), columns=['timestamp', 'amount_total'])
        self.xueqiu_api_is_running = False
        return df_sh000001, df_sz399001, df_sh000016

    def calculate_data(self):
        df_sh000001_last, df_sz399001_last , df_sh000016_last = self.yesterday_data
        df_sh_sz_last = df_sh000001_last.copy()
        df_sh_sz_last.rename(columns={'amount_total': 'sh_amount_toal_last'}, inplace=True)
        df_sh_sz_last['sz_amount_total_last'] = df_sz399001_last['amount_total']
        df_sh_sz_last['sh_sz_amount_total_last'] = df_sh000001_last['amount_total'] + df_sz399001_last['amount_total']

        df_sh000001, df_sz399001 , df_sh000016 = self.get_today_data()
        df_sh_sz = df_sh000001.copy()
        df_sh_sz['sh_sz_amount_total'] = df_sh000001['amount_total'] + df_sz399001['amount_total']
        df_sh_sz['sh_sz_amount_total_change'] = df_sh_sz['sh_sz_amount_total'] - df_sh_sz_last.head(len(df_sh_sz))['sh_sz_amount_total_last']

        # 填充首行的 NaN 值（可选，设为 0 或其他值）
        df_sh_sz['sh_sz_amount_total_change_diff'] = df_sh_sz['sh_sz_amount_total_change'].diff().fillna(0)

        df_sh_sz['sh_sz_amount_total_change_diff'] = round(df_sh_sz['sh_sz_amount_total_change_diff']/100000000, 2)
        df_sh_sz['sh_sz_amount_total_change'] = round(df_sh_sz['sh_sz_amount_total_change']/100000000, 2)
        df_sh_sz['sh_sz_amount_total_last'] = round(df_sh_sz_last['sh_sz_amount_total_last']/100000000, 2)
        df_sh_sz['sh_sz_amount_total'] = round(df_sh_sz['sh_sz_amount_total']/100000000, 2)
        return df_sh_sz

    def save_data(self):
        sh000001 = xueqiu_api.get_realtime_data_from_xueqiu("sh000001")
        sz399001 = xueqiu_api.get_realtime_data_from_xueqiu("sz399001")
        sh000016 = xueqiu_api.get_realtime_data_from_xueqiu("sh000016")
        sh000300 = xueqiu_api.get_realtime_data_from_xueqiu("sh000300")
        if len(json.loads(sh000001)["data"]["items"]) == 242:
            data = {
                "sh000001":  sh000001,
                "sz399001":  sz399001,
                "sh000016":  sh000016,
                "sh000300":  sh000300
            }
            import os
            filename = f"last_data_{time.strftime('%Y_%m_%d',time.localtime())}.json"
            if os.path.isfile(filename):
                print("文件已存在不用再保存了")
                return
            with open(filename, "w") as f:
                json.dump(data, f)

import time
def stampToTime(stamp): #时间转换
    datatime = time.strftime("%H:%M",time.localtime(float(str(stamp)[0:10])))
    return datatime


if __name__ == '__main__':
    # save_data()
    # print(load_last_data())
    # print(get_today_data())
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
    window = MainWindow()
    window.setWindowIcon(QIcon(':/icons/Icons/information.png'))
    window.show()
    sys.exit(app.exec())