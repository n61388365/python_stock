#################################
## created 2025-05
## update 2025-05-27 周二 新股怎么办？

import sqlite3
import utils.net_utils as net_utils
import utils.database_utils as database_utils
import utils.file_utils as file_utils
from utils import log
import concurrent.futures
import pandas as pd
import time


def _save_stock_day_data(stock_code:str,proxy_flag:bool,vendor:str):
    '''
    从网络获取个股日线数据 存入数据库
    '''
    # 先判断表是否存在
    sql_cmd = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name = 'stock_{stock_code}_day';"
    with sqlite3.connect('stocks_day.db') as conn:
        cursor = conn.cursor()
        listOfTable = cursor.execute(sql_cmd).fetchall()
        if listOfTable[0][0]:
            log.error(f"stock_{stock_code}_day exist.")
            return stock_code, '未保存', '表已存在'
    log.info(f'从网络获取 {stock_code} 数据')
    if vendor == 'eastmoney':
        df = net_utils.get_his_close_price_eastmoney(stock_code,101,proxy_flag)
    else:
        df = net_utils.get_his_close_price_sina(stock_code,101,proxy_flag)
    if df.empty:
        log.error(f'网络获取 {stock_code} 数据失败')
        return stock_code, '未保存', f'网络获取数据失败'
    try:
        database_utils.save_A_stock_day_data(stock_code,df)
    except Exception as e:
        log.error(e)
        return stock_code, '未保存', '数据库错误'
    return stock_code, '保存成功', '数据保存成功'


def test_save_stock_day_data():
    stock_code = '301590'
    print(_save_stock_day_data(stock_code,False,'sina'))


def init_all_A_stocks_day_data():
    '''
    从0开始建日线数据库
    '''
    failed_list = []
    stock_code_list = file_utils.get_all_stocks_list()
    log.info(f"total {len(stock_code_list)} stocks")
    start_time = time.localtime()
    
    step = 30
    for seg in range(int(len(stock_code_list)/step)+1):
        if len(stock_code_list)-seg*step < step:
            seg_list = stock_code_list[seg*step:]
        else:
            seg_list = stock_code_list[seg*step:seg*step+step]
        log.info(f"round {seg} {seg_list}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = executor.map(lambda code: _save_stock_day_data(code,True,'eastmoney'),seg_list)

        for res in result:
            if res[1] != '保存成功':
                log.error(res)
                failed_list.append(res)
    
    for stock in failed_list:
        print(stock)

    log.info('start {}'.format(time.strftime('%H:%M:%S',start_time)))
    log.info('end of init day database')


def update_day_stock_data(stock_code, date, price):
    try:
        float(price)
    except Exception as e:
        log.error(e)
        return stock_code, '更新失败', '价格错误'

    df_before = database_utils.load_A_stock_day_data(stock_code)
    if df_before is None:
        return stock_code, '更新失败', '数据库错误'
    date_list = list(df_before.iloc[:,0])
    if date in date_list:
        return stock_code, '已更新', f'{date}, {price}' 

    df_dict = {
        '日期': [date],
        '收盘': [price]
    }
    df_new = pd.DataFrame(df_dict,columns=['日期','收盘'])
    database_utils.append_A_stock_day_data(stock_code,df_new)

    df_after = database_utils.load_A_stock_day_data(stock_code)

    # verification inside function
    if df_after.iloc[-1,0] == date and df_after.iloc[-1,1] == price:
        return stock_code, '更新成功', f'{date}, {price}'
    return stock_code, '更新失败', 'Uknown'


def test_update_day_stock_data_normal():
    stock_code, date, price = ('000750','2025-05-23','3.74')
    print(update_day_stock_data(stock_code,date,price))


def test_update_day_stock_data_no_price():
    stock_code, date, price = ('000750','2025-05-23','--')
    print(update_day_stock_data(stock_code,date,price))


def verify_day_stock_data(stock_code, date, price):
    try:
        float(price)
    except Exception as e:
        log.error(e)
        return stock_code, '未验证', f'价格错误 {date} {price}'
    df_database = database_utils.load_A_stock_day_data(stock_code)
    if df_database is None:
        return stock_code, '数据库错误', f'{date}, {price}'
    if df_database.iloc[-1,0] == date and df_database.iloc[-1,1] == price:
        return stock_code, '更新成功', f'{date}, {price}'
    else:
        return stock_code, '数据未更新', f'({df_database.iloc[-1,0]},{df_database.iloc[-1,1]}) vs ({date},{price})'


def test_verify_day_stock_data():
    stock_tuple = ('000750','2025-05-30','3.76')
    print(verify_day_stock_data(*stock_tuple))


def update_all_A_stocks_day_data(date):
    '''
    日线数据从同花顺导出，不从网络获取
    '''
    start_time = time.localtime()
    stock_tuple_list = file_utils.get_all_stocks_tuple_list(date)
    step = 40
    rounds = int(len(stock_tuple_list)/step) + 1
    failure_list = []
    for round in range(rounds):
        if len(stock_tuple_list) - round*step < step:
            seg_list = stock_tuple_list[round*step:]
        else:
            seg_list = stock_tuple_list[round*step:round*step+step]
        log.info(f"append round {round} {[item[0] for item in seg_list]}")   
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = executor.map(lambda stock_tuple: update_day_stock_data(*stock_tuple), seg_list)
        for res in result:
            if res[1] != '更新成功':
                print(res)
            if res[1] == '更新失败':
                failure_list.append(res)
        log.info(f"verify round {round} {[item[0] for item in seg_list]}")   
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = executor.map(lambda stock_tuple: verify_day_stock_data(*stock_tuple), seg_list)
        for res in result:
            if res[1] != '更新成功':
                print(res)

    [print(item) for item in failure_list]
    log.info('start time {}'.format(time.strftime("%H:%M:%S", start_time)))
    log.info('update all stocks day data ended')


if __name__ == '__main__':

    # init_all_A_stocks_day_data()
    update_all_A_stocks_day_data('2025-06-09')

    # test_save_stock_day_data()

    # test_update_day_stock_data_normal()
    # test_verify_day_stock_data_normal()
