#encoding: utf-8
'''
Created on 2018年9月30日

@author: lxj
'''
from ctypes import windll
from queue import Queue
from multiprocessing.dummy import Pool
from _ast import Try
from _queue import Empty

#相应的交易api 封装相应的dll函数
class TradeApi(object):
    
    BASE_DIR = './'
    
    #异步模式与同步模式
    ASYNC_MODE = 'async'
    SYNC_MODE = 'sync'

    #--------------------------------------------------------------
    def __init__(self,):
        self.dll = None         #使用的dll
        self.mode = self.ASYNC_MODE #执行模式
        self.active = False         #API状态
        self.reqid = 0          #请求编号
        self.queue = Queue()    #请求队列
        self.pool = None        #线程池 
    
    #--------------------------------------------------------------
    def init(self,dllType=None,mode =None):
        #使用的dll 初始化加载相应的dll
        if not dllType:
            dll_path = self.BASE_DIR + "JLAPI.dll"
            self.dll = windll.LoadLibrary(dll_path)
        #外后回加载相应其他类型dll
        else:
            pass
        
        if mode:
            self.mode = mode
        
        return True

    #--------------------------------------------------------------
    def start(self,n= 10):
        self.active = True
        if self.mode == self.ASYNC_MODE:
            self.pool = Pool(n)
            self.pool.map_async(self.run,range(n)) 

    #--------------------------------------------------------------
    def close(self):
        self.active = False
        self.pool.close()
        self.pool.join()

    #--------------------------------------------------------------
    def run(self,n):
        """连续运行"""
        while self.active:
            try:
                req = self.queue.get(timeout=1)
                self.proccessReq(req)
            except Empty:
                pass
    #--------------------------------------------------------------
    def addReq(self,params,func,callback):
        """
                         加入队列相应任务
            params:参数
            func:执行函数
            callback:回调函数
        """
        if self.mode == self.ASYNC_MODE:
            self.reqid += 1
            req = (params,func,callback,self.reqid)
            self.queue.put(req)
        else:
            func(params)

    #--------------------------------------------------------------
    def proccessReq(self,req):
        """处理请求操作"""
        params,func,callback,reqid = req
        result,data = func(params)
        if result:
            if data['status'] == 'ok':
                callback(data['data'],reqid)
            else:
                msg = 'on error'
                self.onError(msg,reqid)
        else:
            self.onError(data,reqid)

    #--------------------------------------------------------------
    def onError(self,msg,reqid):
        """错误处理"""
        print(msg,reqid)

    #--------------------------------------------------------------
    def login(self,params):
        #返回格式
        data = {}
        #初始化相应登录参数
        tradeIp = params['ip']
        version = params['version']
        usrName = params['username']
        psWord = params['password']
        txWord = params['txword']
        yyb = params['yyb']
        port = 7708
        try:
        #返回相应的用户账号
            clientId = self.dll.JL_Login(bytes(tradeIp, 'ascii'),
                                         port,
                                         bytes(version, 'ascii'), 
                                         bytes(usrName, 'ascii'),
                                         bytes(psWord, 'ascii'),
                                         bytes(txWord, 'ascii'),
                                         bytes(yyb, 'ascii'))
            data['status'] = 'ok'
            data['data'] = {usrName:clientId}
            return True,data
        except Exception as e:
            data['status'] = 'false'
            data['data'] = 'error login'
            return False,data
    #--------------------------------------------------------------
    def getLogin(self,ip,version,username,password,txword,yyb):
        """用户登录"""
        params = {
                    'ip':ip,
                    'version':version,
                    'username':username,
                    'password':password,
                    'txword':' ',
                    'yyb':yyb
                    }
        func = self.login
        callback = self.onGetLogin
        return self.addReq(params, func, callback)

    #--------------------------------------------------------------
    def onGetLogin(self,data,reqid):
        return data

    
    #--------------------------------------------------------------
    def queryData(self):
        pass
    
    #--------------------------------------------------------------
    def cancelOrder(self):
        pass
    
    #--------------------------------------------------------------
    def sendOrder(self):
        pass

if __name__ == "__main__":

    tradeApi = TradeApi()
    tradeApi.init()
    clientId = tradeApi.dll.JL_Login(bytes('113.105.77.163', 'ascii'),
                                         7708,
                                         bytes('2.28', 'ascii'), 
                                         bytes('50506031', 'ascii'),
                                         bytes('375228', 'ascii'),
                                         bytes('', 'ascii'),
                                         bytes('0', 'ascii'))
    print(clientId)


