## 东方财富 交易明细转 pandas dataframe

import urllib.request
import pandas as pd
import json


def get_today_ticks():

    url='http://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&pos=-0&secid=0.000750'

    # get data from eastmoney
    with urllib.request.urlopen(url=url) as r:
        data=r.readline().decode().lstrip('data:')
        data_json = json.loads(data)
        print(data_json['data']['details'])

    # Convert data to DataFrame
    df = pd.DataFrame([row.split(',') for row in data_json['data']['details']], 
                    columns=['Time', 'Price', 'Volume', 'Metric', 'Type'])

    # Convert columns to appropriate types
    df['Time'] = df['Time'].map(lambda x: str(x).zfill(6))
    df['Price'] = df['Price'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df['Type'] = df['Type'].astype(int)

    print(df)

if __name__ == '__main__':
    get_today_ticks()
