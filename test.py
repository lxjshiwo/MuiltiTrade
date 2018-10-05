#encoding: utf-8
'''
Created on 2018年10月1日

@author: Administrator
'''

from tkinter import *
from api.BaseApi import *
from dispatcher.TradeDispatcher import *
from engine.EventEngine import EventEngine
import time

if __name__ == "__main__":
    root = Tk()
    eventEngine = EventEngine()
    tDispatcher = TradeDispatcher(eventEngine)
    tDispatcher.init()
    tDispatcher.start()
    tDispatcher.selectedAccounts = {
                                    '50506031':{'ip':'113.105.77.163','version':'2.28','password':'375228','txword':'','yyb':'0','sz':'','sh':''},
#                                     '18041349':{'ip':'114.141.165.219','version':'2.28','password':'600006','txword':'','yyb':'78','sz':'','sh':''},
#                                     '18043120':{'ip':'114.141.165.219','version':'2.28','password':'330228','txword':'','yyb':'78','sz':'','sh':''},
                                    }
    tDispatcher.targetStocks = {
                                    '000100':{
                                            'price':3,
                                            'amount':100,
                                            'side':0
                                            },
                                    '600010':{
                                            'price':3,
                                            'amount':100,
                                            'side':0
                                            }
                                    }
    tDispatcher.registerLogin()
    tDispatcher.startLogin()
    time.sleep(5)
    tDispatcher.startTrade()
    time.sleep(5)
    tDispatcher.startCancel()
#     tDispatcher.getClientId()
#     tradeApi = TradeApi(tDispatcher)
#     tradeApi.init()
#     tradeApi.start()
#     tradeApi.getLogin('113.105.77.163','2.28','50506031','375228', '','0')
#     tradeApi.getLogin('113.105.77.163','2.28','50506031','375228', '','0')
    root.mainloop()


