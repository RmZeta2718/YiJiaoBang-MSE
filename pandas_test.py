import pandas as pd

df = pd.read_csv('./附件/学生信息表.csv', encoding="ANSI")
df = df.astype(str)
df.set_index('学号', inplace=True, verify_integrity=True)
print(df)
print(df.loc['10185102223'])

no = '10185102223'
print(no in df.index)
print(list(df.index))
print(df.loc[no, '姓名'])
df.loc[no, '姓名'] = '123123123123'
df.to_csv('./test.csv', encoding="ANSI")

