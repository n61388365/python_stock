######################################
# 2025-05-28 周三 
# 将同花顺导出的每日收盘数据转为 dataframe

import pandas as pd
if __package__:
    from . import log
else:
    import log


def _get_stocks_df():
    df = pd.read_table('table.txt')
    df_today = df.drop(df.columns[[4]],axis=1)
    df_today['代码'] = df_today['代码'].apply(lambda x:x[2:])
    return df_today


def _get_stocks_list_from_df(df:pd.DataFrame):
    return list(df.iloc[:,0])


def _get_stocks_triple_list_from_df(df:pd.DataFrame,date:str):
    df['日期'] = date
    df['tuple'] = df[['代码','日期','现价','昨收']].apply(tuple,axis=1)
    return(list(df.iloc[:,5]))


def get_all_stocks_list():
    df = _get_stocks_df()
    return _get_stocks_list_from_df(df)


def get_all_stocks_tuple_list(date):
    df = _get_stocks_df()
    return _get_stocks_triple_list_from_df(df,date)


def get_under_6_stocks_list():
    df = pd.read_table('table_6.txt')
    df_today = df.drop(df.columns[[3]],axis=1)
    df_today['代码'] = df_today['代码'].apply(lambda x:x[2:])
    return list(df_today.iloc[:,0])


def get_5_min_fix_list():
    df = pd.read_table('five_minutes_fix.txt')
    return list(df['代码'].astype(str))


if __name__ == '__main__':
    print(get_all_stocks_tuple_list('2025-05-28'))
    # print(get_under_6_stocks_list())
