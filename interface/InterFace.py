#encoding: utf-8
'''
Created on 2018年8月2日

@author: Administrator
'''
import tkinter
from tkinter import * 
from tkinter import messagebox
from tkinter import ttk

PROGRAM_NAME = "下单"
class QuickTrade():

    def __init__(self,root,all_user_info,trade_queue,condition_lock):
        self.root = root
        self.root.title(PROGRAM_NAME)
        #所有用户相应信息
        self.all_user_info = all_user_info
        #选择用户的名单列表 
        self.all_select_user_index = []
        #相应的通信队列 
        self.trade_queue = trade_queue
        #相应的消息通信条件
        self.trade_condition = condition_lock

        self.init_gui()
    
    
    

    #初始化相应的界面     
    
    def init_gui(self):
        self.init_up_gui()
        self.init_middle_gui()
        self.init_down_gui()

    def init_up_gui(self):
        up_frame = Frame(self.root)
        up_frame.grid(row = 0,column = 0,columnspan = 5)
        #名称
        Label(up_frame,text='所有用户').grid(row = 0,column = 0,sticky = 'w',padx = 5)
        Label(up_frame,text='操作用户').grid(row = 0,column = 3,sticky = 'w',padx = 5)
        #所有用户表
        self.user_list = StringVar()
        self.all_client_list = Listbox(up_frame,listvariable=self.user_list,width = 20,height=10,selectmode=SINGLE)
        self.all_client_list.grid(row = 1,column = 0,columnspan = 2,rowspan = 2,padx = 5)
        if self.all_user_info != None:
            for key,value in self.all_user_info.items():
                self.all_client_list.insert(END,str(key))
        
        #选择用户表
        self.select_user_list = StringVar()
        self.selected_user_list =  Listbox(up_frame,listvariable=self.select_user_list,width = 20,height=10,selectmode=SINGLE)
        self.selected_user_list.grid(row = 1,column = 3,columnspan = 2,rowspan = 2,padx = 5)
        #选择与 取消按键
        select_btn = Button(up_frame,text = '选择用户>',command = self.select_btn_down)
        select_btn.grid(row = 1,column = 2)
        unselect_btn = Button(up_frame,text = '<取消用户',command = self.unselect_btn_down)
        unselect_btn.grid(row = 2,column =2)

    def init_middle_gui(self):
        middle_frame = Frame(self.root)
        middle_frame.grid(row = 2,column = 0)
        #名称
        Label(middle_frame,text='操作股票').grid(row = 0,column = 0,sticky = 'w',padx = 5)
        Label(middle_frame,text='下单数量').grid(row = 2,column = 0,sticky = 'w',padx = 5)
        Label(middle_frame,text='下单价格').grid(row = 2,column = 1,sticky = 'w',padx = 40)
        #相应输入框
        self.target_stock = StringVar()
        self.target_stock_entry = Entry(middle_frame,text = self.target_stock)
        self.target_stock_entry.grid(row = 1,column = 0 ,sticky = 'w')
        self.target_amount = StringVar()
        self.target_amount_entry = Entry(middle_frame,text = self.target_amount,width = 20)
        self.target_amount_entry.grid(row = 3,column = 0,sticky = 'w')
        self.target_price = StringVar()
        self.target_price_entry = Entry(middle_frame,text = self.target_price,width = 20)
        self.target_price_entry.grid(row = 3,column = 1,padx = 40)
        #查询股票按键
        query_stock_btn = Button(middle_frame,text = '查询股票',command = self.query_stock_btn_down)
        query_stock_btn.grid(row = 1,column = 1,columnspan = 5,pady = 5)



        



    def init_down_gui(self):
        down_frame = Frame(self.root)
        down_frame.grid(row = 3,column = 0)
        #名称
        Label(down_frame,text='操作结果').grid(row = 0,column = 0,sticky='w',padx = 5)
        #输出结果框
        #选择用户表
        self.res_out_txt =  Text(down_frame,width = 52,height=5)
        self.res_out_txt.grid(row = 1,column = 0,columnspan = 5,padx=5)
        self.res_out_txt.insert(END,"暂时未有成交记录\n")
        self.res_out_txt.insert(END,"等待交易")
        trade_btn = Button(down_frame,text = '下单',command = self.trade_btn_down,width = 52)
        trade_btn.grid(row = 2,column = 0,columnspan = 5,pady = 5)
    
    #按键操作函数
    def select_btn_down(self):
        pass
    def unselect_btn_down(self):
        pass
    def trade_btn_down(self):
        pass
    def query_stock_btn_down(self):
        pass


if __name__ == '__main__':
    root = Tk()
    root.geometry("380x420")
    QuickTrade(root)
    root.mainloop()

    