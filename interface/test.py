#encoding: utf-8
'''
@author: lxj
'''
import Trader
from Trader import *
from ctypes import *
import Constant
import math
import time
import os
import copy
import json
import InterFace
from InterFace import *
import queue
from queue import Queue
# from multiprocessing.context import Process


hx_trader_ip = "202.99.230.133"
hx_trader_port =7708
hx_trader_user ="67200134"
hx_trader_password ="527727"
hx_trader_txword =''
hx_trader_yyb ='0'
hx_trader_version ='2.28'
trader_Ree = create_string_buffer(1024*1024) 


#相应的dll需要放置在src目录下 才可以加载
dll_path = "./JLAPI.dll"
user_file = "./user.json"

import tkinter
from tkinter import * 
from tkinter import messagebox
from tkinter import ttk

class TradeThread(threading.Thread):

    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        print( 'starting',self.name,'at:',time.ctime())
        self.res = self.func(*self.args)
        print(self.name,'finished at:',time.ctime())



class ShowInterface(QuickTrade):

    def select_btn_down(self):
        user_pos = self.all_client_list.curselection()
        if user_pos != None:
            selected_user = self.all_client_list.get(user_pos)
            self.all_client_list.delete(user_pos)
            self.selected_user_list.insert(END,selected_user)
            self.all_select_user_index.append(selected_user)

    def unselect_btn_down(self):
        user_pos = self.selected_user_list.curselection()
        if user_pos != None:
            selected_user = self.selected_user_list.get(user_pos)
            self.selected_user_list.delete(user_pos)
            self.all_client_list.insert(END,selected_user)
            self.all_select_user_index.remove(selected_user)

    def trade_btn_down(self):
        trade_stock = self.target_stock.get()
        trade_amount = int(self.target_amount.get())
        self.res_out_txt.delete(0.0,END)
#             print(index)
#             self.trade_target_stock(index,trade_stock,trade_amount)
#         index = self.all_select_user_index[0]
#         th = TradeThread(self.trade_target_stock,(index,trade_stock,trade_amount),self.trade_target_stock.__name__)
#         th.start()
        names = locals()
        for i in range(len(self.all_select_user_index)):
            index = self.all_select_user_index[i]
            names['th' + str(i)] = TradeThread(self.trade_target_stock,(index,trade_stock,trade_amount),self.trade_target_stock.__name__)
            names.get('th' + str(i)).start()
            

    
    def trade_target_stock(self,user_index,trade_stock,trade_amount):
        ip = self.all_user_info[user_index]['Ip']
        code = self.all_user_info[user_index]['Code']
        password = self.all_user_info[user_index]['Password']
        sh_code = self.all_user_info[user_index]['SHcode']
        sz_code = self.all_user_info[user_index]['SZcode']
        if len(trade_stock) < 6:
            trade_stock = '0'*(6- len(trade_stock)) + trade_stock
        tmp_trader = Trader(ip,
                        7708,
                        code,
                        password,
                        '',
                        '0',
                        dll_path,
                        None,
                        sh_code = sh_code,
                        sz_code = sz_code,
                        )
        out_res = tmp_trader.buy_stock(trade_stock,9.4,trade_amount)
        print(out_res)
        note = user_index + " 执行结果:" + out_res +"\n"
        print(note)
        self.trade_queue.put(note)
        self.notice(1)
        
    #按下查询股按键 
    def query_stock_btn_down(self):
        stock_info_top = Toplevel(self.root)
        stock_info_top.title("股票信息")
        stock_info_top.transient(self.root)
        stock_info_top.resizable(False,False)

    
    def flush_trade_res(self,msg):
        self.res_out_txt.insert(END,msg) 
    
    def notice(self,code):
        if code == 1:
            msg = self.trade_queue.get()
            self.flush_trade_res(msg)
            


if __name__ == "__main__":
    condition_lock = threading.Condition()
    trade_queue = Queue()
    uf = open(user_file,'r')
    all_user_info = json.load(uf)
    root = Tk()
    root.geometry("380x450")
    ShowInterface(root,all_user_info,trade_queue,condition_lock)
    root.mainloop()




#加载相应的所有用户信息
#     with open(user_file,'r') as uf:
#         user = json.load(uf)
#         print(user)





#     tmp_trader = Trader(hx_trader_ip,
#                         hx_trader_port,
#                         hx_trader_user,
#                         hx_trader_password,
#                         hx_trader_txword,
#                         hx_trader_yyb,
#                         dll_path,
#                         None,
#                         sh_code = 'A352792110',
#                         sz_code = '0190066160',
#                         )
#     
#     tmp_trader = Trader("113.105.77.163",
#                         7708,
#                         '50506031',
#                         '375228',
#                         '',
#                         '0',
#                         dll_path,
#                         '6.46',
#                         sh_code = 'A816730905',
#                         sz_code = '0159580158',
#                         )
#   
#     print(tmp_trader.buy_stock('000001',9.4,100))
#     print(tmp_trader.trader_Ree.value.decode('gbk','ignores'))
#     print(tmp_trader.trader_Ree.value.decode('gbk','ignore'))


    
