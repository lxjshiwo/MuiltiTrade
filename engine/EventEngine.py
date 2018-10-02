#encoding: utf-8
'''
Created on 2018年10月1日

@author: Administrator
'''
from multiprocessing.queues import Queue
from threading import Thread
from _collections import defaultdict
from _queue import Empty

class EnventEngine():
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
            
            

    