import urllib.request
import json
import time
if __package__:
    from . import log
else:
    import log


proxy_host = 'localhost:7789'


## eastmoney secid
def _get_eastmoney_secid(stock='000750'):
    '''
    内部使用 深票加0. 沪票加1.
    '''
    if stock[0] == '6':
        return f"1.{stock}"
    return f"0.{stock}"


## 历史分钟日线
## https://php-note.com/2045.html
def get_his_kindle(stock_code='000750',klt=101,proxy_flag=False):
    '''
    功能：获取5分钟的历史K线
    返回：list of kindle
    '''
    # 5,30,60分钟 klt=5,30,60 101日线 102周线 103月线
    url_his_kindle = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&ut=7eea3edcaed734bea9cbfc24409ed989&klt={klt}&fqt=1&secid={_get_eastmoney_secid(stock_code)}&beg=0&end=20500000&_=1633082201530"
    req = urllib.request.Request(url_his_kindle)
    if proxy_flag:
        req.set_proxy(proxy_host,'http')
    retry = 10
    while retry:
        try:
            response = urllib.request.urlopen(req)
            data=response.readline().decode().lstrip('data:')
            data_json = json.loads(data)
            return(data_json['data']['klines'])
        except Exception as e:
            retry = retry - 1
            log.error(f"{e}, retry {10 - retry}, wait 5 second")
            time.sleep(5)


def test_his_kindle():
    stock_code = '300065'
    print(get_his_kindle(stock_code,102,True))


if __name__ == '__main__':
    test_his_kindle()