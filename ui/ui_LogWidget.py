# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logview.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_logView(object):
    def setupUi(self, logView):
        logView.setObjectName("logView")
        logView.resize(369, 269)
        self.scrollArea = QtWidgets.QScrollArea(logView)
        self.scrollArea.setGeometry(QtCore.QRect(10, 10, 351, 251))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 349, 249))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget.setGeometry(QtCore.QRect(0, 0, 351, 251))
        self.widget.setObjectName("widget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.widget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 351, 251))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.textBrowser.setFont(font)
        self.verticalLayout.addWidget(self.textBrowser)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(logView)
        QtCore.QMetaObject.connectSlotsByName(logView)

    def retranslateUi(self, logView):
        _translate = QtCore.QCoreApplication.translate
        logView.setWindowTitle(_translate("logView", "Form"))
