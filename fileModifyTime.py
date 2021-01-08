"""
假定助教输入ddl或界面上给出ddl输入格式为类似：2020-02-04 05:04:01,类型为字符串，务必注意0的输入和中间空格
num 为第num次实验，类型为整数
缺省参数path为储存路径，类型为字符串
迟交即返回TRUE，否则为FALSE

第二种方案中返回的是每一个文件的名字和晚交T/F列表,根据情况可以另作调整
"""
import os
import datetime


def fileModifyTime(path: str) -> datetime.datetime:
    statInfo = os.stat(path)
    # print(datetime.datetime.fromtimestamp(statInfo.st_mtime))
    return datetime.datetime.fromtimestamp(statInfo.st_mtime)


def checkPathLate(path: str, ddl: datetime.datetime) -> bool:
    """
    若超过DDL则返回True
    """
    return ddl < fileModifyTime(path)


# def late_delivery(ddl, num, path="/Users/10361/Desktop/软件工程/易教帮/已归档作业_%d_未批改"):
#     path = path % num
#     path_list = os.listdir(path)
#     # print(path_list)
#     # late_delivert_list = []
#
#     for i in range(len(path_list)):
#         statinfo = os.stat(path + '/' + path_list[i])
#         return ddl < time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(statinfo.st_mtime))
#         # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(statinfo.st_mtime)))
#         # late_delivert_list += [path_list[i]，ddl<time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(statinfo.st_mtime))]
#     # return late_delivert_list

if __name__ == '__main__':
    # late_delivery("2020-02-04 05:04:01",1)
    # print(late_delivery("2020-02-14 05:04:01",1))
    pass
