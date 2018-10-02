#encoding: utf8
'''
Created on 2018年10月2日

@author: Administrator
'''
from monitor.BaseMonitor import BasicMonitor
from engine.EventType import *
from _collections import OrderedDict

class LogMonitor(BasicMonitor):
    # ----------------------------------------------------------------------
    def __init__(self, eventEngine, parent=None):
        """Constructor"""
        super(LogMonitor, self).__init__(eventEngine, parent)

        d = OrderedDict()
        d['logTime'] = {'chinese': u'时间', 'cellType': ""}
        d['logContent'] = {'chinese': u'内容', 'cellType': ""}
        # d['gatewayName'] = {'chinese': u'接口', 'cellType': ""}
        self.setHeaderDict(d)

        self.setEventType(EVENT_LOG)
        self.registerEvent()

