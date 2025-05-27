import urllib.request
import time
import json
 
 
def gupiaopankou_eastmoney(daima):
    """
    从东方财富网获取股票盘口实时数据
    :param daima: 股票代码
    :return:  盘口数据
    """
    if daima[:2] == "sh":
        lsbl = '1.'+daima[2:]
    else:
        lsbl = '0.' + daima[2:]
    wangzhi = 'http://push2.eastmoney.com/api/qt/stock/get?&fltt=2&invt=2&fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,' \
              'f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,' \
              'f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,' \
              'f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,' \
              'f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,' \
              'f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295&secid='+lsbl+ \
              '&_='+str(time.time())
 
    print(wangzhi)

    with urllib.request.urlopen(url=wangzhi) as r:
        data=r.readline().decode().lstrip('data:')
        data_json = json.loads(data)['data']
        print(data_json)

    pankou = {'代码': data_json['f57'], '名称': data_json['f58'], '开盘': data_json['f46'], '最高': data_json['f44'], '最低': data_json['f45'],
              '最新': data_json['f43'], '金额': data_json['f48'], '昨天收盘':data_json['f60'], 'timestamp':data_json['f86'],
              '卖1价': data_json['f39'], '卖1量': data_json['f40'], '卖2价': data_json['f37'], '卖2量': data_json['f38'],
              '卖3价': data_json['f35'], '卖3量': data_json['f36'], '卖4价': data_json['f33'], '卖4量': data_json['f34'],
              '卖5价': data_json['f31'], '卖5量': data_json['f32'],
              '买1价': data_json['f19'], '买1量': data_json['f20'], '买2价': data_json['f17'], '买2量': data_json['f18'],
              '买3价': data_json['f15'], '买3量': data_json['f16'], '买4价': data_json['f13'], '买4量': data_json['f14'],
              '买5价': data_json['f11'], '买5量': data_json['f12']
              }
    print(pankou)
    return pankou
 
 
if __name__ == '__main__':
    gupiaopankou_eastmoney('sz000750')
