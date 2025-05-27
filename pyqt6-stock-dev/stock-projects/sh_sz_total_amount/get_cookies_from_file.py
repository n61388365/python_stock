def get_cookies():
    with open('xueqiu_cookies.txt','r') as f:
        line = f.readline()
    cookie_string = line.rstrip()
    cookie_dict = {}
    for item in cookie_string.split("; "):
        key, value = item.split("=", 1)  # Split on first "=" only
        cookie_dict[key] = value
    return cookie_dict


if __name__ == '__main__':
    print(get_cookies())