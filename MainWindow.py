import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from PyQt5 import uic  # for loadUI
from StuFileRename import stuFileRename
import pandas as pd


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('MainWindow.ui', self)  # load *.ui file

        # global variables (in class)
        self.rootDir = None  # 工作环境根目录
        self.hwNo = None  # 当前处理的作业编号
        self.stuInfo = None  # 学生信息表，pandas data frame
        self.statDir = None  # 作业统计信息表, 路径
        self.fileFormat = r'%s_%s'  # 重命名格式
        self.encoding = None  # 文件编码格式，由学生信息表确定

        # global contants (in class)
        self.fileDf = '学生信息表.csv'
        self.statDf = '作业统计信息表.csv'
        self.dirWaiting = '待归档作业'
        self.dirArchive = '已归档作业'
        self.dirNoMark = '未批改作业'
        self.dirMarked = '已批改作业'
        self.CSV_NOT_FOUND = 0
        self.CSV_NOT_STAND = 1
        self.CSV_CHECKED = 2

        # create slots
        self.pushButtonDirectory.clicked.connect(self.onPushButtonDirectory)
        self.pushButtonHwNo.clicked.connect(self.onPushButtonHwNo)
        self.pushButtonArchive.clicked.connect(self.onPushButtonArchive)
        self.pushButtonCheck.clicked.connect(self.onPushButtonCheck)

    def onPushButtonDirectory(self):
        self.rootDir = QFileDialog.getExistingDirectory(self)
        if len(self.rootDir) == 0:  # 按取消
            self.rootDir = None
            return
        ans = QMessageBox.information(self, '更改工作目录', f'是否将根目录修改为：\n{self.rootDir}',
                                      buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if ans == QMessageBox.No:
            self.rootDir = None
            return
        os.chdir(self.rootDir)  # change current working directory to rootDir
        if not self.initdf:
            self.rootDir = None
            return
        tardir = ['./' + path for path in [self.dirWaiting, self.dirArchive]]
        if not self.setupDir(tardir):
            self.rootDir = None
            return
        self.showSysHint()

    def onPushButtonHwNo(self):
        if not self.checkSettings(onlyRoot=True):
            return
        # 输入
        self.hwNo, ok = QInputDialog.getInt(self, '作业批次', '请输入作业批次', min=1, max=100)
        if not ok:
            self.hwNo = None
            return
        # 每次作业的总文件夹
        tardir = [f'./{self.dirArchive}/{self.hwNo}']
        # 子文件夹
        tardir += [f'./{self.dirArchive}/{self.hwNo}/{path}' for path in [self.dirNoMark, self.dirMarked]]
        if not self.setupDir(tardir):
            self.hwNo = None
            return
        self.statDir = f'./{self.dirArchive}/{self.hwNo}/{self.statDf}'
        if not self.checkStatCsv:
            self.hwNo = None
            return
        self.showSysHint()

    def onPushButtonArchive(self):
        if not self.checkSettings():
            return

        waiting_files = [file for file in os.listdir(f'./{self.dirWaiting}')
                         if os.path.isfile(f'./{self.dirWaiting}/{file}')]
        print(waiting_files)

        if len(waiting_files) == 0:
            if len(os.listdir('./' + self.dirWaiting)) != 0:
                QMessageBox.warning(self, '警告', '本系统不支持文件夹形式的作业\n请将文件夹打包成压缩包')
            else:
                QMessageBox.information(self, '作业归档', '没有待归档文件')
            return

        archive_cnt = 0
        for file_name in waiting_files:
            new_name = stuFileRename(file_name, self.stuInfo, self.fileFormat)
            print(file_name, '|', new_name)
            if len(new_name) == 0:
                continue
            src = f'./{self.dirWaiting}/{file_name}'
            dst = f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}/{new_name}'
            os.rename(src, dst)
            archive_cnt += 1
        text = f'已归档 {archive_cnt} 份作业'
        if archive_cnt != len(waiting_files):
            text += f'\n有 {len(waiting_files) - archive_cnt} 份作业命名不完全，请手动处理'
        QMessageBox.information(self, '作业归档', text)

    def onPushButtonCheck(self):
        if not self.checkSettings():
            return
        stuno, ok = QInputDialog.getText(self, '作业批改', '请输入学号')
        if not ok:
            return
        file_name = self.stuno2filename(stuno)
        print(file_name)
        if file_name is None:
            QMessageBox.critical(self, '错误', f'学号 {stuno} 不存在')
            return
        score, ok = QInputDialog.getText(self, '作业批改', '请输入成绩')
        if not ok:
            return
        comment, ok = QInputDialog.getText(self, '作业批改', '请输入批注')
        if not ok:
            return
        self.StatCommit(stuno, score, comment)
        # 移动到已批改
        src = f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}/{file_name}'
        dst = f'./{self.dirArchive}/{self.hwNo}/{self.dirMarked}/{file_name}'
        print(src)
        print(dst)
        os.rename(src, dst)

    def setupDir(self, dirs):
        """
        给定一个路径列表（文件夹的路径）
        判断每个文件夹是否存在，若不存在则询问创建
        :param dirs: list
        :return: bool 是否所有要求都已满足
        """
        ask = True  # 只询问一次是否要创建
        # create directories
        for directory in dirs:
            if not os.path.exists(directory):
                if ask:
                    ans = QMessageBox.warning(self, '警告', '没有找到必要路径，是否自动创建？',
                                              buttons=QMessageBox.Yes | QMessageBox.No,
                                              defaultButton=QMessageBox.Yes)
                    if ans == QMessageBox.No:
                        return False
                    ask = False
                os.makedirs(directory)
            if not os.path.isdir(directory):
                QMessageBox.critical(self, '错误', f'创建文件夹 "{directory}" 失败！')
                return False
        return True

    def initdf(self):
        """
        初始化学生信息表，并检测各种错误
        :return:
        """
        target = f'{self.rootDir}/{self.fileDf}'
        if not os.path.isfile(target):
            QMessageBox.critical(self, '错误', f'没有找到学生信息表，请确保该文件路径为：\n{target}')
            return False
        try:
            self.stuInfo = pd.read_csv(target, encoding='ANSI')
            self.encoding = 'ANSI'
        except UnicodeDecodeError:
            try:
                self.stuInfo = pd.read_csv(target, encoding='UTF-8')
                self.encoding = 'UTF-8'
            except UnicodeDecodeError:
                QMessageBox.critical(self, '错误', '无法解析学生信息表，请确保其编码格式为UTF-8或ANSI')
                return False
        self.stuInfo = self.stuInfo.astype(str)
        print(self.stuInfo)
        return True

    def checkSettings(self, onlyRoot=False):
        if self.rootDir is None:
            QMessageBox.critical(self, '错误', '没有设定工作目录！')
            return False
        if onlyRoot:
            return True
        if self.hwNo is None:
            QMessageBox.critical(self, '错误', '没有设定当前作业编号！')
            return False

        return True

    def checkStatCsv(self):
        ans = None
        if not os.path.isfile(self.statDir):
            ans = QMessageBox.warning(self, '警告', f'没有找到 {self.statDf} ，是否自动创建？\n'
                                                  f'若已有该文件，请确保其路径为：\n{self.statDir}',
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        # try:
        #     df = pd.read_csv(path, encoding='ANSI')
        # except UnicodeDecodeError:
        #     try:
        #         df = pd.read_csv(path, encoding='UTF-8')
        #     except UnicodeDecodeError:
        #         return self.CSV_NOT_STAND, None
        # return self.CSV_CHECKED, df
        # elif csv_status == self.CSV_NOT_STAND:
        #     ans = QMessageBox.warning(self, "警告", "检测到 %s 格式不规范，是否重写？" % self.statDf,
        #                               buttons=QMessageBox.Yes | QMessageBox.No,
        #                               defaultButton=QMessageBox.Yes)
        if ans == QMessageBox.Yes:
            self.initCsv()
        elif ans == QMessageBox.No:
            return False
        return True

    def initCsv(self):
        rows = self.stuInfo.shape[0]
        data = {'学号': self.stuInfo.学号, '姓名': self.stuInfo.姓名,
                '成绩': [None] * rows, '状态': [None] * rows, '批注': [None] * rows}
        df = pd.DataFrame(data)
        # print(df)
        df.to_csv(self.statDir, encoding=self.encoding, index=False)

    def stuno2filename(self, stuNo):
        # TODO: stuNo == ""
        file_list = os.listdir(f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}')
        for file in file_list:
            if file.find(stuNo) >= 0:
                return file
        return None

    def StatCommit(self, stuno, grade, comment):
        for idx, no in enumerate(self.stuInfo.学号):
            if no == stuno:
                break
        df = pd.read_csv(self.statDir, encoding='ANSI')
        # df.成绩[idx] = grade
        # df.批注[idx] = comment
        df.loc[idx, ['成绩', '批注']] = grade, comment
        print(df.iloc[idx, :])
        df.to_csv(self.statDir, encoding=self.encoding, index=False)

    def showSysHint(self):
        text = ''
        if self.rootDir is not None:
            text += f'当前根目录：\n{self.rootDir}\n'
        if self.hwNo is not None:
            text += f'正在处理第 {self.hwNo} 次作业\n'
        self.textBrowser.setText(text)


if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # dialog = QtWidgets.QDialog()
    # prog = MyFirstGuiProgram(dialog)
    # dialog.show()
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())
