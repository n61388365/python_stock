# https://github.com/uname-yang/pysnowball
#
# created 26/02/27 周五


import pysnowball as ball

ball.set_token("xq_a_token=c079e7210f60e9309743a78c216c05ca7d5cb8eb;u=9457486544")
print(ball.quote_detail('SZ002027')['data']["quote"]['last_close'])
