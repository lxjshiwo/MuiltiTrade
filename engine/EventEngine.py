#encoding: utf-8
'''
Created on 2018年10月1日

@author: Administrator
'''
from queue import Queue
from threading import Thread
from _collections import defaultdict
from _queue import Empty
from time import sleep

from engine.EventType import *

class EventEngine(object):
    #事件引擎
    #通过事件引擎进行相应的数据交换操作
    
    def __init__(self):
        """初始化相应的事件引擎"""
        self.__queue = Queue()
        self.__active = False
        #事件处理线程
        self.__thread = Thread(target = self.__run)
        #计时器
        self.__timer = Thread(target=self.__runTimer)
        self.__timerActive = False
        self.__timerSleep = 1
        
        #保存相应的事件调用关系
        self.__handlers = defaultdict(list)
        
        #列表保存通用回调函数(所有事件均调用)
        self.__generalHandlers = []
    #-------------------------------------------------------------    
    def __run(self):
        """运行"""
        while self.__active == True:
            try:
                event = self.__queue.get(block = True, timeout = 1)
                self.__process(event)
            except Empty:
                pass
    #-------------------------------------------------------------    
    def __process(self,event):
        """处理函数"""
        if event.type_ in self.__handlers:
            #若存在则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]
            
            
    #-------------------------------------------------------------    
    def __runTimer(self):
        while self.__timerActive:
            #创建计时器事件
            event = Event(type_ = EVENT_TIMER)
            
            #向队列中存入计时器
            self.put(event)
            
            #等待
            sleep(self.__timerSleep)
    #-------------------------------------------------------------    
    def start(self,timer=True):
        """
        启动
        """
        self.__active = True
        
        self.__thread.start()
        
        #启动计时器，计时器事件间隔默认设定位1秒
        if timer:
            self.__timerActive = True
            self.__timer.start()
        
    
    #-------------------------------------------------------------    
    def stop(self):
        """
        停止
        """
        self.__active = False
        
        
        #停止计时器
        self.__timerActive = False
        self.__timer.join()
        
        #等待事件处理线程退出
        self.__thread.join()

    #-------------------------------------------------------------    
    def register(self,type_,handler):
        """注册事件处理函数监听"""
        handlerList = self.__handlers[type_]
        
        #若注册的处理函数不存在则增加
        if handler not in handlerList:
            handlerList.append(handler)

            
    
    #-------------------------------------------------------------    
    def unregister(self,type_,handler):
        handlerList = self.__handlers[type_]
        
        if handler in handlerList:
            del self.__handlers[type_]
    
    
    #-------------------------------------------------------------    
    def put(self,event):
        self.__queue.put(event)
        
    #-------------------------------------------------------------    
    def registerGeneralHandler(self,handler):

        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)
        
        
    #-------------------------------------------------------------    
    def unregisterGeneralHandler(self,handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)
        

class Event:    
    """事件对象"""
    #-------------------------------------------------------------    
    def __init__(self,type_ = None):
        self.type_ = type_  #事件类型
        self.dict_ = {}     #字典用于保存具体的事件数据
    

    
    
    
    
