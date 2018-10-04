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
        
        #成功登录账户
        self.accountInfo = {}
        
        
        #目标股票交易计划
        self.targetStocks = {}
        """
        { 
            "stockcode1":{'price':price,'amount':amount }
            "stockcode2":{'price':price,'amount':amount }
            "stockcode3":{'price':price,'amount':amount }
        }
        """
        #用户的委托单号
        self.activeBookCodeLists = {}
        """
        {
            'username1':['bookOrder1',...],
            'username2':['bookOrder1',...],
            'username3':['bookOrder1',...]
        }
        """
        
        
    #--------------------------------------------------------------
    def init(self):
        #初始化数据
        self.accountRegister()
        
        
        #初始化相应的tradeApi
        self.tradeApi = TradeApi(self)
        self.tradeApi.init()
        #初始化相应选中用户数
        self.selectedAccountsLen = len(self.selectedAccounts)
    
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
        #登录操作
        self.eventEngine.register(EVENT_LOGIN,self.getClientId)
        #交易操作
        self.eventEngine.register(EVENT_TRADE_PLAN,self.getTrade)
        #撤单操作
        self.eventEngine.register(EVENT_TRADE_CANCEL,self.getCancel)

    #--------------------------------------------------------------
    def startLogin(self):
        #开始登陆
        event = Event()
        event.type_ = EVENT_LOGIN
        self.eventEngine.put(event)
    
    #--------------------------------------------------------------
    def startTrade(self):
        #开始交易
        event = Event()
        event.type_ = EVENT_TRADE_PLAN
        self.eventEngine.put(event)
    
    #--------------------------------------------------------------
    
    def startCancel(self):
        #开始撤销
        event = Event()
        event.type_ = EVENT_TRADE_CANCEL
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
            return True


#多线程争夺资源问题
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
    def getTrade(self,event):
        try:
            username,info = self.accountInfo.popitem()
            for stockcode,plan in self.targetStocks.items():
                clientId = info['clientId']
                szCode = info['sz']
                shCode = info['sh']
                stockPrice = plan['price']
                stockAmount = plan['amount']
                stockSide = plan['side']
                if stockcode[0] == '3' or stockcode == '0':
                    self.tradeApi.getSendOrder(username,szCode, stockcode, stockPrice, stockAmount, stockSide, clientId)
                else:
                    self.tradeApi.getSendOrder(username,shCode, stockcode, stockPrice, stockAmount, stockSide, clientId)
            return True
        except Exception as e:
            pass
    #--------------------------------------------------------------
    def getCancel(self,event):
        try:
            userName,bookList = self.activeBookCodeLists.popitem()
            for entity in bookList:
                bookCode,stockCode,clientId = entity
                #判断为上海或者深圳
                if stockCode[0] == '3' or stockCode[0] == '0':
                    exchangetype = 0
                else:
                    exchangeType = 1
                self.tradeApi.getCancelOrder(userName, bookCode, exchangetype,clientId)
        except Exception as e:
            pass

        
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
        username = data[0]
        params = data[1]
        self.accountInfo[username] = params
        print(self.accountInfo)
    #--------------------------------------------------------------
    def onGetTrade(self,data,reqid):
        #获取完成相应的用户交易
        userLen = self.selectedAccountsLen
        stockLen = len(self.targetStocks)
        status = (reqid - userLen) % stockLen
        if status == 0:
            event = Event()
            event.type_ = EVENT_TRADE_PLAN
            self.eventEngine.put(event)
        username,content,stockcode,clientid = data
        try:
            bookList = self.activeBookCodeLists[username]
        except KeyError:
            bookList = []
            self.activeBookCodeLists[username] = bookList
        
        if not content.isdigit():
            print("error data %s" %content)
        else:
            book = (content,stockcode,clientid)
            bookList.append(book)
            print(content)
    #--------------------------------------------------------------
    def onGetCancel(self,data,reqid):
        #取消成功
        username,bookcode,status = data
        if not status == 1:
            outstr = "%s 未取消 %s 委托" %(username,bookcode)
            print(outstr)
        else:
            outstr = "%s 取消 %s 委托" %(username,bookcode)
            print(outstr)
        #往队列中发出清空下一用户的全部委托单
        userLen = self.selectedAccountsLen
        stockLen = len(self.targetStocks)
        status = (reqid - userLen)% stockLen 
        if not status == 1:
            event = Event()
            event.type_ = EVENT_TRADE_CANCEL
            self.eventEngine.put(event)

        
        
        
        


class TradeApi(BaseApi):
    
    
    def __init__(self,dispatcher):

        super(TradeApi,self).__init__()
        #获取相应调度者
        self.dispatcher = dispatcher
    
    #--------------------------------------------------------------------------------------------- 
    def onGetLogin(self, data, reqid):
        #完成一用户登录
        self.dispatcher.onGetClientId(data)
        #更新轮询
        event = Event()
        event.type_ = EVENT_LOGIN
        self.dispatcher.eventEngine.put(event)
    #--------------------------------------------------------------------------------------------- 
    def onSendOrder(self,data,reqid):
        #完成一次交易
        self.dispatcher.onGetTrade(data,reqid)
    #--------------------------------------------------------------------------------------------- 
    def onCancelOrder(self,data,reqid):
        self.dispatcher.onGetCancel(data,reqid)


        
        
        
        
    