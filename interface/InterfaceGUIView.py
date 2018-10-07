#encoding: utf8
'''
Created on 2018年10月4日

@author: Administrator
'''

from tkinter import *
from tkinter import ttk
import tkinter as tk
import os
import json
from dispatcher.TradeDispatcher import TradeDispatcher
from engine.EventEngine import EventEngine
from engine.EventType import EVENT_LOGIN,EVENT_GUI_LOGIN
import datetime
from sqlalchemy.sql.expression import column


class InterfaceView(object):
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Trade')
        self.window.resizable(False,False)
        
        #所有可操作账户信息
        self.all_user_info = None
        #所有交易目标股票
        self.all_target_stocks = None
        #所有的选择用户列表
        self.all_select_user_index = []
        #当前操作用户
        self.selectedAccounts = {}
        
        self.init_gui()

    #初始化相应的数据
    def init(self,all_user_info,targetStocks):
        #初始化相应的基本数据
        self.all_user_info = all_user_info
        self.all_target_stocks = targetStocks


    
    #初始化相应的界面     
    def init_gui(self):
        self.init_up_gui()
        self.init_middle_gui()
        self.init_down_gui()

    def init_up_gui(self):
        up_frame = Frame(self.window)
        up_frame.grid(row = 0,column = 0,columnspan = 5)
        #名称
        Label(up_frame,text='所有用户').grid(row = 0,column = 0,sticky = 'w',padx = 5)
        Label(up_frame,text='操作用户').grid(row = 0,column = 3,sticky = 'w',padx = 5)
        #所有用户表
        self.user_list = StringVar()
        self.all_client_list = Listbox(up_frame,listvariable=self.user_list,width = 20,height=10,selectmode=SINGLE)
        self.all_client_list.grid(row = 1,column = 0,columnspan = 2,rowspan = 2,padx = 5)
        #选择用户表
        self.select_user_list = StringVar()
        self.selected_user_list =  Listbox(up_frame,listvariable=self.select_user_list,width = 20,height=10,selectmode=SINGLE)
        self.selected_user_list.grid(row = 1,column = 3,columnspan = 2,rowspan = 2,padx = 5)
        #选择与 取消按键
        self.select_btn = Button(up_frame,text = '选择用户>')
        self.select_btn.grid(row = 1,column = 2)
        self.unselect_btn = Button(up_frame,text = '<取消用户')
        self.unselect_btn.grid(row = 2,column =2)

    def init_middle_gui(self):
        middle_frame = Frame(self.window)
        middle_frame.grid(row = 2,column = 0)
        #名称
        Label(middle_frame,text='操作股票').grid(row = 0,column = 0,sticky = 'w',padx = 5)
        #相应输入框
        self.target_stock = StringVar()
        self.target_plan = Listbox(middle_frame,listvariable = self.target_stock,width = 50)
        self.target_plan.grid(column = 0,row = 3,columnspan = 3)
        #相应的操作
        self.addButton = Button(middle_frame,text = "+增加股票")
        self.addButton.grid(column = 0,row = 4)
        self.delButton = Button(middle_frame,text = "-减去股票")
        self.delButton.grid(column = 1,row = 4)
        self.saveButton= Button(middle_frame,text="保存计划")
        self.saveButton.grid(column = 2,row = 4)

    def init_down_gui(self):
        down_frame = Frame(self.window)
        down_frame.grid(row = 3,column = 0)
        #名称
        Label(down_frame,text='操作结果').grid(row = 0,column = 0,sticky='w',padx = 5)
        #输出结果框
        #选择用户表
        self.res_out_txt =  Text(down_frame,width = 52,height=5)
        self.res_out_txt.grid(row = 1,column = 0,columnspan = 5,padx=5)
        self.res_out_txt.insert(END,"暂时未有成交记录\n")
        self.res_out_txt.insert(END,"等待交易")

        #启动按键
        self.login_btn = Button(down_frame,text = '启动选择用户',width = 52)
        self.login_btn.grid(row = 2,column = 0,columnspan = 5,pady = 5)

        #执行交易按键
        self.trade_btn = Button(down_frame,text = '计划交易下单',width = 52)
        self.trade_btn.grid(row = 3,column = 0,columnspan = 5,pady = 5)
        #取消委托
        self.trade_cancel_btn = Button(down_frame,text = '撤销委托下单',width = 52)
        self.trade_cancel_btn.grid(row = 4,column = 0,columnspan = 5,pady = 5)
    
    
    def addRes(self,data):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        outstr = now +  ':' + data
        self.res_out_txt.insert(END,outstr)
   


