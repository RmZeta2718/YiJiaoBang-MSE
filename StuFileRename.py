import pandas as pd
from typing import Tuple


def stuCheck(file_name: str, df: pd.DataFrame) -> int:
    """
    检查file_name的一致性
    :return: int 若信息一致，返回学生在df中的行索引，否则返回-1
    """
    suspect = -1
    for idx, row in df.iterrows():
        if file_name.find(row['学号']) != -1:
            if suspect >= 0:
                if suspect != idx:
                    return -1
            suspect = idx
        if file_name.find(row['姓名']) != -1:
            if suspect >= 0:
                if suspect != idx:
                    return -1
            suspect = idx
        return suspect


def stuFormat(df: pd.DataFrame, idx: int, fmt: str) -> str:
    row = df.iloc[idx]
    return fmt % (row['学号'], row['姓名'])


def getSuffix(file_name: str) -> Tuple[str, str]:
    idx = file_name.rfind('.')
    if idx < 0:
        return (
            file_name, '')
    return (
        file_name[:idx], file_name[idx:])


def stuFileRename(file_name: str, df: pd.DataFrame, fmt: str) -> str:
    file_name, suffix = getSuffix(file_name)
    idx = stuCheck(file_name, df)
    if idx < 0:
        return ''
    return stuFormat(df, idx, fmt) + suffix


if __name__ == '__main__':
    pass
