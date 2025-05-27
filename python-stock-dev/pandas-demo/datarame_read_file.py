import pandas as pd


df = pd.read_table('five_minutes_fix.txt')

print(df)
print(list(df['代码']))
