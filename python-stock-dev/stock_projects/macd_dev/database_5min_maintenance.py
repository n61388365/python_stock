#################################
# created 2025-05
# update 
#  2025-05-27 周二 新股怎么办？
#  2025-06-03 周二 数据不一致校验

import sqlite3
import utils.net_utils as net_utils
import utils.database_utils as database_utils
import utils.file_utils as file_utils
from utils import log
import concurrent.futures
import pandas as pd
import time


correct_end_time = time.strftime('%Y-%m-%d 15:00',time.localtime())
# correct_end_time = '2025-06-06 15:00'
integrity_check = True


def _save_stock_5min_data(stock_code:str,proxy_flag:bool,vendor:str):
    try:
        # 判断表是否存在
        sql_cmd = f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name = 'stock_{stock_code}_005';"
        with sqlite3.connect('stocks_005.db') as conn:
            cursor = conn.cursor()
            listOfTable = cursor.execute(sql_cmd).fetchall()
            if listOfTable[0][0]:
                log.error(f"stock_{stock_code}_day exist.")
                return stock_code, '未保存', '表已存在'
    except Exception as e:
        log.error(e)
    log.debug(f'从网络获取 {stock_code} 数据')
    if vendor == 'eastmoney':
        df = net_utils.get_his_close_price_eastmoney(stock_code,5,proxy_flag)
    else:
        df = net_utils.get_his_close_price_sina(stock_code,5,proxy_flag)
    if df.empty:
        log.error(f'网络获取 {stock_code} 数据失败')
        return stock_code, '未保存', f'网络获取数据失败'
    try:
        database_utils.save_A_stock_5min_data(stock_code,df)
    except Exception as e:
        log.error(e)
        return stock_code, '未保存', '数据库错误'
    log.debug(f'保存 {stock_code} 数据成功')
    return stock_code, '保存成功', '数据保存成功'


def test_save_stock_5min_data():
    stock_code = '301590'
    print('save',_save_stock_5min_data(stock_code,False,'eastmoney'))


def init_all_A_stocks_5min_data():
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
            result = executor.map(lambda code: _save_stock_5min_data(code,True,'eastmoney'),seg_list)

        for res in result:
            if res[1] != '保存成功':
                log.error(res)
                failed_list.append(res)
    
    for stock in failed_list:
        print(stock)

    log.info('start {}'.format(time.strftime('%H:%M:%S', start_time)))
    log.info('end of init 5 min data')


def update_5min_stock_data(stock_code:str,proxy_flag:bool,vendor:str):
    global correct_end_time
    global integrity_check

    # 数据库更新前的数据
    records_count_before = database_utils.get_5min_records_count(stock_code)
    if not records_count_before:
        return _save_stock_5min_data(stock_code,True,'eastmoney')
    last_record = database_utils.get_5min_last_record(stock_code)

    if last_record[0] == correct_end_time:
        return stock_code, '已更新', f'db {correct_end_time}'
    # 从网络获取5分钟数据
    if vendor == 'eastmoney':
        df_5min_net = net_utils.get_his_close_price_eastmoney(stock_code,5,proxy_flag)
    else:
        df_5min_net = net_utils.get_his_close_price_sina(stock_code,5,proxy_flag)
    if df_5min_net.empty:
        return stock_code, '更新失败', '网络错误' # 网络错误

    # 更新前数据与网络数据相同，无需要更新
    end_time_net = df_5min_net.iloc[-1,0]
    end_price_net = df_5min_net.iloc[-1,1]
    if last_record[0] == end_time_net and last_record[1] == end_price_net:
        return stock_code, '无须更新', f'停牌 {end_time_net}'

    # 更新数据库前一致性校验
    if integrity_check:
        df_db = database_utils.load_A_stock_5min_data(stock_code)
        df_cross = pd.merge(df_db, df_5min_net, how='inner')
        if len(df_cross) % 48 != 0:
            df_minus = pd.concat([df_5min_net,df_cross]).drop_duplicates(keep=False)
            return stock_code, '更新失败', f'数据不一致 net {df_minus.iloc[0,0]} {df_minus.iloc[0,1]}'

    # 更新数据库
    database_utils.append_A_stock_5min_data(stock_code,df_5min_net[-48:])
    log.info(f'{stock_code} write database')

    # 读取数据验证
    data_count_after = database_utils.get_5min_records_count(stock_code)
    if data_count_after == records_count_before:
        return stock_code, '更新失败', '数据库操作失败'
    
    # 成功更新
    return stock_code, '更新成功', '数据库更新成功'


def test_update_5min_stock_data():
    '''
    测试 停牌 无表
    '''
    stock_code = '600905'
    print(update_5min_stock_data(stock_code,False,'eastmoney'))


def update_stocks_5min_data(stock_code_list):
    start_time = time.localtime()

    log.info(f"total {len(stock_code_list)} stocks")
    all_update_failed = []
    no_need_update = []
    step = 1000
    for seg in range(int(len(stock_code_list)/step)+1):
        if len(stock_code_list) - seg*step < step:
            seg_list = stock_code_list[seg*step:]
        else:
            seg_list = stock_code_list[seg*step:seg*step+step]
        log.info(f"append round {seg}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = executor.map(lambda code: update_5min_stock_data(code,True,'eastmoney'),seg_list)

        for res in result:
            if res[1] != '更新成功':
                print(res)
            if res[1] == '更新失败':
                all_update_failed.append(res)
            if res[1] == '无须更新':
                no_need_update.append(res)

    log.info('start time {}'.format(time.strftime("%H:%M:%S",start_time)))
    log.info('update 5 min data ended')    
    return all_update_failed, no_need_update


def update_all_A_stocks_5min_data():
    stock_code_list = file_utils.get_all_stocks_list()
    failed_stock_list, no_need_list = update_stocks_5min_data(stock_code_list)
    log.info('更新失败')
    [print(res) for res in failed_stock_list]
    log.info('停牌')
    [print(res) for res in no_need_list]
    while len(failed_stock_list) and len(failed_stock_list) != len(stock_code_list):
        stock_code_list = [res[0] for res in failed_stock_list]
        log.info('fix round: {}'.format(stock_code_list))
        failed_stock_list, _ = update_stocks_5min_data(stock_code_list)
    [print(res) for res in failed_stock_list]


def group_fix_5min_stocks_data():
    global integrity_check
    integrity_check = False
    stock_code_list = file_utils.get_5_min_fix_list()
    failed_stock_list, _ = update_stocks_5min_data(stock_code_list)
    [print(res) for res in failed_stock_list]


if __name__ == '__main__':

    init_all_A_stocks_5min_data()
    # update_all_A_stocks_5min_data()
    # group_fix_5min_stocks_data()

    # test_update_5min_stock_data()
    # test_save_stock_5min_data()
