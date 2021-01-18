# -*- coding: UTF-8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QTableWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui.ui_TableWindow import Ui_QTableWindow
from module.api_http_gitlab import GitlabAPI
from config import *

class TableWindow(QMainWindow):
    
    def __init__(self, parent=None, gitPath=None, token=None):
        super().__init__(parent)  # 调用父类构造函数，创建窗体
        self.ui = Ui_QTableWindow()  # 创建UI对象
        self.ui.setupUi(self)  #    构造UI界面
        self.gitPath = gitPath
        self.__token = token

        self.members = self.getMemberList()
        print(len(self.members))
        self.__rowNum = len(self.members)
        self.__colNum = 3

        # 设置table view不可编辑
        self.ui.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAutoFillBackground(True)
        # 设置ui标题和位置
        self.setWindowTitle(str(self.gitPath) + "成员权限")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()
        x = self.x() + self.ui.centralwidget.width() + 10
        y = self.y()
        self.move(x, y)
        
        
        # 构建Model/View
        self.itemModel = QStandardItemModel(self.__rowNum, self.__colNum, self)  # 数据模型,n行3列
        self.selectionModel = QItemSelectionModel(self.itemModel)  # Item选择模型
        self.ui.tableView.setModel(self.itemModel)  # 设置数据模型
        self.ui.tableView.setSelectionModel(self.selectionModel)  # 设置选择模型
        
        self.setTableHeader()
        self.__createItemsARow()

        self.ui.statusbar.showMessage("仓库：" + str(self.gitPath) + "    成员人数：" + str(self.__rowNum))
        
        
    #QTableWidget 设置表头和行数
    def setTableHeader(self):
        headText = ["姓 名", "域账号", "权限级别"]
        self.itemModel.setColumnCount(len(headText))
        self.itemModel.setHorizontalHeaderLabels(headText)
        
       
    def getMemberList(self):
        try:
            gl = GitlabAPI(GITLAB_URL, self.__token)
            pid = gl.getProjectIdByPath(self.gitPath)
            members = gl.listProjectMembers(pid)
        except Exception as errorMsg:
            self.logger.LOGE("ConnectionError!")
            self.messageShowed[str].emit("网络连接错误！")
            return
        return members

    def __getRowsValue(self):
        rowsValue = []
        accessDict = {
            10: "Guest",
            20: "Reporter",
            30: "Developer",
            40: "Maintainer",
            50: "Owner"
        }
        for user in self.members:
            row = []
            row.append(user['name'])
            row.append(user['username'])
            row.append(accessDict[user['access_level']])
            row.append(user['access_level'])
            print(row)
            rowsValue.append(row)
        return rowsValue
     
    def __createItemsARow(self):
        rowsValue = self.__getRowsValue()
        # 按权限级别排序
        rowsValue.sort(key=self.__sortList, reverse=True)
        
        for i in range(self.__rowNum):
            row = rowsValue[i]
            for j in range(self.__colNum):
                item = QStandardItem(row[j])
                self.itemModel.setItem(i, j, item)
    
    def __sortList(self, elem):
        return elem[-1]


if  __name__ == "__main__":
   app = QApplication(sys.argv)
   form=TableWindow(gitPath='seewosystem/3399_9', token='Y8-wVCBS2Wzush7p38xv')
   form.show()
   sys.exit(app.exec_())
