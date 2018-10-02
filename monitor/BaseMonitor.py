#encoding: utf8
'''
Created on 2018年10月2日

@author: Administrator
'''
########################################################################
from _collections import OrderedDict
import logging
import types



class BasicMonitor(object):
    """ 基础监控

    headerDict中的值对应的字典格式如下
    {'chinese': u'中文名', 'cellType': ""}

    """

    # ----------------------------------------------------------------------
    def __init__(self, eventEngine=None, parent=None):
        self.eventEngine = eventEngine

        # 保存表头标签用
        self.headerDict = OrderedDict()  # 有序字典，key是英文名，value是对应的配置字典
        self.headerList = []             # 对应self.headerDict.keys()

        # 保存相关数据用
        self.dataDict = {}  # 字典，key是字段对应的数据，value是保存相关单元格的字典
        self.dataKey = ''   # 字典键对应的数据字段

        # 监控的事件类型
        self.eventType = ''

        # 保存数据对象到单元格
        self.saveData = False

    # ----------------------------------------------------------------------
    def setHeaderDict(self, headerDict):
        """设置表头有序字典"""
        self.headerDict = headerDict
        self.headerList = headerDict.keys()

    # ----------------------------------------------------------------------
    def setDataKey(self, dataKey):
        """设置数据字典的键"""
        self.dataKey = dataKey

    # ----------------------------------------------------------------------
    def setEventType(self, eventType):
        """设置监控的事件类型"""
        self.eventType = eventType

    # ----------------------------------------------------------------------
    def setSaveData(self, saveData):
        """设置是否要保存数据到单元格"""
        self.saveData = saveData

    # ----------------------------------------------------------------------
    def registerEvent(self):
        self.eventEngine.register(self.eventType, self.updateEvent)

    # ----------------------------------------------------------------------
    def updateEvent(self, event):
        """收到事件更新"""
        data = event.dict_['data']
        self.updateData(data)

    # ----------------------------------------------------------------------
    def updateData(self, data):
        """将数据更新到表格中"""
        s = []
        for header, value in self.headerDict.items():
            v = getattr(data, header)
#             if isinstance(v, basestring) and not isinstance(v, unicode):
            if v:
                try:
                    v = v.decode('utf8')
                except:
                    v = v.decode('gbk')
            s.append('%s: %s' % (value['chinese'], v))
        logging.info(' '.join(s))


