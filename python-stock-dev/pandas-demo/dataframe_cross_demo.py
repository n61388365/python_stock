# https://blog.csdn.net/ljp1919/article/details/107165778

import pandas as pd
import numpy as np
 
#Create a DataFrame
data1 = { \
    'Subject':['semester1','semester2','semester3','semester4','semester1','semester2','semester3'], \
    'Score':[62,47,55,74,31,77,85] \
}
 
df2 = {
    'Subject':['semester1','semester2','semester3','semester4'],
    'Score':[90,47,85,74]
}

 
df1 = pd.DataFrame(data1,columns=['Subject','Score'])
df2 = pd.DataFrame(df2,columns=['Subject','Score'])
 
# print(df1)
# print(df2)

# # 交集
# intersected_df = pd.merge(df1, df2, how='inner')
# print(intersected_df)

# df2 - df1
set_diff_df = pd.concat([df2, df1]).drop_duplicates(keep=False)
print(set_diff_df)

# print(df1.drop_duplicates(subset=['Subject'],keep=False))
