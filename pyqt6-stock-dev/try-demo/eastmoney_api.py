import urllib.request
import json


## https://youle.zhipin.com/articles/65dc904f019f799fqxB73tm1EA~~.html
## 成交明细

def get_transaction_details():

    url='http://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&pos=-0&secid=0.300026'

    with urllib.request.urlopen(url=url) as r:
        data=r.readline().decode().lstrip('data:')
        data_json = json.loads(data)
        return(data_json['data']['details'])


## https://blog.csdn.net/meiaoxue1234/article/details/122859077
# 实时盘口

url_pk = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secid=0.000750'

def get_realtime_ticks(stock_code):
    # 深证 0. + 000750，上证 1. + 601568
    stock_code = stock_code.startswith('6') and '1.{}'.format(stock_code) or '0.{}'.format(stock_code)
    url = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secid={}'.format(stock_code)
    print(url)
    with urllib.request.urlopen(url=url) as r:
        data=r.readline().decode().lstrip('data:')
        data_json = json.loads(data)
        return data_json['data']


if __name__ == '__main__':
    print(get_transaction_details())
