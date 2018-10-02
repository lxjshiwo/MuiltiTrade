#encoding: utf8
'''
Created on 2018年10月2日

@author: Administrator
'''

from dispatcher.BaseDispatcher import *
from api.BaseApi import BaseApi
from asyncio.tasks import sleep

class TradeDispatcher(BaseDispatcher):
    #交易调度
    #--------------------------------------------------------------
    def __init__(self,eventEngine):
        super(TradeDispatcher,self).__init__(eventEngine,'TradeDispatcher')
        #信号引擎
        self.eventEngine = eventEngine
        self.eventEngine.start()
        #交易api
        self.tradeApi = None

        #选中的交易账户
        self.selectedAccounts = {}
        #分配到的交易账户
        """
        { 
            "username1":{ip':ip ... }
            "username2":{ip':ip ... }
            "username3":{ip':ip ... }
        }
        """
        self.registeredAccounts = {}
        
        #账户登录号 
        self.accountClientId = {}
        
        
    #--------------------------------------------------------------
    def init(self):
        #初始化数据
        self.accountRegister()
        
        
        #初始化相应的tradeApi
        self.tradeApi = TradeApi(self)
        self.tradeApi.init()
    
    def start(self):
        #开启
        self.tradeApi.start()
    
    def close(self):
        #关闭
        self.eventEngine.stop()
        self.tradeApi.close()
    #--------------------------------------------------------------
    def registerLogin(self):
        #注册相应的登录操作
        self.eventEngine.register('eLogin',self.getClientId)

    #--------------------------------------------------------------
    def startLogin(self):
        event = Event()
        event.type_ = 'eLogin'
        self.eventEngine.put(event)

    #--------------------------------------------------------------
    def getClientId(self,event):
        if not self.selectedAccounts:
            return False
        else:
            username,info = self.selectedAccounts.popitem()
            ip = info['ip']
            version = info['version']
            password = info['password']
            txword = info['txword']
            yyb = info['yyb']
            self.tradeApi.getLogin(ip, version, username, password, txword, yyb)


#         if not self.selectedAccounts:
#             return False
#         else:
#             for username,info in self.selectedAccounts.items():
#                 ip = info['ip']
#                 version = info['version']
#                 password = info['password']
#                 txword = info['txword']
#                 yyb = info['yyb']
#                 self.tradeApi.getLogin(ip, version, username, password, txword, yyb)
#             return True
    
    #--------------------------------------------------------------
    def accountRegister(self):
        #加载相应的分配账户
        pass



    #--------------------------------------------------------------
    def addActiveUser(self):
        """增加激活用户"""
        pass
    
    #--------------------------------------------------------------
    def removeActiveUser(self):
        """删除激活用户"""
        pass
    
    #--------------------------------------------------------------
    def onGetClientId(self,data):
        #获取相应的用户登录id
        print(data)


class TradeApi(BaseApi):
    
    
    def __init__(self,dispatcher):

        super(TradeApi,self).__init__()
        #获取相应调度者
        self.dispatcher = dispatcher
    
    
    def onGetLogin(self, data, reqid):
        self.dispatcher.onGetClientId(data)
        event = Event()
        event.type_ = 'eLogin'
        self.dispatcher.eventEngine.put(event)
        
        
        
        
    