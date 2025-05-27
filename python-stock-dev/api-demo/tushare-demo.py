# coding: utf-8

# update 2022-12-05
# change back to pro_bar, use tushare.pro_api(TOKEN) solve the connection issue

# update 2022-12-05
# tushare.pro_bar need high scores
# change interface to tushare.get_hist_data


import tushare
import datetime
import time


# tushare initialization
selector = 0
TOKEN_01 = "4563b71d2582929f061585a3b075a0bbca4a1ee1c6616259ef668fde"
TOKEN_02 = "fc087ee503a6feac6cf5dde3e409dc44613d395bab12a4c4470707a4"
token='b3252a4869a96c045a5111ed9f879b44bfcd0f02f2f84f9fe6d487a5'
TOKEN = selector and TOKEN_01 or TOKEN_02
tushare.set_token(TOKEN)
# tushare.pro_api(TOKEN)

# now
now = datetime.datetime.now()


tushare_code = "000750.SZ"

# tushare.pro_bar(ts_code="000750.SZ", adj='qfq', start_date='2025-01-01', end_date='2025-05-23')
# tushare.pro_bar(ts_code="000750.SZ", freq='30min', start_date='2025-01-01', end_date='2025-05-23')
# tushare.pro_bar(ts_code="600782.SH", freq='30min', start_date='2025-01-01', end_date='2025-05-23')
# tushare.pro_bar(ts_code="600782.SH", freq='90min', start_date='2025-01-01', end_date='2025-05-23')
# pro.stk_mins(ts_code='600782.SH', freq='1min', start_date='2025-05-23 09:00:00', end_date='2025-05-23 19:00:00')

def add_exchanger(code, vendor):
    if vendor == 'tushare':
        if code.startswith("6"):
            return code + ".SH"
        else:
            return code + ".SZ"
    else:
        if code.startswith("6"):
            return "SH" + code
        else:
            return "SZ" + code


def load_tushare_data(sdate, edate):
     """
     :return [(date, current price), ...]
     """
     print("loading {} data from tushare".format(tushare_code))

     df = tushare.pro_bar(ts_code=f'{tushare_code}', adj='qfq', start_date=sdate, end_date=edate)
     time.sleep(1)
     df_data_list = df.to_dict(orient='list')

     data = []
     for idx in range(len(df)):
         data.append((df_data_list['trade_date'][idx], df_data_list['close'][idx]))

     # return(data[-1::-1])
     return data


if __name__ == '__main__':
    print(load_tushare_data('2022-12-02'))

