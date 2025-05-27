######################################
# 2025-05-28 周三 
# 将同花顺导出的每日收盘数据转为 dataframe

import re
from pypinyin import pinyin, Style
import pandas as pd

def get_stocks_df():
    df = pd.read_table('table.txt')
    df_today = df.drop(df.columns[[3]],axis=1)
    return df_today


def get_pinyin_list_from_df(df:pd.DataFrame):
    qt6_pinyin_list = [""]
    for idx, row in df.iterrows():
        stock_code = row[0][2:]
        stock_name = row[1]
        stock_price = row[2]
        print(stock_code,stock_name,stock_price)
        # 去除 *ST 等非汉字前缀
        clean_name = re.sub(r'^\*ST|\s+', '', stock_name)
        # 获取拼音
        pinyin_list = pinyin(clean_name, style=Style.NORMAL)
        # 提取首字母
        initials = ""
        for p in pinyin_list:
            if p[0]:  # 确保拼音不为空
                initial = p[0][0].upper()  # 取拼音的第一个字母，大写
                initials += initial
        # 写入一行
        qt6_pinyin_list.append(",".join([stock_code, stock_name, initials]))
    return qt6_pinyin_list


def get_combobox_list():
    df_stocks = get_stocks_df()
    return get_pinyin_list_from_df(df_stocks)


def test_get_pinyin_list_from_df():
    df_stocks = get_stocks_df()
    print(df_stocks)
    get_pinyin_list_from_df(df_stocks)


if __name__ == '__main__':
    test_get_pinyin_list_from_df()