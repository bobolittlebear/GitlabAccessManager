# -*- coding: utf-8 -*-

import sys, time
import threading
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QScrollArea)
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ui.ui_LogWidget import Ui_logView


class LogView(QWidget):
    textChanged = pyqtSignal(str)
    
    def __init__(self, parent=None, logFile=''):
        super().__init__(parent)
        self.ui = Ui_logView()
        self.ui.setupUi(self)

        # self.ui.textBrowser.ensureCursorVisible()  # 游标可用
        # cursor = self.ui.textBrowser.textCursor()  # 设置游标
        # pos = len(self.ui.textBrowser.toPlainText())  # 获取文本尾部的位置
        # cursor.setPosition(pos)  # 游标位置设置为尾部
        # self.ui.textBrowser.setTextCursor(cursor)  # 滚动到游标位置

        self.logFile = logFile
        self.textChanged.connect(self.do_textChanged_str)
        
        thread = threading.Thread(target=self.getLogContent)
        thread.start()
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        a0.ignore()
        self.hide()
    
    def getLogContent(self):
        try:
            while True:
                logStream = open(self.logFile, "r")
                content = logStream.read()
                self.textChanged[str].emit(str(content))
                logStream.close()
                time.sleep(0.5)
        except Exception as errorMsg:
            print(errorMsg)
            
    
    @pyqtSlot(str)
    def do_textChanged_str(self, content):
        self.ui.textBrowser.setText(content)
        self.ui.textBrowser.moveCursor(self.ui.textBrowser.textCursor().End)  # 文本框显示到底部


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = LogView(logFile="./data/exec.log")
    form.setWindowTitle("log")
    form.show()
    # form.hide()
    sys.exit(app.exec_())