class InterfaceController(object):

    def __init__(self):
        self.dispatcher = None
        self.interface = None
        self.eventEngine  = EventEngine()
    
    def registerFunc(self):
        self.dispatcher.eventEngine.register(EVENT_GUI_LOGIN,self.initGuiUser)
        self.dispatcher.eventEngine.register(EVENT_LOGIN,self.loginStatus)
    
    def init(self):
        self.dispatcher = TradeDispatcher(self,self.eventEngine)
        self.dispatcher.init()
        self.dispatcher.registerLogin()
        self.dispatcher.start()
        #初始化所有的用户信息
        all_user_info = self.dispatcher.accountRegister()
        targetStocks = self.dispatcher.stocksRegister()
        self.interface = InterfaceView()
        self.interface.init(all_user_info,targetStocks)
        
        
        event = Event()
        event.type_ = EVENT_GUI_LOGIN
        self.dispatcher.eventEngine.put(event)
    
    def initGuiUser(self,event):
        #初始化所有的用户信息
        if self.interface.all_user_info != None:
            for key,value in self.interface.all_user_info.items():
                self.interface.all_client_list.insert(END,str(key))
        #初始化所有的交易股票信息
        self.initTradePlan()
        

    def initTradePlan(self):
        self.interface.target_plan.delete(0,END)
        if self.interface.all_target_stocks != None:
            for key,value in self.interface.all_target_stocks.items():
                outstr = ''
                if value['side'] == 0:
                    outstr = str(key) + ":" + " "*4 +"以价格" + str(value['price'])+ " 元 " + "买入" + str(value['amount']) + " 股"
                else:
                    outstr = str(key) + ":" + " "*4 +"以价格" + str(value['price'])+ " 元"  +" 卖出" + str(value['amount']) + " 股"
                self.interface.target_plan.insert(END,outstr)

    
    def run(self):
        #用户选择按键
        self.interface.select_btn.bind('<Button-1>',self.select_btn_down)
        self.interface.unselect_btn.bind('<Button-1>',self.unselect_btn_down)
        #总体交易计划操作按键
        self.interface.trade_btn.bind('<Button-1>',self.trade_btn_down)
        self.interface.trade_cancel_btn.bind('<Button-1>',self.trade_cancel_btn_down)
        self.interface.login_btn.bind('<Button-1>',self.login_btn_down)
        #操作股票操作按键
        self.interface.addButton.bind('<Button-1>',self.addTargetStock)
        self.interface.delButton.bind('<Button-1>',self.delTargetStock)
        self.interface.saveButton.bind('<Button-1>',self.saveTargetStock)
        self.interface.window.mainloop()
    
    #按键操作函数
    def select_btn_down(self,event):
        user_pos = self.interface.all_client_list.curselection()
        if user_pos != None:
            selected_user = self.interface.all_client_list.get(user_pos)
            self.interface.all_client_list.delete(user_pos)
            self.interface.selected_user_list.insert(END,selected_user)
            self.interface.all_select_user_index.append(selected_user)
            self.dispatcher.addActiveAccount(selected_user)
    
    def unselect_btn_down(self,event):
        user_pos = self.interface.selected_user_list.curselection()
        if user_pos != None:
            selected_user = self.interface.selected_user_list.get(user_pos)
            self.interface.selected_user_list.delete(user_pos)
            self.interface.all_client_list.insert(END,selected_user)
            self.interface.all_select_user_index.remove(selected_user)
            self.dispatcher.removeActiveAccount(selected_user)
    
    #---------------------------------------------------------------------------------
    def login_btn_down(self,event):
        #登录选择账户
        self.interface.res_out_txt.delete(0.0,END)
        self.dispatcher.startLogin()
    
    
    #---------------------------------------------------------------------------------
    def trade_btn_down(self,event):
        #提交相应交易
        self.dispatcher.startTrade()
    
    def trade_cancel_btn_down(self,event):
        print(self.dispatcher.activeBookCodeLists)
        #结束相应的交易
        self.dispatcher.startCancel()
    
    def loginStatus(self,event):
        selectedUserLen = len(self.interface.all_select_user_index)
        index = ''
        for i in range(selectedUserLen):
            index = self.interface.selected_user_list.get(i)
            if not index in self.dispatcher.selectedAccounts:
                self.interface.selected_user_list.itemconfig(i,bg='green')

    def addLog(self,data):
        self.interface.addRes(data)
        
        
    def addTargetStock(self,event):
        top = Toplevel()
        top.title('新增股票')
        top.resizable(False,False)
        
        self.targetStock = StringVar()
        self.targetPrice = StringVar()
        self.targetAmount = StringVar()
        self.side = StringVar()

        stockLabel = Label(top,text='股票')
        stockLabel.grid(column = 0,row = 0)
        priceLabel = Label(top,text='价格')
        priceLabel.grid(column = 1,row = 0)
        amountLabel = Label(top,text='数量')
        amountLabel.grid(column = 2,row = 0)
        sideLabel = Label(top,text='操作')
        sideLabel.grid(column = 3,row = 0)

        self.stockEntry = Entry(top,textvariable=self.targetStock,width = 20)
        self.stockEntry.grid(column = 0,row = 1,padx = 5)
        self.priceEntry = Entry(top,textvariable=self.targetPrice,width = 20)
        self.priceEntry.grid(column = 1,row = 1,padx = 5)
        self.amountEntry = Entry(top,textvariable=self.targetAmount,width = 20)
        self.amountEntry.grid(column = 2,row = 1)

        self.sideCombo = ttk.Combobox(top, textvariable=self.side)
        self.sideCombo['values'] = ("买入","卖出")
        self.sideCombo.grid(column=3,row = 1,padx = 5)
        
        
        self.confirmAddButton = Button(top,text = '确认添加',command=self.addPlanStock,width = 20)
        self.confirmAddButton.grid(column = 3,row =2,pady = 2)
        
    def addPlanStock(self):
        infoEntity = {}
        stockcode = self.stockEntry.get()
        price = self.priceEntry.get()
        amount = self.amountEntry.get()
        if self.sideCombo.get() == "买入":
            side = 0
        else:
            side = 1
        infoEntity['price'] = float(price)
        infoEntity['amount'] = int(amount)
        infoEntity['side'] = side
        if len(stockcode) < 6:
            stockcode = "0"*(6-len(stockcode)) + stockcode
        self.dispatcher.targetStocks[stockcode] = infoEntity
        self.initTradePlan()

    def delTargetStock(self,event):
        try:
            index = self.interface.target_plan.curselection()
            info = self.interface.target_plan.get(index)
            key = info.split(':')[0]
            if key in self.dispatcher.targetStocks.keys():
                del self.dispatcher.targetStocks[key]
            self.initTradePlan()

        except EXCEPTION as e:
            pass
    
    def saveTargetStock(self,event):
        try:
            filename = os.getcwd() + '/DispatcherCache/'+'TargetStocks.json'
#             filename = '../DispatcherCache/'+'TargetStocks.json'
            f = open(filename,'w')
            json.dump(self.dispatcher.targetStocks,f)
        except EXCEPTION as e:
            pass
    
    def tradeStatus(self):
        pass

if __name__ == "__main__":
    tmp = InterfaceController()
    tmp.init()
    tmp.registerFunc()
    tmp.run()
    
