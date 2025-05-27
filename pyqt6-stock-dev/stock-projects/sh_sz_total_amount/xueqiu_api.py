# coding:utf-8
#
# @date: 2024-07-18

import requests
import maps
import log
import time
import json
import get_cookies_from_file


# https://stock.xueqiu.com/v5/stock/quote.json?symbol=SH000001&extend=detail
# minutes_web_url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SH000001&begin=1721233755202&period=1m&type=before&count=-284&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
# sz_web_url = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SZ399001"
# sh_web_url = "https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SH000001"


# headers = {"User-Agent": "PostmanRuntime/7.28.4"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"}

# def _get_cookie():
#     session = requests.Session()
#     r = session.get(maps.xueqiu_web_url, headers=headers, timeout=1)
#     print(r.headers.get("set-cookie"))
#     print(dict(session.cookies))
#     return r.cookies
# cookies = _get_cookie()

# cookies = {
#     "cookiesu": "cookiesu=281716104716909; device_id=fb34a7259be5c082be9ae8fa5cd4a062; s=bf121fdjny; xq_is_login=1; u=9679143601; xq_a_token=d9bb48ddf2dbd49daeb1b18623252c03441183f5; xqat=d9bb48ddf2dbd49daeb1b18623252c03441183f5; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjk2NzkxNDM2MDEsImlzcyI6InVjIiwiZXhwIjoxNzQ5NzgwMDE0LCJjdG0iOjE3NDcxODgwMTQxNjUsImNpZCI6ImQ5ZDBuNEFadXAifQ.RGXyt1_3G81P3y0eG0CaZ2Aqn0uyZXURt96d0eT3OIrg35eqswoTnktfgl1qtQZz_xesqsj-eiVk581CiZnCWuyTVL68aKMZB99e21blYWJ-k2sy-WEEtAP1XzvjmBhs3usuu8TJ6RGYPb3SgvopY7SQeYkQVqmdXWYc_rZKzU0HmwEyrzTEiGkPRYJjKjFvtn8Sqw0NbNo5FbRXBEO4GygJwUdRvr-Jd-49Zogna9dCP32FvKi99Fh4bfwoMgVhq0zOe1wmumjijZbEdZKaO83NgHuWdxLfB8EmCRKXXNpGVXitQUzrvJUai1za2i_0hz-zhaYFSzvHvW7ql7DpiA; xq_r_token=7264bbfa0c6a216c31ab08572f1fced037f9f4bd; Hm_lvt_1db88642e346389874251b5a1eded6e3=1745723712,1747188015; HMACCOUNT=B7AB5909520D150A; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1747188572; ssxmod_itna=iqmhY540xjxG2EDhx+gDfOCheG7ndDXDUqAjtGgDYq7=GFYDCx7K8ci3GkKREWWUmu2DPW4=BDtDlx3WoDUg4iaDI3md+t02iBP3F7bYyxwuKQ0xuuEEiBRQpwOAC0C1tREnQ8cA2P4GLDY6vIhGiYidD44DvDBYD74G+DDeDixGmz4DS3xD9DGP3cjTN6eDEDYprxitxrxcaxDLbAnrFpDDBDD=xx7QWUnxD0q4YfTrKFPD+emcbl1uOF/d3x0tWDBLdR9x3uakU1inpv/LWaRrDzT1Dtuu8cny7UmnNTP2xW+Gx4rLP42P7RQl2xiuQ7iVA0ilxxbAqIrYIxxTii8BsnbKqxDGRszWdqG4QYeLu10kWNOzhixgks77s3hx3io+0dBx4ZidWihMA5VGxH0DtBiHBD5Yhg0=5Ss5iDD; ssxmod_itna2=iqmhY540xjxG2EDhx+gDfOCheG7ndDXDUqAjtGgDYq7=GFYDCx7K8ci3GkKREWWUmu2DPW4=BiYDiPRrAINhSnopxB9cM5wdKCii3754D"
# }
# cookies = {
#     "cookiesu": "281716104716909; device_id=fb34a7259be5c082be9ae8fa5cd4a062; s=bf121fdjny; xq_is_login=1; u=9679143601; xq_a_token=d9bb48ddf2dbd49daeb1b18623252c03441183f5; xqat=d9bb48ddf2dbd49daeb1b18623252c03441183f5; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjk2NzkxNDM2MDEsImlzcyI6InVjIiwiZXhwIjoxNzQ5NzgwMDE0LCJjdG0iOjE3NDcxODgwMTQxNjUsImNpZCI6ImQ5ZDBuNEFadXAifQ.RGXyt1_3G81P3y0eG0CaZ2Aqn0uyZXURt96d0eT3OIrg35eqswoTnktfgl1qtQZz_xesqsj-eiVk581CiZnCWuyTVL68aKMZB99e21blYWJ-k2sy-WEEtAP1XzvjmBhs3usuu8TJ6RGYPb3SgvopY7SQeYkQVqmdXWYc_rZKzU0HmwEyrzTEiGkPRYJjKjFvtn8Sqw0NbNo5FbRXBEO4GygJwUdRvr-Jd-49Zogna9dCP32FvKi99Fh4bfwoMgVhq0zOe1wmumjijZbEdZKaO83NgHuWdxLfB8EmCRKXXNpGVXitQUzrvJUai1za2i_0hz-zhaYFSzvHvW7ql7DpiA; xq_r_token=7264bbfa0c6a216c31ab08572f1fced037f9f4bd; Hm_lvt_1db88642e346389874251b5a1eded6e3=1745723712,1747188015; HMACCOUNT=B7AB5909520D150A; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1747188572; ssxmod_itna=iqmhY540xjxG2EDhx+gDfOCheG7ndDXDUqAjtGgDYq7=GFYDCx7K8ci3GkKREWWUmu2DPW4=BDtDlx3WoDUg4iaDI3md+t02iBP3F7bYyxwuKQ0xuuEEiBRQpwOAC0C1tREnQ8cA2P4GLDY6vIhGiYidD44DvDBYD74G+DDeDixGmz4DS3xD9DGP3cjTN6eDEDYprxitxrxcaxDLbAnrFpDDBDD=xx7QWUnxD0q4YfTrKFPD+emcbl1uOF/d3x0tWDBLdR9x3uakU1inpv/LWaRrDzT1Dtuu8cny7UmnNTP2xW+Gx4rLP42P7RQl2xiuQ7iVA0ilxxbAqIrYIxxTii8BsnbKqxDGRszWdqG4QYeLu10kWNOzhixgks77s3hx3io+0dBx4ZidWihMA5VGxH0DtBiHBD5Yhg0=5Ss5iDD; ssxmod_itna2=iqmhY540xjxG2EDhx+gDfOCheG7ndDXDUqAjtGgDYq7=GFYDCx7K8ci3GkKREWWUmu2DPW4=BiYDiPRrAINhSnopxB9cM5wdKCii3754D"
# }

cookies = get_cookies_from_file.get_cookies()


def get_realtime_data_from_xueqiu(id):
    id_minutes = "{}_minutes".format(id)
    retry = 10
    while retry:
        session = requests.Session()
        r1 = session.get(maps.web_urls[id_minutes], headers=headers, timeout=1, cookies=cookies)
        if r1.status_code == 200:
            return r1.text
        session.close()
        retry = retry - 1
        log.error("error from xueqiu, try {}".format(10 - retry))
        time.sleep(5)
    return ""


if __name__ == '__main__':
    output = json.loads(get_realtime_data_from_xueqiu("sh000001"))
    print(json.dumps(output, indent=4))
    # print(_get_cookie())
