import macd_utils
import utils.database_utils as database_utils
from utils import log


class StockMacd:
    def __init__(self, stock_code, freq_list):
        self.stock_code = stock_code
        # self.FREQ_LIST = [5,30,60,101,102,103]
        self.freq_list = freq_list
        self.bl_dict = {}
        self.bl = None # 1 底背离， 2 顶背离
        self.stock_data = {}
        self.close_price = None
        self._load_stock_data()
    
    def bl_detect(self):
        '''
        返回 dict
        {
            5: (0, None), 
            30: (1, -2.1072537149786186), 
            60: (1, -2.4123475263388983), 
            120: (0, None), 
            101: (0, None)}
        '''
        for freq in self.freq_list:
            bl, target_price = self._bl_detect(freq)
            # 1 底背离 2 顶背离
            self.bl = bl
            self.bl_dict.update({freq:(bl,target_price)})
        return self.bl_dict

    def _load_stock_data(self):
        '''
        {
            5: None,
            30: None,
            60: None,
            120: None,
            101: None,
            102: None,
            103: None
        }
        '''
        # 加载5分钟数据
        if 101 in self.freq_list:
            self.stock_data[101] = database_utils.load_A_stock_day_data(self.stock_code)
            self.close_price = float(self.stock_data[101]['收盘'].iloc[-1])
        else:
            self.stock_data[5] = database_utils.load_A_stock_5min_data(self.stock_code)
            self.stock_data[15] = self.stock_data[5][self.stock_data[5].index%3 == 2].reset_index().drop('index',axis=1)
            self.stock_data[30] = self.stock_data[5][self.stock_data[5].index%6 == 5].reset_index().drop('index',axis=1)
            self.stock_data[60] = self.stock_data[5][self.stock_data[5].index%12 == 11].reset_index().drop('index',axis=1)
            # list_90 = [idx for idx in range(len(self.stock_data[5])) if idx % 18 ==17]
            # if list_90[-1] != len(self.stock_data[5])-1:
            #     list_90.append(len(self.stock_data[5])-1)
            # self.stock_data[90] = self.stock_data[5].iloc[list_90].reset_index().drop('index',axis=1)
            self.stock_data[120] = self.stock_data[5][self.stock_data[5].index%24 == 23].reset_index().drop('index',axis=1)
            # 收盘价
            self.close_price = float(self.stock_data[5]['收盘'].iloc[-1])

    def _bl_detect(self, freq):
        log.debug(f"{self.stock_code} {freq}")
        # 生成 macd 数据
        stock_macd_data = macd_utils.compute_macd(self.stock_data[freq])
        # print(stock_macd_data)
        # 找出 金叉 死叉
        JC_list, SC_list = macd_utils.find_JC_SC_list(stock_macd_data)
        # print('金叉',JC_list)
        # print('死叉',SC_list)
        return macd_utils.bl_detect(stock_macd_data, JC_list, SC_list)


def test_stock_macd():
    # stock_000420 = StockMacd('000420')
    # stock = StockMacd('001390',[5])
    stock = StockMacd('000785',[60])
    print(stock.bl_detect())


if __name__ == '__main__':
    test_stock_macd()
