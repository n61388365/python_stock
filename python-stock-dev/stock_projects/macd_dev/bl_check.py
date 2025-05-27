from utils import log
import stock_macd
import concurrent.futures
import utils.file_utils as file_utils
import threading


dibl_list = []
dingbl_list = []
lock = threading.Lock()

FREQ_LIST = [101]

def handle_single_stock(stock_code):
    global dibl_list
    global dingbl_list
    stock = stock_macd.StockMacd(stock_code,FREQ_LIST)
    bl_dict = stock.bl_detect()
    log.info(f"{stock_code} {bl_dict}")
    with lock:
        if stock.bl == 1:
            dibl_list.append((stock_code, bl_dict))
        if stock.bl == 2:
            dingbl_list.append((stock_code, bl_dict))


def bl_check():
    stock_code_list = file_utils.get_under_6_stocks_list()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda code: handle_single_stock(code), stock_code_list)
    log.info("底背离列表")
    for item in dibl_list:
        print(item)
    with open(f'dibl_{FREQ_LIST[0]}.txt', 'w') as f:
        f.write("\n".join([item[0] for item in dibl_list]))
    log.info("顶背离列表")
    for item in dingbl_list:
        print(item)


if __name__ == '__main__':
    bl_check()