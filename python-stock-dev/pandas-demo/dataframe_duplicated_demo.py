import pandas as pd

data1 = { \
    'Subject':['semester1','semester2','semester3','semester4','semester1','semester2','semester3','semester3'], \
    'Score':[62,47,55,74,31,77,85,55] \
}

df1 = pd.DataFrame(data1)

# print(df)

print(True in [item for item in df1.duplicated(subset=['Subject'])])

data2 = { \
    'Subject':['semester1','semester2','semester3','semester4','semester5','semester6','semester7','semester8'], \
    'Score':[62,47,55,74,31,77,85,55] \
}

df2 = pd.DataFrame(data2)
print(df2.duplicated(subset=['Subject']))


print(df2.iloc[0,0], df2.iloc[0,1])
