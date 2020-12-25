import os
import time


def dirContains(path, tarlist):
    """
    检查path这个文件夹内是否存在指定的若干个文件夹
    :param path: str
    :param tarlist: list
    :return: bool
    """
    if not os.path.isdir(path):
        return False
    dir_set = set([path for path in os.listdir(path) if os.path.isdir(path)])
    for tar in tarlist:
        if tar not in dir_set:
            return False
    return True


if __name__ == '__main__':
    print(time.localtime(os.stat(r'D:\Study\20-1现代软件工程\项目\易教帮').st_mtime))
    # print(legalRootDir(r'D:\Study\20-1现代软件工程\项目\易教帮\checkrs.py', []))
