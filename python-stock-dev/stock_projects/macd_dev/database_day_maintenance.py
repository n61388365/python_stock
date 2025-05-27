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
    stock_code = '688775'
    print(_save_stock_day_data(stock_code,False,'sina'))


def init_all_A_stocks_day_data():
    '''
    从0开始建日线数据库
    '''
    failed_list = []
    stock_code_list = file_utils.get_all_stocks_list()
    log.info(f"total {len(stock_code_list)} stocks")
    start_time = time.localtime()
    
    step = 1000
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


if __name__ == '__main__':

    init_all_A_stocks_day_data()

    # test_save_stock_day_data()
