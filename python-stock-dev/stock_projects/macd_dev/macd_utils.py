import ta
import ta.trend
import utils.net_utils as net_utils
import utils.database_utils as db_utils
import pandas as pd
from utils import log
import traceback


def compute_macd(stock_data:pd.DataFrame):
    '''
    返回macd的计算结果
    '''
    stock_data_new = stock_data.copy()
    macd_obj = ta.trend.MACD(stock_data_new['收盘'])
    stock_data_new['DIF'] = macd_obj.macd()*100
    stock_data_new['DEA'] = macd_obj.macd_signal()*100
    stock_data_new['MACD'] = macd_obj.macd_diff()*200
    return stock_data_new


def find_JC_SC_list(stock_data :pd.DataFrame):
    '''
    输入是算过macd的数据
    '''
    JC = []
    SC = []
    for idx, row in stock_data[:-1].iterrows():
        idx_next = idx + 1
        row_next = stock_data.iloc[idx_next]
        if row['MACD'] < 0 and row_next['MACD'] > 0:
            JC.append(idx_next)
        if row['MACD'] > 0 and row_next['MACD'] < 0:
            SC.append(idx_next)
    log.debug(f"金叉 {JC}")
    log.debug(f"死叉 {SC}")
    return JC, SC


def bl_detect(stock_data :pd.DataFrame, JC_list, SC_list):
    '''
    返回 底背离 1，顶背离 2
    '''

    DINGBL = False
    DIBL =False
    target_dif = None
    try:
        # str to float
        stock_data['收盘'] = stock_data['收盘'].astype(float)
        # 判断底背离
        if stock_data.iloc[-1]['MACD'] < 0:
            # 当前绿区最低价
            close_lowest_0 = stock_data.iloc[SC_list[-1]:]['收盘'].min()
            dif_lowest_0 = stock_data.iloc[SC_list[-1]:]['DIF'].min()
            log.debug('当前区间最低价 {} {}'.format(close_lowest_0, dif_lowest_0))
            # 前一绿区最低价
            close_lowest_1 = stock_data.iloc[SC_list[-2]:JC_list[-1]]['收盘'].min()
            dif_lowest_1 = stock_data.iloc[SC_list[-2]:JC_list[-1]]['DIF'].min()
            log.debug('上一区间最低价 {} {}'.format(close_lowest_1, dif_lowest_1))
            # 前二绿区最低价
            close_lowest_2 = stock_data.iloc[SC_list[-3]:JC_list[-2]]['收盘'].min()
            dif_lowest_2 = stock_data.iloc[SC_list[-3]:JC_list[-2]]['DIF'].min()
            log.debug('上一区间最低价 {} {}'.format(close_lowest_2, dif_lowest_2))

            
            if close_lowest_0<close_lowest_1 and dif_lowest_0>dif_lowest_1:
                log.debug("直接底背离")
                target_dif = dif_lowest_1
                DIBL = True
            if close_lowest_0<close_lowest_1 and dif_lowest_0<dif_lowest_1 \
                and close_lowest_0<close_lowest_2 and dif_lowest_0>dif_lowest_2:
                log.debug("间接底背离")
                target_dif = dif_lowest_2
                DIBL = True

        # 判断顶背离
        if stock_data.iloc[-1]['MACD'] > 0:
            # 当前红区最高价
            close_highest_0 = stock_data.iloc[JC_list[-1]:]['收盘'].max()
            dif_highest_0 = stock_data.iloc[JC_list[-1]:]['DIF'].max()
            log.debug('当前区间最高价 {} {}'.format(close_highest_0, dif_highest_0))
            # 前一红区最高价
            close_highest_1 = stock_data.iloc[JC_list[-2]:SC_list[-1]]['收盘'].max()
            dif_highest_1 = stock_data.iloc[JC_list[-2]:SC_list[-1]]['DIF'].max()
            log.debug('上一区间最高价 {} {}'.format(close_highest_1, dif_highest_1))
            # 前二红区最高价
            close_highest_2 = stock_data.iloc[JC_list[-3]:SC_list[-2]]['收盘'].max()
            dif_highest_2 = stock_data.iloc[JC_list[-3]:SC_list[-2]]['DIF'].max()
            log.debug('上二区间最高价 {} {}'.format(close_highest_2, dif_highest_2))

            if close_highest_0>close_highest_1 and dif_highest_0<dif_highest_1:
                log.debug("直接顶背离")
                target_dif = dif_highest_1
                DINGBL = True
            if close_highest_0>close_highest_1 and dif_highest_0>dif_highest_1 \
                and close_highest_0>close_highest_2 and dif_highest_0<dif_highest_2:
                log.debug("间接顶背离")
                target_dif = dif_highest_2
                DINGBL = True

        return (DIBL and 1 or 0) + (DINGBL and 2 or 0), target_dif and f'{target_dif:.3f}'
    except Exception as e:
        log.error(traceback.format_exc())
        return 0, None


def fake_close_price_to_macd(fake_price, stock_data: pd.DataFrame):
    '''
    输入为原生的stock_data,不能用算过macd的data
    '''
    alist = [pd.NA,fake_price]
    stock_data.loc[len(stock_data)] = alist
    print(compute_macd(stock_data))


def test_compute_macd(stock_code='000750',klt=5):
    stock_data = net_utils.get_his_close_price_eastmoney(stock_code,klt)
    print(compute_macd(stock_data).iloc[-2:-1])


def test_find_JC_SC(stock_code='000750',klt=5):
    stock_data = net_utils.get_his_close_price_eastmoney(stock_code,klt)
    find_JC_SC_list(compute_macd(stock_data))


def test_bl_detect(stock_code='000750',klt=5):
    stock_data = net_utils.get_his_close_price_eastmoney(stock_code,klt)
    # stock_data_5min = db_utils.load_A_stock_5min_data(stock_code)
    # stock_data = stock_data_5min[stock_data_5min.index%24 == 23].reset_index().drop('index',axis=1)
    print(stock_data)
    stock_data_macd = compute_macd(stock_data)
    print(stock_data_macd)
    JC, SC = find_JC_SC_list(stock_data_macd)
    print(f"金叉 {JC}")
    print(f"死叉 {SC}")
    bl, target_dif = bl_detect(stock_data_macd, JC, SC)
    print(bl,target_dif)


def test_fake_close_price_to_macd(stock_code='000750',klt=5):
    fake_price = 5.1
    stock_data = net_utils.get_his_close_price_eastmoney(stock_code,klt)
    print(stock_data)
    fake_close_price_to_macd(fake_price, stock_data)


if __name__ == '__main__':
    # stock_code = '000750'
    # stock_test = ('600782',60) # 60分钟底钝
    stock_test = ('600368',60)
    # test_compute_macd()
    # test_find_JC_SC()
    test_bl_detect(*stock_test)
    # test_fake_close_price_to_macd(stock_code=stock_test[0],klt=stock_test[1])
