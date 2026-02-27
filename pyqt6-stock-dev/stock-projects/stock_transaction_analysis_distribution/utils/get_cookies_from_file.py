def _get_cookies(file_name='cookies_xueqiu.txt'):
    with open(file_name,'r') as f:
        line = f.readline()
    cookie_string = line.rstrip()
    cookie_dict = {}
    for item in cookie_string.split("; "):
        key, value = item.split("=", 1)  # Split on first "=" only
        cookie_dict[key] = value
    return cookie_dict

def get_xueqiu_cookies():
    return _get_cookies()


def get_eastmoney_cookies():
    return _get_cookies('cookies_eastmoney.txt')


if __name__ == '__main__':
    print(get_xueqiu_cookies())
    # print(get_eastmoney_cookies())
