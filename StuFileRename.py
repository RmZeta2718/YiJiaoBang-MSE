import pandas as pd
import re
from typing import Tuple


def stuCheck(file_name: str, df: pd.DataFrame) -> str:
    """
    检查file_name的一致性
    :return: str 若信息一致，返回学号，否则返回空字符串
    """
    suspect = ""
    for stuno, row in df.iterrows():
        stuno = str(stuno)
        if file_name.find(stuno) != -1:
            if suspect != "" and suspect != stuno:
                return ""
            suspect = stuno
        if file_name.find(row['姓名']) != -1:
            if suspect != "" and suspect != stuno:
                return ""
            suspect = stuno
    return suspect


def stuFormat(df: pd.DataFrame, stuno: str, hwno: int, fmt: str) -> str:
    row = df.loc[stuno]
    fmt = re.sub(r'<学号>', stuno, fmt)
    fmt = re.sub(r'<姓名>', row['姓名'], fmt)
    fmt = re.sub(r'<实验编号>', str(hwno), fmt)
    return fmt


def getSuffix(file_name: str) -> Tuple[str, str]:
    idx = file_name.rfind('.')
    if idx < 0:
        return file_name, ''
    return file_name[:idx], file_name[idx:]


def stuFileRename(file_name: str, df: pd.DataFrame, hwno: int, fmt: str) -> str:
    file_name, suffix = getSuffix(file_name)
    stuno = stuCheck(file_name, df)
    if stuno == "":
        return ""
    return stuFormat(df, stuno, hwno, fmt) + suffix


if __name__ == '__main__':
    df = pd.read_csv('./附件/学生信息表.csv', encoding="ANSI")
    df = df.astype(str)
    df.set_index('学号', inplace=True, verify_integrity=True)
    print(stuFormat(df, '10185102223', 3, '<学号>_<姓名>:<实验编号>'))
