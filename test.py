#encoding: utf-8
'''
Created on 2018年10月1日

@author: Administrator
'''

from tkinter import *
from api.TradeApi import *

if __name__ == "__main__":
    root = Tk()
    tradeApi = TradeApi()
    tradeApi.init()
    tradeApi.start()
    tradeApi.getLogin('113.105.77.163','2.28','50506031','375228', '','0')
    root.mainloop()

