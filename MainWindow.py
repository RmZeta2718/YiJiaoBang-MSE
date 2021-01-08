import sys
import os
from typing import Union
import datetime
import pandas as pd
from StuFileRename import stuFileRename, nameFormatDump
from fileModifyTime import fileModifyTime, checkPathLate
from ui_functions import *

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QDateTime
from PyQt5 import uic  # for loadUI


class MainWindow(QtWidgets.QMainWindow):
    # type annotation
    rootDir: Union[str, None]
    hwNo: Union[int, None]
    ddl: Union[datetime.datetime, None]
    stuInfo: Union[pd.DataFrame, None]
    statDir: Union[str, None]
    fileFormat: Union[str, None]
    encoding: Union[str, None]
    animation: QPropertyAnimation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # uic.loadUi('MainWindow.ui', self)  # load *.ui file
        uic.loadUi('ui_main.ui', self)  # load *.ui file

        # global variables (in class)
        self.rootDir = None  # 工作环境根目录
        self.hwNo = None  # 当前处理的作业编号
        self.ddl = None  # 作业截止日期，
        self.stuInfo = None  # 学生信息表，pandas data frame
        self.statDir = None  # 作业统计信息表, 路径
        self.fileFormat = r'<学号>_<姓名>_实验<实验编号>'  # 重命名格式
        self.encoding = None  # 文件编码格式，由学生信息表确定
        # self.animation = None  # Qt动画对象

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
        # page slots
        self.BtnPageFormat.clicked.connect(self.onBtnPageFormat)
        self.BtnPageArchive.clicked.connect(self.onBtnPageArchive)  # need change datetime on click
        self.BtnPageCheck.clicked.connect(self.onBtnPageCheck)
        self.BtnPageStat.clicked.connect(self.onBtnPageStat)
        self.BtnToggle.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))
        # Format page button slots
        self.BtnAddName.clicked.connect(self.onBtnAddName)
        self.BtnAddStuNo.clicked.connect(self.onBtnAddStuNo)
        self.BtnAddHwNo.clicked.connect(self.onBtnAddHwNo)
        self.BtnSetFormat.clicked.connect(self.onBtnSetFormat)
        self.textEditFormat.textChanged.connect(self.onTextFormatChanged)
        # Archive page button slots
        self.BtnSetDir.clicked.connect(self.onBtnSetDir)
        self.BtnSetHwNo.clicked.connect(self.onBtnSetHwNo)
        self.BtnSetDdl.clicked.connect(self.onBtnSetDdl)
        self.BtnArchive.clicked.connect(self.onBtnArchive)
        # Check page button slots
        self.BtnCheck.clicked.connect(self.onBtnCheck)
        self.textEditStuNo.textChanged.connect(self.onTextStuNoChanged)
        self.textEditScore.textChanged.connect(self.onTextScoreChanged)

    # page switch function
    def onBtnPageFormat(self):
        """
        来到格式页时总显示当前格式
        """
        # self.textEditFormat: QtWidgets.QTextEdit
        self.textEditFormat.setText(self.fileFormat)
        self.labelTop.setText(self.BtnPageFormat.text())
        self.stackedWidget.setCurrentWidget(self.pageFormat)

    def onBtnPageArchive(self):
        """
        每次点击菜单页的归档按钮，把DDL默认值改为当前时间
        """
        # self.dateTimeEdit: QtWidgets.QDateTimeEdit
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime().addDays(-365))
        self.dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime().addDays(365))
        self.labelTop.setText(self.BtnPageArchive.text())
        self.stackedWidget.setCurrentWidget(self.pageArchive)

    def onBtnPageCheck(self):
        self.labelTop.setText(self.BtnPageCheck.text())
        self.stackedWidget.setCurrentWidget(self.pageCheck)

    # Format page
    def onBtnAddName(self):
        self.textEditFormat.setText(self.textEditFormat.toPlainText() + '<姓名>')

    def onBtnAddStuNo(self):
        self.textEditFormat.setText(self.textEditFormat.toPlainText() + '<学号>')

    def onBtnAddHwNo(self):
        self.textEditFormat.setText(self.textEditFormat.toPlainText() + '<实验编号>')

    def onBtnSetFormat(self):
        # self.textEditFormat: QtWidgets.QTextEdit
        # self.labelForamt: QtWidgets.QLabel
        fmt = self.textEditFormat.toPlainText()
        if fmt.find(' ') != -1:
            ans = QMessageBox.question(self, '提示', '文件名中包含空格，是否替换为下划线(_)？')
            if ans == QMessageBox.Yes:
                fmt = nameFormatDump(fmt)
                self.textEditFormat.setText(fmt)
        self.fileFormat = fmt
        self.labelForamt.setText('')

    def onTextFormatChanged(self):
        # self.textEditFormat: QtWidgets.QTextEdit
        # self.labelForamt: QtWidgets.QLabel
        if self.fileFormat != self.textEditFormat.toPlainText():
            self.labelForamt.setText(f'当前格式：{self.fileFormat}')
        else:
            self.labelForamt.setText('')

    ###################################################################
    # Archive page
    def onBtnSetDir(self):
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
        if not self.initInfo():
            self.rootDir = None
            return
        tardir = [f'./{path}' for path in [self.dirWaiting, self.dirArchive]]
        if not self.setupDir(tardir):
            self.rootDir = None
            return
        self.updateArchiveText()

    def onBtnSetHwNo(self):
        if not self.checkSettings(onlyRoot=True):
            return
        # 输入
        self.hwNo, ok = QInputDialog.getInt(self, '作业批次', '请输入作业批次', min=1, max=99)
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
        if not self.checkStat():
            self.hwNo = None
            return
        self.updateArchiveText()
        self.updateCheckText()

    def onBtnSetDdl(self):
        # self.dateTimeEdit: QtWidgets.QDateTimeEdit
        self.ddl = self.dateTimeEdit.dateTime().toPyDateTime()
        self.updateArchiveText()

    def onBtnArchive(self):
        if not self.checkSettings():
            return

        # 待归档文件列表（不包含文件夹）
        waiting_files = [file for file in os.listdir(f'./{self.dirWaiting}')
                         if os.path.isfile(f'./{self.dirWaiting}/{file}')]
        # print(waiting_files)

        if len(waiting_files) == 0:
            if len(os.listdir('./' + self.dirWaiting)) != 0:
                # 列表为空，但是存在目录非空。可能是所有作业都以文件夹形式存在
                # 若先把所有非文件夹作业成功归档，再按归档按钮，则来到这里
                QMessageBox.warning(self, '警告', '本系统不支持文件夹形式的作业\n请将文件夹打包成压缩包')
            else:
                QMessageBox.information(self, '作业归档', '没有待归档文件')
            return

        df = self.openCsv(self.statDir)
        archive_cnt = 0
        for file_name in waiting_files:
            stuno, new_name = stuFileRename(file_name, self.stuInfo, self.hwNo, self.fileFormat)
            # print(file_name, '|', new_name)
            if len(new_name) == 0:
                continue
            src = f'./{self.dirWaiting}/{file_name}'
            dst = f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}/{new_name}'
            if os.path.isfile(dst):
                if fileModifyTime(src) < fileModifyTime(dst):
                    # 目标位置已经有修改日期更晚的文件，丢弃现在的文件
                    os.remove(src)
                    continue
                else:       # 目标位置文件是旧版本，丢弃目标位置的文件，准备放入新文件
                    os.remove(dst)
            os.rename(src, dst)
            # 标记状态
            # print(stuno, stuno in df.index)
            df.loc[stuno, '状态'] = '迟交' if checkPathLate(dst, self.ddl) else '√'
            archive_cnt += 1
        self.writeCsv(self.statDir, df)
        text = f'已归档 {archive_cnt} 份作业'
        if archive_cnt != len(waiting_files):
            text += f'\n有 {len(waiting_files) - archive_cnt} 份作业命名不完全，请手动处理'
        QMessageBox.information(self, '作业归档', text)

    def setupDir(self, dirs: list):
        """
        给定一个路径列表（文件夹的路径）
        判断每个文件夹是否存在，若不存在则询问创建
        返回是否所有要求都已满足
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

    def initInfo(self) -> bool:
        """
        初始化学生信息表，并检测各种错误
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
        # change to str
        self.stuInfo = self.stuInfo.astype(str)
        self.stuInfo.set_index('学号', inplace=True, verify_integrity=True)
        # print('initInfo', self.stuInfo)
        # print(self.stuInfo.index)
        return True

    def checkStat(self):
        ans = None
        if not os.path.isfile(self.statDir):
            ans = QMessageBox.warning(self, '警告', f'没有找到 {self.statDf} ，是否自动创建？\n'
                                                  f'若已有该文件，请确保其路径为：\n{self.statDir}',
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        # TODO: 检查文件格式是否规范
        if ans == QMessageBox.Yes:
            self.initStat()
        elif ans == QMessageBox.No:
            return False
        return True

    def initStat(self):
        rows = self.stuInfo.shape[0]
        data = {'学号': list(self.stuInfo.index), '姓名': self.stuInfo['姓名'],
                '成绩': [' '] * rows, '状态': [' '] * rows, '批注': [' '] * rows}
        df = pd.DataFrame(data)
        df = df.astype(str)
        df.set_index('学号', inplace=True, verify_integrity=True)
        # print(df.index)
        # print(df['状态'])
        # print('initStat', df)
        # df.to_csv(self.statDir, encoding=self.encoding, index=False)
        self.writeCsv(self.statDir, df)

    def updateArchiveText(self):
        text = ''
        if self.rootDir is not None:
            text += f'当前根目录：\n{self.rootDir}\n'
        else:
            text += f'尚未指定工作目录\n'
        if self.hwNo is not None:
            text += f'正在处理第 {self.hwNo} 次作业\n'
        else:
            text += f'尚未指定作业批次\n'
        if self.ddl is not None:
            text += f'截止日期： {self.ddl.strftime("%Y-%m-%d %H:%M:%S")} \n'
        else:
            text += f'尚未指定截止日期\n'
        text = text.strip()
        self.textBrowserArchive.setText(text)

    ###################################################################
    # Check page
    def onBtnCheck(self):
        self.textEditStuNo: QtWidgets.QTextEdit
        self.textEditScore: QtWidgets.QTextEdit
        self.textEditComment: QtWidgets.QTextEdit
        self.labelStuNo: QtWidgets.QLabel
        self.labelScore: QtWidgets.QLabel

        if not self.checkSettings():
            return
        # 检查学号
        stuno = self.textEditStuNo.toPlainText()
        if stuno not in self.stuInfo.index:
            QMessageBox.critical(self, '错误', f'学号 {stuno} 不存在')
            return
        # 检查学号对应的未批改文件是否存在
        file_name = self.stuno2filename(stuno)
        # print(file_name)
        if file_name is None:
            QMessageBox.critical(self, '错误', f'找不到学号 {stuno} 对应的未批改作业文件')
            return
        # 检查分数格式
        score = self.textEditScore.toPlainText()
        try:
            float(score)
        except ValueError:
            QMessageBox.critical(self, '错误', f'分数格式错误')
            return
        # 获取评论
        comment = self.textEditComment.toPlainText()
        # 登记分数
        self.StatCommit(stuno, score, comment)
        # 移动到已批改
        src = f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}/{file_name}'
        dst = f'./{self.dirArchive}/{self.hwNo}/{self.dirMarked}/{file_name}'
        os.rename(src, dst)
        self.textEditScore.setText('')
        self.textEditComment.setText('')
        QMessageBox.information(self, '登记成绩', '登记成功')

    def onTextStuNoChanged(self):
        # self.textEditStuNo: QtWidgets.QTextEdit
        # self.labelStuNo: QtWidgets.QLabel
        if self.stuInfo is None:
            return
        stuno = self.textEditStuNo.toPlainText()
        if stuno in self.stuInfo.index:
            self.labelStuNo.setText(self.stuInfo.loc[stuno, '姓名'])
        else:
            self.labelStuNo.setText('')

    def onTextScoreChanged(self):
        # self.textEditScore: QtWidgets.QTextEdit
        # self.labelScore: QtWidgets.QLabel
        score = self.textEditScore.toPlainText()
        if score == '':
            self.labelScore.setText('')
            return
        try:
            float(score)
        except ValueError:
            self.labelScore.setText('格式错误')
        else:
            self.labelScore.setText('')

    def stuno2filename(self, stuNo: str) -> Union[str, None]:
        """
        调用者需要确保stuNo在学生信息表中存在。
        """
        file_list = os.listdir(f'./{self.dirArchive}/{self.hwNo}/{self.dirNoMark}')
        for file in file_list:
            if file.find(stuNo) >= 0:
                return file
        return None

    def StatCommit(self, stuno: str, grade: str, comment: str):
        df = self.openCsv(self.statDir)
        # df.成绩[idx] = grade
        # df.批注[idx] = comment
        df.loc[stuno, ['成绩', '批注']] = grade, comment
        # print(df.loc[stuno, :])
        self.writeCsv(self.statDir, df)

    def updateCheckText(self):
        self.textBrowserCheck: QtWidgets.QTextBrowser
        text = ''
        if self.hwNo is not None:
            text += f'正在处理第 {self.hwNo} 次作业\n'
        else:
            text += f'尚未指定作业批次\n'
        text = text.strip()
        self.textBrowserCheck.setText(text)

    ###################################################################
    # Stat page
    def onBtnPageStat(self):
        # self.textBrowserStat: QtWidgets.QTextBrowser
        # self.BtnPageStat: QtWidgets.QPushButton
        if not self.checkSettings():
            self.textBrowserStat.setText('')
            return
        text = ''
        nothandin = []
        late = []
        df = self.openCsv(self.statDir)
        for stuno, row in df.iterrows():
            if row['状态'] == '√':
                continue
            elif row['状态'] == '迟交':
                late.append(row['姓名'])
            else:
                nothandin.append(row['姓名'])
        text += f'迟交 {len(late)} 人\n'
        if len(late):
            text += ', '.join(late)
            text += '\n'
        text += f'未交 {len(nothandin)} 人\n'
        if len(nothandin):
            text += ', '.join(nothandin)
            text += '\n'
        text = text.strip()
        self.textBrowserStat.setText(text)
        self.labelTop.setText(self.BtnPageStat.text())
        self.stackedWidget.setCurrentWidget(self.pageStat)

    ###################################################################
    # functions for all pages
    def checkSettings(self, onlyRoot=False):
        if self.rootDir is None:
            QMessageBox.critical(self, '错误', '没有设定工作目录！')
            return False
        if onlyRoot:
            return True
        if self.hwNo is None:
            QMessageBox.critical(self, '错误', '没有设定当前作业编号！')
            return False
        if self.ddl is None:
            ans = QMessageBox.question(self, '错误', '尚未设定截止日期\n是否设置为现在的时间？')
            if ans == QMessageBox.Yes:
                self.ddl = datetime.datetime.now()
                self.updateArchiveText()
            else:
                return False
        return True

    def openCsv(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, encoding=self.encoding)
        df = df.astype(str)
        df.set_index('学号', inplace=True)
        # print('openCsv:', df)
        return df

    def writeCsv(self, path: str, df: pd.DataFrame):
        df.to_csv(path, encoding=self.encoding)


if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # dialog = QtWidgets.QDialog()
    # prog = MyFirstGuiProgram(dialog)
    # dialog.show()
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle('Fusion')
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())
