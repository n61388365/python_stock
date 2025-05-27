###############################
#  2025-05-30 周五
#  错误描述: 只有两条数据的时候
#    (.venv) G:\workspace\pyqt6-stock-dev>G:/workspace/pyqt6-stock-dev/.venv/Scripts/python.exe g:/workspace/pyqt6-stock-dev/stock-projects/sh_sz_total_amount/volume_gap_check.py
#    I am here waiting for you
#           timestamp  amount_total  sh_sz_amount_total  sh_sz_amount_total_change  sh_sz_amount_total_change_diff  sh_sz_amount_total_last
#    0  1748568600000  1.968652e+10              564.21                     121.57                            0.00                   442.63
#    1  1748568660000  2.591950e+10              725.69                      89.35                          -32.23                   636.35
#    Traceback (most recent call last):
#      File "g:/workspace/pyqt6-stock-dev/stock-projects/sh_sz_total_amount/volume_gap_check.py", line 115, in set_analyze_timer
#        self.analyze_data_on_timer()
#      File "g:/workspace/pyqt6-stock-dev/stock-projects/sh_sz_total_amount/volume_gap_check.py", line 159, in analyze_data_on_timer
#        change_max_timestamp = sh_sz_calculated[sh_sz_calculated.sh_sz_amount_total_change == change_max_volume].iloc[0].timestamp
#      File "G:\workspace\pyqt6-stock-dev\.venv\lib\site-packages\pandas\core\indexing.py", line 1103, in __getitem__
#        return self._getitem_axis(maybe_callable, axis=axis)
#      File "G:\workspace\pyqt6-stock-dev\.venv\lib\site-packages\pandas\core\indexing.py", line 1656, in _getitem_axis
#        self._validate_integer(key, axis)
#      File "G:\workspace\pyqt6-stock-dev\.venv\lib\site-packages\pandas\core\indexing.py", line 1589, in _validate_integer
#        raise IndexError("single positional indexer is out-of-bounds")
#    IndexError: single positional indexer is out-of-bounds
#  解决方法:
#    两条数据的时候单独处理     

import pandas as pd
import time


my_dict = {
    'timestamp': [1748568600000,1748568660000],
    'amount_total': [1.968652e+10, 2.591950e+10],
    'sh_sz_amount_total': [564.21, 725.69],
    'sh_sz_amount_total_change': [121.57, 89.35],
    'sh_sz_amount_total_change_diff': [0.00, -32.23],
    'sh_sz_amount_total_last': [442.63, 636.35]
}

df = pd.DataFrame(my_dict)
df_no_last = df[0:-1]

# 取最后一行
last_row = df.iloc[-1]
change_max_volume = df[0:-1]['sh_sz_amount_total_change'][1:].max()

print(("{} {} minutes {}亿 {}亿".format(time.strftime("%H:%M:%S",time.localtime(float(str(last_row[0])[0:10]))), len(df), last_row[3], last_row[4])))