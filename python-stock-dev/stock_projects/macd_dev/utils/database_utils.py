####################################
## update 2025-05-27 周二 添加 test_load_A_stock_5min_data


import sqlite3
import pandas as pd
import traceback

if __package__:
    from . import log
else:
    import log


# 5分钟
def load_A_stock_5min_data(stock_code):
    try:
        query = f"SELECT * FROM stock_{stock_code}_005"
        with sqlite3.connect('stocks_005.db') as conn:
            result_df = pd.read_sql(query, conn)
        return result_df
    except Exception as e:
        log.error(e)
        return


def test_load_A_stock_5min_data():
    '''
    测试查询不存在的表
    '''
    stock_code = '000000'
    try:
        print(load_A_stock_5min_data(stock_code))
    except Exception as e:
        print(traceback.format_exc())


def save_A_stock_5min_data(stock_code, df):
    with sqlite3.connect('stocks_005.db') as conn:
        df.to_sql(f'stock_{stock_code}_005',conn,if_exists='replace',index=False)
    log.info('saved 5min {}'.format(stock_code))


def append_A_stock_5min_data(stock_code, df):
    with sqlite3.connect('stocks_005.db') as conn:
        df.to_sql(f'stock_{stock_code}_005',conn,if_exists='append',index=False)


def get_5min_records_count(stock_code):
    try:
        with sqlite3.connect('stocks_005.db') as conn:
            sql_cmd = f"SELECT COUNT(*) FROM stock_{stock_code}_005"
            cursor = conn.cursor()
            return cursor.execute(sql_cmd).fetchall()[0][0]
    except:
        return


def get_5min_last_record(stock_code):
    with sqlite3.connect('stocks_005.db') as conn:
        sql_cmd = f"SELECT * FROM stock_{stock_code}_005 ORDER by ROWID DESC LIMIT 1"
        cursor = conn.cursor()
        return cursor.execute(sql_cmd).fetchall()[0]


# day
def load_A_stock_day_data(stock_code):
    try:
        query = f"SELECT * FROM stock_{stock_code}_day"
        with sqlite3.connect('stocks_day.db') as conn:
            result_df = pd.read_sql(query, conn)
        return result_df
    except Exception as e:
        log.error(e)
        return


def save_A_stock_day_data(stock_code, df):
    with sqlite3.connect('stocks_day.db') as conn:
        df.to_sql(f'stock_{stock_code}_day',conn,if_exists='replace',index=False)
    log.info(f"saved day {stock_code}")


def append_A_stock_day_data(stock_code, df):
    with sqlite3.connect('stocks_day.db') as conn:
        df.to_sql(f'stock_{stock_code}_day',conn,if_exists='append',index=False)


# week database
def load_A_stock_week_data(stock_code):
    query = f"SELECT * FROM stock_{stock_code}_week"
    with sqlite3.connect('stocks_week.db') as conn:
        result_df = pd.read_sql(query, conn)
    return result_df


def save_A_stock_week_data(stock_code, df):
    with sqlite3.connect('stocks_week.db') as conn:
        df.to_sql(f'stock_{stock_code}_week',conn,if_exists='replace',index=False)
    log.info(f"saved week {stock_code}")


def test_load_A_stock_week_data():
    print(load_A_stock_week_data('002373'))


if __name__ == '__main__':
    print(load_A_stock_day_data('600300'))

