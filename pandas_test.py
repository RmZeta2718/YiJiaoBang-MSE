import pandas as pd

df = pd.read_csv('./附件/学生信息表.csv', encoding="ANSI")
df = df.astype(str)
df.set_index('学号', inplace=True, verify_integrity=True)
print(df)
print(df.loc['10185102223'])

print(df.loc['10185102223'])
print('1018512223' in df.index)
print(df.index)
