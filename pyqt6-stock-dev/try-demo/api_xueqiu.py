# coding:utf-8
#
# @date: 26/02/26
#
# 盘口
# https://stock.xueqiu.com/v5/stock/realtime/pankou.json?symbol=SH600794
# https://stock.xueqiu.com/v5/stock/realtime/pankou.json?symbol=SZ300484


import requests
import log
import time
import json
import get_cookies_from_file


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"}
cookies = get_cookies_from_file.get_xueqiu_cookies()


def get_pankou_from_xueqiu(id):
    pankou_url = "https://stock.xueqiu.com/v5/stock/realtime/pankou.json?symbol=" + id
    retry = 10
    while retry:
        session = requests.Session()
        r1 = session.get(pankou_url, headers=headers, timeout=1, cookies=cookies)
        if r1.status_code == 200:
            return r1.text
        session.close()
        retry = retry - 1
        log.error("error from xueqiu, try {}".format(10 - retry))
        time.sleep(5)
    return ""


if __name__ == '__main__':
    output = json.loads(get_pankou_from_xueqiu("SH600794"))
    print(json.dumps(output, indent=4))
    # print(_get_cookie())
