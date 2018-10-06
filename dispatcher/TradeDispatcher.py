#encoding: utf8
'''
Created on 2018年10月2日

@author: Administrator
'''

from dispatcher.BaseDispatcher import *
from api.BaseApi import BaseApi
from asyncio.tasks import sleep
import os
import json
import threading

class TradeDispatcher(BaseDispatcher):
    #交易调度
    #--------------------------------------------------------------
    def __init__(self,interface,eventEngine):
        super(TradeDispatcher,self).__init__(eventEngine,'TradeDispatcher')
        #界面
        self.interface = interface
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
        #创建相应的内部线程锁
        self.lock = threading.Lock()
        
        
    #--------------------------------------------------------------
    def init(self):
        #初始化数据
        self.accountRegister()
        self.stocksRegister()
        
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
            sz = info['sz']
            sh = info['sh']
            self.tradeApi.getLogin(ip, version, username, password, txword, yyb,sz,sh)
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
            exchangetype = 1
            userName,bookList = self.activeBookCodeLists.popitem()
            if not bookList:
                self.startCancel()
                return 
            for entity in bookList:
                bookCode,stockCode,clientId = entity
                #判断为上海或者深圳
                if stockCode[0] == '3' or stockCode[0] == '0':
                    exchangetype = 0
                else:
                    exchangeType = 1
                self.tradeApi.getCancelOrder(userName, bookCode, exchangetype,clientId,stockCode)
        except Exception as e:
            print(e)
            pass

        
    #--------------------------------------------------------------
    def accountRegister(self):
        #加载相应的分配账户
        filename = os.getcwd() + '/DispatcherCache/'+'RegisterAccounts.json'
#         filename =  '../DispatcherCache/'+'RegisterAccounts.json'
        try:
            f = open(filename,'r')
            self.registeredAccounts = json.load(f)
        except IOError:
            pass
        return self.registeredAccounts

    #--------------------------------------------------------------
    def stocksRegister(self):
        #加载相应的股票计划
        filename = os.getcwd() + '/DispatcherCache/' + 'TargetStocks.json'
#         filename = '../DispatcherCache/' + 'TargetStocks.json'
        try:
            f = open(filename,'r')
            self.targetStocks = json.load(f)
        except IOError:
            pass 
        return self.targetStocks




    #--------------------------------------------------------------
    def addActiveAccount(self,username):
        """增加激活用户"""
        try:
            selectedAccount = self.registeredAccounts[username]
            self.selectedAccounts[username] = selectedAccount
        except KeyError:
            pass
    
    #--------------------------------------------------------------
    def removeActiveAccount(self,username):
        """删除激活用户"""
        try:
            del self.selectedAccounts[username]
            print(self.selectedAccounts)
        except Exception as e:
            pass
    
    #--------------------------------------------------------------
    def onGetClientId(self,data):
        #获取相应的用户登录id
        username = data[0]
        params = data[1]
        self.accountInfo[username] = params
        print(self.accountInfo)
        self.interface.addLog(username + "登录成功\n")
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
        self.lock.acquire()
        try:
            bookList = self.activeBookCodeLists[username]
        except KeyError:
            bookList = []
            self.activeBookCodeLists[username] = bookList
        self.lock.release()
        if not content.isdigit():
            print("error data %s" %content)
            self.interface.addLog(username + "未完成" + stockcode +"委托\n")
        else:
            book = (content,stockcode,clientid)
            bookList.append(book)
            self.interface.addLog(username + "完成" + stockcode +"委托\n")
            print(content)
        print(self.activeBookCodeLists)
    #--------------------------------------------------------------
    def onGetCancel(self,data,reqid):
        #取消成功
        username,bookcode,stockcode,status = data
        if not status == 1:
            outstr = "%s 未取消 %s 委托" %(username,bookcode)
            print(outstr)
            self.interface.addLog(username + "未完成"+ stockcode +":" + bookcode +"委托撤销\n")
        else:
            outstr = "%s 取消 %s 委托" %(username,bookcode)
            print(outstr)
            self.interface.addLog(username + "完成"+ stockcode +":" + bookcode +"委托撤销\n")
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


        
        
        
        
    