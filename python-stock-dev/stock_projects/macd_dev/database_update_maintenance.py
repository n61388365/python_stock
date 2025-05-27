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
    log.info(f'从网络获取 {stock_code} 数据')
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
    log.info(f'保存 {stock_code} 数据成功')
    return stock_code, '保存成功', '数据保存成功'


def test_save_stock_5min_data():
    stock_code = '002697'
    print('save',_save_stock_5min_data(stock_code,False,'eastmoney'))
    print('veri',verify_5min_stock_data(stock_code,False))


def init_all_A_stocks_5min_data():
    failed_list = []
    stock_code_list = file_utils.get_all_stocks_list()
    log.info(f"total {len(stock_code_list)} stocks")
    for seg in range(int(len(stock_code_list)/10)+1):
        if len(stock_code_list)-seg*10 < 10:
            seg_list = stock_code_list[seg*10:]
        else:
            seg_list = stock_code_list[seg*10:seg*10+10]
        log.info(f"round {seg} {seg_list}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if seg % 2:
                result = executor.map(lambda code: _save_stock_5min_data(code,False,'eastmoney'),seg_list)
            else:
                result = executor.map(lambda code: _save_stock_5min_data(code,True,'eastmoney'),seg_list)

        for res in result:
            if res[1] != '保存成功':
                log.error(res)
                failed_list.append(res)
    
    for stock in failed_list:
        print(stock)


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
    stock_code = '001390'
    print(_save_stock_day_data(stock_code,False,'sina'))


def init_all_A_stocks_day_data():
    '''
    从0开始建日线数据库
    '''
    failed_list = []
    stock_code_list = file_utils.get_all_stocks_list()
    log.info(f"total {len(stock_code_list)} stocks")
    
    for seg in range(int(len(stock_code_list)/10)+1):
        if len(stock_code_list)-seg*10 < 10:
            seg_list = stock_code_list[seg*10:]
        else:
            seg_list = stock_code_list[seg*10:seg*10+10]
        log.info(f"round {seg} {seg_list}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if seg % 2:
                result = executor.map(lambda code: _save_stock_day_data(code,False,'eastmoney'),seg_list)
            else:
                result = executor.map(lambda code: _save_stock_day_data(code,True,'eastmoney'),seg_list)

        
        for res in result:
            if res[1] != '保存成功':
                log.error(res)
                failed_list.append(res)
    
    for stock in failed_list:
        print(stock)


def update_5min_stock_data(stock_code:str,proxy_flag:bool,vendor:str):
    correct_end_time = time.strftime('%Y-%m-%d 15:00',time.localtime())
    # correct_end_time = '2025-05-30 15:00'

    # 数据库更新前的数据
    df_before = database_utils.load_A_stock_5min_data(stock_code)
    if df_before is None:
        return stock_code, '更新失败', '数据库错误'
    end_time_before = df_before.iloc[-1,0]
    if end_time_before == correct_end_time:
        return stock_code, '已更新', f'{end_time_before}, {correct_end_time}'

    # 从网络获取5分钟数据
    if vendor == 'eastmoney':
        df_5min_net = net_utils.get_his_close_price_eastmoney(stock_code,5,proxy_flag)
    else:
        df_5min_net = net_utils.get_his_close_price_sina(stock_code,5,proxy_flag)
    if df_5min_net.empty:
        return stock_code, '更新失败', '网络错误' # 网络错误

    # 更新前数据与网络数据相同，无需要更新
    end_time_net = df_5min_net.iloc[-1,0]
    if end_time_before == end_time_net:
        return stock_code, '无须更新', f'停牌 {end_time_before}'

    # 求增量
    ## 先交集
    df_cross = pd.merge(df_5min_net,df_before, how='inner')
    ## 后差集
    df_minus = pd.concat([df_5min_net,df_cross]).drop_duplicates(keep=False)

    # 更新数据库
    database_utils.append_A_stock_5min_data(stock_code,df_minus)

    # 读取数据验证
    df_after = database_utils.load_A_stock_5min_data(stock_code)
    end_time_after = df_after.iloc[-1,0]
    if end_time_after == end_time_net:
        return stock_code, '更新成功', f'{end_time_net}' # 成功
    
    # 未成功更新
    return stock_code, '更新失败', f'net {end_time_net}, db {end_time_after}' # 数据库操作错误


def test_update_5min_stock_data():
    '''
    测试 停牌 无表
    '''
    stock_code = '603959' # 中科署光，已停牌
    print(update_5min_stock_data(stock_code,False))


def update_all_A_stocks_5min_data():
    stock_code_list = [stock.split(',')[0] for stock in file_utils.get_all_stocks_list()]
    log.info(f"total {len(stock_code_list)} stocks")
    all_update_failed = []
    for seg in range(int(len(stock_code_list)/10)+1):
        if len(stock_code_list) - seg*10 < 10:
            seg_list = stock_code_list[seg*10:]
        else:
            seg_list = stock_code_list[seg*10:seg*10+10]
        log.info(f"append round {seg} {seg_list}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if seg % 2 == 0:
                result = executor.map(lambda code: update_5min_stock_data(code,True,'eastmoney'),seg_list)
            if seg % 2 == 1:
                result = executor.map(lambda code: update_5min_stock_data(code,False,'eastmoney'),seg_list)

        for res in result:
            if res[1] != '更新成功':
                print(res)
            if res[1] == '更新失败':
                all_update_failed.append(res)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if seg % 2:
                result = executor.map(lambda code: verify_5min_stock_data(code,False),seg_list)
            else:
                result = executor.map(lambda code: verify_5min_stock_data(code,True),seg_list)

        for res in result:
            if res[1] != '更新成功':
                print(res)

    [print(res) for res in all_update_failed]


def verify_5min_stock_data(stock_code:str,proxy_flag:bool):
    correct_end_time = time.strftime('%Y-%m-%d 15:00',time.localtime())
    # correct_end_time = '2025-05-30 15:00'
    try:
        df = database_utils.load_A_stock_5min_data(stock_code)
        end_time = df.iloc[-1,0]
        if end_time != correct_end_time:
            df_net = net_utils.get_his_close_price_eastmoney(stock_code,5,proxy_flag)
            if df_net.iloc[-1,0] == end_time:
                return stock_code, '停牌', f'db {end_time} net {end_time}'
            else:
                return stock_code, '未更新' # 最后一条记录的时间不一致
        return stock_code, '更新成功', f'last time: {correct_end_time} vs last db time: {end_time}'
    except Exception as e:
        log.error(f"faile to get data from database {e}")
        return stock_code, '数据库错误'


def verify_all_A_stocks_5min_database():
    stock_code_list = [stock.split(',')[0] for stock in file_utils.get_all_stocks_list()]
    log.info(f"total {len(stock_code_list)} stocks")

    check_results = []

    for seg in range(int(len(stock_code_list)/10)+1):
        if len(stock_code_list) - seg*10 < 10:
            seg_list = stock_code_list[seg*10:]
        else:
            seg_list = stock_code_list[seg*10:seg*10+10]
        log.info(f"verify round {seg} {seg_list}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if seg % 2:
                result = executor.map(lambda code: verify_5min_stock_data(code,True),seg_list)
            else:
                result = executor.map(lambda code: verify_5min_stock_data(code,False),seg_list)

        for res in result:
            if res[1] != '更新成功':
                print(res)
                check_results.append(res)
    
    [print(res) for res in check_results]


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
    stock_code, date, price = ('000750','2025-05-24','3.74')
    print(update_day_stock_data(stock_code,date,price))


def test_update_day_stock_data_no_price():
    stock_code, date, price = ('000750','2025-05-24','--')
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
    stock_tuple_list = file_utils.get_all_stocks_tuple_list(date)
    rounds = int(len(stock_tuple_list)/20) + 1
    failure_list = []
    for round in range(rounds):
        if len(stock_tuple_list) - round*20 < 20:
            seg_list = stock_tuple_list[round*20:]
        else:
            seg_list = stock_tuple_list[round*20:round*20+20]
        log.info(f"append round {round} {[item[0] for item in seg_list]}")   
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            result = executor.map(lambda stock_tuple: update_day_stock_data(*stock_tuple), seg_list)
        for res in result:
            if res[1] != '更新成功':
                print(res)
            if res[1] == '更新失败':
                failure_list.append(res)
        log.info(f"verify round {round} {[item[0] for item in seg_list]}")   
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            result = executor.map(lambda stock_tuple: verify_day_stock_data(*stock_tuple), seg_list)
        for res in result:
            if res[1] != '更新成功':
                print(res)

    [print(item) for item in failure_list]


if __name__ == '__main__':

    init_all_A_stocks_5min_data()
    # update_all_A_stocks_5min_data()
    # verify_all_A_stocks_5min_database()
    # test_update_5min_stock_data()
    # test_save_stock_5min_data()

    # init_all_A_stocks_day_data()
    # update_all_A_stocks_day_data('2025-05-30')
    # save_stock_day_data_helper('002697',False,'eastmoney')

    # test_update_day_stock_data_no_price()
    # test_verify_day_stock_data_normal()

    # get_valid_all_stocks_day_data()
