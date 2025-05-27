# coding:utf-8
#
# @date: 2024-07-19


xueqiu_web_url = "https://xueqiu.com/S/SH000001"
web_urls = {
    "sh000001_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SH000001&period=1d",  # 上证指数
    "sh000016_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SH000016&period=1d",  # 上证50
    "sh000300_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SH000300&period=1d",  # 沪深300
    "sz399001_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SZ399001&period=1d",  # 深证成指
    "sz399303_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SZ399303&period=1d",  # 国证2000
    "sh510310_minutes": "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SH510310&period=1d"   # 沪深300ETF易方达
}

name_id_map = {
    "上证指数": "sh000001",
    "上证50": "sh000016",
    "沪深300": "sh000300",
    "深证成指": "sz399001",
    "国证2000": "sz399303",
    "沪深300ETF易方达": "sh510310"
}