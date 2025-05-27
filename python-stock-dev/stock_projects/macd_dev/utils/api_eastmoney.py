import urllib.request
import json
import time
import threading
if __package__:
    from . import log
else:
    import log


# proxy_host_list = ['localhost:7789']
proxy_host_list = ['localhost:37890', 'localhost:7789', 'localhost:7890', 'localhost:10809']
# proxy_host_list = ['localhost:7789', 'localhost:7890']
call_count = 0
lock = threading.Lock()

def call_count_increase():
    lock.acquire()
    call_count = call_count + 1
    lock.release()


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
    global call_count
    '''
    功能：获取5分钟的历史K线
    返回：list of kindle
    '''
    # 5,30,60分钟 klt=5,30,60 101日线 102周线 103月线
    url_his_kindle = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&ut=7eea3edcaed734bea9cbfc24409ed989&klt={klt}&fqt=1&secid={_get_eastmoney_secid(stock_code)}&beg=0&end=20500000&_=1633082201530"
    req = urllib.request.Request(url_his_kindle)
    retry = 10
    while retry:
        response = None
        call_count = call_count + 1
        proxy_host = proxy_host_list[call_count%len(proxy_host_list)]
        if proxy_flag:
            if proxy_host:
                # proxy_host = 'localhost:7789'
                req.set_proxy(proxy_host,'http')
        log.debug(f'eastmoney {proxy_host} call count: {call_count} {stock_code}')
        try:
            response = urllib.request.urlopen(req,timeout=7)
            data=response.readline().decode().lstrip('data:')
            data_json = json.loads(data)
            response.close()
            return(data_json['data']['klines'])
        except Exception as e:
            retry = retry - 1
            log.error(f"{stock_code} {proxy_host} {e}, retry {10 - retry}, wait 5 second")
            if response:
                response.close()


def test_his_kindle():
    stock_code = '600363'
    log.info('begin')
    for row_data in get_his_kindle(stock_code,60,True):
        print(row_data)
    log.info('end')


if __name__ == '__main__':
    test_his_kindle()
    # test_his_kindle()