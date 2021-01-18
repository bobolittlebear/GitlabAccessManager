# -*- coding: UTF-8 -*-
import os
import pickle
import requests
import sys
import threading
import time
from xml import sax

from PyQt5.QtCore import pyqtSlot, QDir, QFile, QIODevice, Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog, QLineEdit)

from logWidget import LogView
from module import api_http_gitlab as gitlab
from module.mdl_Log import Log
from module.mdl_ManifestXml import ManifestHandler as xmlHandler
from tableWindow import TableWindow
from ui.ui_MainWindow import Ui_MainWindow
from config import *


class QmyMainWindow(QMainWindow):
    # 子线程发射显示QMessageBox的信号
    messageShowed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        # 调用父类构造函数，创建窗体
        super().__init__(parent)
        # 创建UI对象,构造UI界面
        self.__ui = Ui_MainWindow()
        self.__ui.setupUi(self)
        
        # 创建QmyMainWindow对象的业务属性
        self.__initDataFile()
        self.__initToken()
        # self.__initGitlab()
        self.__initLogger()
        self.__initComboValue()
        self.createLogWindow()
        
        self.__subThreads = []
        # 权限子窗口记录————关闭子窗口功能使用
        self.__subWindows = []
        
        self.messageShowed.connect(self.do_messageShowed_str)
        
        self.levelMap = {
            'developer': 30,
            'reporter': 20,
            'maintainer': 40
        }
    
    def networkDetect(self):
        url = 'https://gitlab.gz.cvte.cn'
        state = "False"
        while True:
            try:
                r = requests.get(url, timeout=5)
                state = "True"
            except:
                state = "False"
            self.networkStateChanged[str].emit(state)
            time.sleep(60)
    
    #  ===========由connectSlotsByName() 自动连接的槽函数=====================
    @pyqtSlot(str)
    def do_messageShowed_str(self, message):
        QMessageBox.warning(self, "提示", message)
    
    # ==================Tab 1=================================
    @pyqtSlot()
    def on_setTokenBtn_clicked(self):
        title = "导入Token"
        txtLabel = "请输入Gitlab Token:"
        echoMode = QLineEdit.Normal
        token, OK = QInputDialog.getText(self, title, txtLabel, echoMode)
        if (OK):
            if (token):
                self.__token = token
                try:
                    with open(self.__tokenfile, 'wb') as tokenStream:
                        pickle.dump(self.__token, tokenStream)
                        tokenStream.close()
                    # 导入新 Token 后,重新创建gitlab对象
                    # self.__initGitlab()
                except Exception as errorMsg:
                    print(errorMsg)
                    QMessageBox.critical(self, '错误', '写入Token错误!\n请重新导入Token')
                    exit(1)
            else:
                QMessageBox.warning(self, "提示", "未导入/更改 Gitlab Token !")
    
    @pyqtSlot()
    def on_confirmBtn_clicked(self):
        account = self.__ui.accountEdit.text()
        platform = self.__ui.platformCombo.currentText()
        level = self.__ui.levelCombo.currentText()
        access_level = self.levelMap[level]
        print(str(access_level) + ' ' + platform)
        thread = threading.Thread(target=self.__setAccess, args=(account, platform, access_level))
        thread.start()
        # thread.join()
        self.__subThreads.append(thread)
    
    @pyqtSlot(str)
    def on_accountEdit_textChanged(self, account):
        account = self.__ui.accountEdit.text()
        platform = self.__ui.platformCombo.currentText()
        level = self.__ui.levelCombo.currentText()
        if account and platform and level:
            self.__ui.confirmBtn.setEnabled(True)
        else:
            self.__ui.confirmBtn.setDisabled(True)
    
    @pyqtSlot(bool)
    def on_showGitBox_clicked(self, checked):
        pass
    
    @pyqtSlot(bool)
    def on_shoLogBox_clicked(self, checked):
        try:
            if checked:
                x = self.x() - self.width() - 20
                y = self.y() + 40
                self.logWin.move(x, y)
                self.logWin.show()
            else:
                self.logWin.hide()
        except Exception as msg:
            self.logger.LOGE(msg)
    
    # ==================Tab 2=================================
    @pyqtSlot()
    def on_fileButton_clicked(self):
        curPath = QDir.currentPath()
        title = "打开一个文件"
        # 文件过滤器
        filt = "程序文件(*.xml)"
        fileName, flt = QFileDialog.getOpenFileName(self, title, curPath, filt)
        print(fileName)
        if (fileName == ""):
            return
        if self.__openByIODevice(fileName):
            pass
        else:
            QMessageBox.critical(self, "error", "打开文件失败")
        
        # 重设button text
        text = fileName.split('/')[-1]
        self.__ui.fileButton.setText(text)
        self.__ui.fileButton.setAccessibleDescription(fileName)
        print(self.__ui.fileButton.accessibleDescription())
    
    @pyqtSlot()
    def on_importRepoBtn_clicked(self):
        fileName = self.__ui.fileButton.accessibleDescription()
        platform = self.__ui.platformEdit.text()
        ret = self.__parseManifestXml(fileName, platform)
        if ret:
            self.__ui.platformCombo.addItem(platform)
            self.__ui.platformCombo_2.addItem(platform)
            self.__ui.platformCombo_3.addItem(platform)
            self.logger.LOGI('添加平台' + platform + '成功!')
            QMessageBox.information(self, '成功', '添加平台成功!')
        else:
            self.logger.LOGE('添加平台' + platform + '失败!')
            QMessageBox.critical(self, '错误', '添加平台失败!')
        
        self.__ui.fileButton.setAccessibleDescription('')
        self.__ui.fileButton.setText("选择xml文件")
        self.__ui.fileButton.setText('')
    
    @pyqtSlot()
    def on_importGitBtn_clicked(self):
        gitName = self.__ui.gitNameEdit.text()
        gitID = self.__ui.gitLinkEdit.text()
        git = self.createGitlabObject()
        if git is None:
            return
        if gitName and gitID:
            gitPath = git.getProjectPathById(gitID)
            print(self.projectList)
            if gitName in self.projectList.keys():
                QMessageBox.critical(self, '失败', gitName + "已存在")
                return
            self.projectList[gitName] = [gitPath]
            print(self.projectList[gitName])
            self.__ui.platformCombo.addItem(gitName)
            self.__ui.platformCombo_2.addItem(gitName)
            self.__ui.platformCombo_3.addItem(gitName)
            try:
                with open(self.projectFile, 'wb') as save_project:
                    pickle.dump(self.projectList, save_project)
                self.logger.LOGI('添加仓库' + gitName + '成功!')
                QMessageBox.information(self, '成功', "导入" + gitName + "成功")
            except Exception as errorMsg:
                self.logger.LOGE('添加仓库' + gitName + '失败!' + str(errorMsg))
                QMessageBox.critical(self, '错误', '请选择正确的Manifest XML文件！')
        else:
            QMessageBox.warning(self, "提示", "仓库信息不全!")
    
    @pyqtSlot(str)
    def on_platformEdit_textChanged(self, paltform):
        platform = self.__ui.platformEdit.text()
        file = self.__ui.fileButton.accessibleDescription()
        if platform and file:
            self.__ui.importRepoBtn.setEnabled(True)
        else:
            self.__ui.importRepoBtn.setDisabled(True)
    
    @pyqtSlot(str)
    def on_gitNameEdit_textChanged(self, gitName):
        self.setGitBtnEnable()
    
    @pyqtSlot(str)
    def on_gitLinkEdit_textChanged(self, gitID):
        self.setGitBtnEnable()
    
    @pyqtSlot()
    def setGitBtnEnable(self):
        gitName = self.__ui.gitNameEdit.text()
        gitId = self.__ui.gitLinkEdit.text()
        if gitName and gitId:
            self.__ui.importGitBtn.setEnabled(True)
        else:
            self.__ui.importGitBtn.setDisabled(True)
    
    # ==================Tab 3=================================
    @pyqtSlot()
    def on_fileButton_2_clicked(self):
        curPath = QDir.currentPath()
        title = "打开一个文件"
        # 文件过滤器
        filt = "程序文件(*.txt)"
        fileName, flt = QFileDialog.getOpenFileName(self, title, curPath, filt)
        print(fileName)
        if fileName == "":
            return
        if self.__openByIODevice(fileName):
            self.__ui.statusbar.showMessage(fileName)
        else:
            QMessageBox.critical(self, "error", "打开文件失败")
        
        # 重设button text
        text = fileName.split('/')[-1]
        self.__ui.fileButton_2.setText(text)
        self.__ui.fileButton_2.setAccessibleDescription(fileName)
        print(self.__ui.fileButton_2.accessibleDescription())
    
    @pyqtSlot()
    def on_showLogBtn_2_clicked(self):
        try:
            x = self.x() - self.width() - 20
            y = self.y() + 40
            self.logWin.move(x, y)
            self.logWin.show()
        except Exception as msg:
            self.logger.LOGE(msg)
    
    @pyqtSlot()
    def on_importMemberBtn_clicked(self):
        platform = self.__ui.platformCombo_2.currentText()
        level = self.levelMap[self.__ui.levelCombo_2.currentText()]
        fileName = self.__ui.fileButton_2.accessibleDescription()
        subThread = threading.Thread(target=self.batchImportMember, args=(fileName, platform, level))
        subThread.start()
        self.__subThreads.append(subThread)
    
    def batchImportMember(self, fileName, platform, level):
        users = self.__parseMemberText(fileName)
        for user in users:
            self.__setAccess(user, platform, level)
    
    # ==================Tab 4=================================
    @pyqtSlot(str)
    def on_platformCombo_3_currentTextChanged(self, curText):
        # print(self.projectList[curText])
        gitPath = self.projectList[curText]
        self.__ui.gitCombo.clear()
        for i in gitPath:
            # 列表展示project名，关联数据是projrct的path_with_namespace
            self.__ui.gitCombo.addItem(i.split('/')[-1], i)
    
    @pyqtSlot()
    def on_showTableBtn_clicked(self):
        if self.__token == '':
            self.messageShowed[str].emit("请先导入token")
            return
        if self.createGitlabObject() is not None:
            path = self.__ui.gitCombo.currentData()
            memberView = TableWindow(self, path, self.__token)
            self.__subWindows.append(memberView)
        else:
            self.logger.LOGE("ConnectionError!")
            self.messageShowed[str].emit("网络连接错误！")
            return

    @pyqtSlot()
    def on_closeSubwinBtn_clicked(self):
        print(self.__subWindows)
        try:
            for i in self.__subWindows:
                i.close()
                self.__subWindows.remove(i)
        except Exception as errorMsg:
            self.logger.LOGE("关闭子窗口:" + str(errorMsg))
            print(errorMsg)
    
    ##  ============自定义功能函数================================
    def __initDataFile(self):
        self.__tokenfile = "./data/token"
        self.__token = ''
        self.projectFile = "./data/projects"
        self.projectList = {}
        if os.path.isfile(self.projectFile):
            try:
                if os.path.getsize(self.projectFile) != 0:
                    with open(self.projectFile, 'rb') as dict:
                        self.projectList = pickle.load(dict)
            except Exception as errorMsg:
                print(errorMsg)
                QMessageBox.warning(self, '错误', '初始化平台列表出错, 请重启程序解决')
    
    # Token 初始化
    def __initToken(self):
        if os.path.isfile(self.__tokenfile) and os.path.getsize(self.__tokenfile) != 0:
            try:
                with open(self.__tokenfile, 'rb') as tokenStream:
                    self.__token = pickle.load(tokenStream)
            except Exception as errorMsg:
                QMessageBox.critical(self, '错误', '读取Token错误!\n\r解决方法:重启程序或重新导入Token')
                exit(1)
        else:
            QMessageBox.warning(self, '提示', "未检测到Token, 点击\"权限开通 >> 导入Token \"将用户 Gitlab Token 导入!")
    
    def createGitlabObject(self):
        # if self.__networkStatus and len(self.__token) != 0:
        if len(self.__token) != 0:
            try:
                git = gitlab.GitlabAPI(GITLAB_URL, self.__token)
                return git
            except Exception as msg:
                self.logger.LOGE("Init git error:" + msg)
        return None
    
    def __initLogger(self):
        self.logger = Log("./data/exec.log")
    
    def __initComboValue(self):
        if len(self.projectList):
            l = list(self.projectList.keys())
            self.__ui.platformCombo.addItems(l)
            self.__ui.platformCombo_2.addItems(l)
            self.__ui.platformCombo_3.addItems(l)
            currentPlatform = self.__ui.platformCombo_3.currentText()
            print(self.projectList[currentPlatform])
            gitpath = self.projectList[currentPlatform]
            for i in gitpath:
                # 列表展示project名，关联数据是projrct的path_with_namespace
                self.__ui.gitCombo.addItem(i.split('/')[-1], i)
        
        # 设置combo box item text居中
        self.__ui.platformCombo.setEditable(True)
        self.__ui.platformCombo_2.setEditable(True)
        self.__ui.platformCombo_3.setEditable(True)
        self.__ui.levelCombo.setEditable(True)
        self.__ui.levelCombo_2.setEditable(True)
        self.__ui.gitCombo.setEditable(True)
        
        self.__ui.platformCombo.lineEdit().setAlignment(Qt.AlignCenter)
        self.__ui.platformCombo_2.lineEdit().setAlignment(Qt.AlignCenter)
        self.__ui.platformCombo_3.lineEdit().setAlignment(Qt.AlignCenter)
        self.__ui.levelCombo.lineEdit().setAlignment(Qt.AlignCenter)
        self.__ui.levelCombo_2.lineEdit().setAlignment(Qt.AlignCenter)
        self.__ui.gitCombo.lineEdit().setAlignment(Qt.AlignCenter)
        
        self.__ui.platformCombo.lineEdit().setReadOnly(True)
        self.__ui.platformCombo_2.lineEdit().setReadOnly(True)
        self.__ui.platformCombo_3.lineEdit().setReadOnly(True)
        self.__ui.levelCombo.lineEdit().setReadOnly(True)
        self.__ui.levelCombo_2.lineEdit().setReadOnly(True)
        self.__ui.gitCombo.lineEdit().setReadOnly(True)
    
    def __openByIODevice(self, fileName):
        fileDevice = QFile(fileName)
        if not fileDevice.exists():
            return False
        if not fileDevice.open(QIODevice.ReadOnly):
            return False
        try:
            while not fileDevice.atEnd():
                # 返回QByteArray类型
                qtBytes = fileDevice.readLine()
                # 将QByteArray转换为bytes类型
                pyBytes = bytes(qtBytes.data())
                # 将bytes转换为str类型
                lintStr = pyBytes.decode("utf-8")
                # 去除结尾空行
                lineStr = lineStr.strip()
                self.__token = lineStr
        except (Exception) as errorMsg:
            print(errorMsg)
        finally:
            fileDevice.close()
        return True
    
    def __setAccess(self, account, platform, level):
        p_list = self.projectList.get(platform)
        git = self.createGitlabObject()
        if git is None:
            self.logger.LOGW("无初始化git，权限开通失败")
            return
        try:
            isMember = git.getUserStatus(account)
        except:
            self.logger.LOGE("ConnectionError!")
            self.messageShowed[str].emit("网络连接错误！")
            return
        if isMember:
            self.logger.LOGI("gitlab account:" + str(account))
        else:
            self.messageShowed[str].emit("域账号错误!")
            return
        if platform == '':
            self.messageShowed[str].emit("未选择平台!")
            return
        
        self.__ui.statusbar.showMessage("Access setting ...")
        uid = git.getUserIdByUsername(account)
        print(uid)
        try:
            for path in p_list:
                print(path)
                pid = git.getProjectIdByPath(path)
                if pid == None:
                    self.logger.LOGE("仓库id获取失败:" + path)
                    return
                print('------')
                print(git.isProjectMember(account, pid))
                if git.isProjectMember('laiyuansheng', pid):
                    git.editMemberToProject(uid, pid, level)
                    info = path + ' modified'
                    self.logger.LOGI(info)
                else:
                    git.addMemberToProject(uid, pid, level)
                    info = path + ' added'
                    self.logger.LOGI(info)
                
            self.messageShowed[str].emit("权限开通成功!")
        except Exception as errorMsg:
            self.logger.LOGE(errorMsg)
            self.messageShowed[str].emit("权限开通出错!")
        finally:
            self.__ui.statusbar.showMessage(" ")
            return
    
    def __parseManifestXml(self, fileName, platform):
        handler = xmlHandler()
        ret = True
        try:
            sax.parse(fileName, handler)
            self.projectList[platform] = handler.reposities
            
            with open(self.projectFile, 'wb') as save_project:
                pickle.dump(self.projectList, save_project)
        except Exception as errorMsg:
            self.logger.LOGE('Import platform error:' + str(errorMsg))
            # QMessageBox.critical(self, '错误', '请选择正确的Manifest XML文件！')
            ret = False
        finally:
            # 回收xml解析对象
            del handler
        return ret
    
    def __parseMemberText(self, fileName):
        file = open(fileName, 'r')
        allLines = file.readlines()
        file.close()
        newLine = []
        for strLine in allLines:
            # 去掉末尾的\n
            newLine.append(strLine.strip())
            print(strLine.strip())
        return newLine
    
    def createLogWindow(self):
        log = "./data/exec.log"
        try:
            f = open(log, "r+")
            f.truncate()
            f.close()
        except Exception as msg:
            self.logger.LOGE("IOERROR: " + msg)
        self.logWin = LogView(logFile=log)
        self.logWin.setWindowTitle("log")
        self.logWin.hide()

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        for task in self.__subThreads:
            task.join()
            print('destroy thread')
        self.logWin.close()
        for i in self.__subWindows:
            i.close()
            self.__subWindows.remove(i)
        self.messageShowed.disconnect(self.do_messageShowed_str)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建GUI应用程序
    app.setQuitOnLastWindowClosed(True)
    form = QmyMainWindow()  # 创建窗体
    form.show()
    sys.exit(app.exec_())

# 导出exe:
# pyinstaller mainWindow.py -D --noconsole --add-data data/;data/
