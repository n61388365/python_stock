################################################
# 2025-05-30 周五 普通的api会被反爬虫，需要用scrapy
#


import urllib.request
import json
import time

if __package__:
    from . import log
else:
    import log


proxy_host = 'localhost:7789'


## eastmoney secid
def _get_sina_symbol(stock='000750'):
    '''
    内部使用 深票加0. 沪票加1.
    '''
    if stock[0] == '6':
        return f"sh{stock}"
    return f"sz{stock}"


## 历史分钟日线
## https://php-note.com/2045.html
def get_his_kindle(stock_code='000750',klt=5,proxy_flag=False):
    '''
    功能：获取5分钟的历史K线
    返回：list of kindle
    '''
    log.info(f'loading {stock_code} from sina')

    # 5,30,60分钟 klt=5,30,60 240日线 1200周线 103月线
    klt_dict = {5:5,60:60,101:240,102:1200}
    url_his_kindle = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={_get_sina_symbol(stock_code)}&scale={klt_dict[klt]}&ma=5"
    req = urllib.request.Request(url_his_kindle)
    log.debug(url_his_kindle)
    if proxy_flag:
        req.set_proxy(proxy_host,'http')
    retry = 10
    try:
        while retry:
            response = urllib.request.urlopen(req)
            data=response.readline().decode().lstrip('data:')
            data_json = json.loads(data)
            log.debug(data_json)
            return(data_json)
    except Exception as e:
        retry = retry - 1
        log.error(f"{e}, retry {10 - retry}, wait 5 second")
        time.sleep(5)


def test_his_kindle():
    stock_code = '603049'
    print(len(get_his_kindle(stock_code,60,False)))
    print(get_his_kindle(stock_code,60,False))


if __name__ == '__main__':
    test_his_kindle()