######################################
# 2025-05-28 周三 
# 将同花顺导出的每日收盘数据转为 dataframe


import pandas as pd

def get_stocks_df():
    df = pd.read_table('table.txt')
    df_today = df.drop(df.columns[[3]],axis=1)
    df_today['代码'] = df_today['代码'].apply(lambda x:x[2:])
    return df_today


def get_stocks_list_from_df(df:pd.DataFrame):
    return list(df.iloc[:,0])


def test_get_stocks_list_from_df():
    df = get_stocks_df()
    print(get_stocks_list_from_df(df))


if __name__ == '__main__':
    test_get_stocks_list_from_df()
