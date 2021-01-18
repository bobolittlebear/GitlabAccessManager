import os
from xml import sax
import json


# 定义自己的handler类，继承sax.ContentHandler
class ManifestHandler(sax.ContentHandler):
    def __init__(self):
        # 父类和子类都需要初始化, 做一些变量的赋值操作等
        sax.ContentHandler.__init__(self)
        self._content = ""
        self._tag = ""
        self.remote = {}
        self.reposities = []
    
    # 重写startElement：遇到<tag>标签时候会执行的方法
    def startElement(self, name, attrs):
        self._tag = name
        if name == "manifest":
            # print("======manifest======")
            pass
        elif self._tag == "remote":
            tmp = attrs['fetch'].split('/')
            # 使用‘/’分割字符串后取倒数第一个值，index=-1
            self.remote[attrs['name']] = tmp[-1]
            # self.remote[attrs['name']] = attrs['fetch']
        elif self._tag == "project":
            if 'remote' in attrs:
                self.reposities.append(self.remote[attrs['remote']] + '/' + attrs['name'])
                # print(self.remote[attrs['remote']] + '/' + attrs['name'])
            
            else:
                self.reposities.append(self.remote['origin'] + '/' + attrs['name'])
                # print(self.remote['origin'] + '/' + attrs['name'])
    
    # 重写endElement：遇到<tag>标签时候会执行的方法，这里的name，attrs不用自己传值的
    def endElement(self, name):
        if name == 'manifest':
            pass
            # print("======manifest=======")

