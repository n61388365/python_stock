if __package__:
    from . import api_eastmoney
    from . import api_sina_finance
    from . import log
else:
    import api_eastmoney
    import api_sina_finance
    import log

import pandas as pd

EASTMONEY_KLINE_FIELDS = {
    "f51": "日期",
    "f52": "开盘",
    "f53": "收盘",
    "f54": "最高",
    "f55": "最低",
    "f56": "成交量",
    "f57": "成交额",
    "f58": "振幅",
    "f59": "涨跌幅",
    "f60": "涨跌额",
    "f61": "换手率",
}


def get_his_close_price_eastmoney(stock_code='000750',klt=5,proxy_flag=False):
    '''
    返回历史数据
    '''
    json_data = api_eastmoney.get_his_kindle(stock_code,klt,proxy_flag)
    df = pd.DataFrame(
        [row.split(',') for row in json_data],
        columns=list(EASTMONEY_KLINE_FIELDS.values())
    )
    return df.loc[:,['日期','收盘']]


def get_his_close_price_sina(stock_code='000750',klt=5,proxy_flag=False):
    '''
    从sina获取的是list
    {
        "day": "2025-05-23 14:45:00",
        "open": "3.770",
        "high": "3.770",
        "low": "3.760",
        "close": "3.760",
        "volume": "1361600",
        "ma_price5": 3.762,
        "ma_volume5": 1466432
    }
    '''
    json_data = api_sina_finance.get_his_kindle(stock_code,klt,proxy_flag)
    if json_data is None:
        return pd.DataFrame(columns=['日期','收盘'])
    df = pd.DataFrame(json_data)
    # 数据归一化
    df['日期'] = df['day'].map(lambda x: x[:-3])
    df['收盘'] = df['close'].map(lambda x: x[:-1])
    return df.loc[:,['日期','收盘']]


def test_get_his_close_price_eastmoney():
    print(get_his_close_price_eastmoney('001390',101,False))


def test_get_his_close_price_sina():
    print(get_his_close_price_sina('301191',5,False))
    # print(get_his_close_price_sina('001390',101,False))


if __name__ == '__main__':
    test_get_his_close_price_eastmoney()
    # test_get_his_close_price_sina()