#encoding: utf-8
'''
Created on 2018年9月30日

@author: lxj
'''
from ctypes import windll, create_string_buffer, memset, c_float
from queue import Queue
from multiprocessing.dummy import Pool
from _ast import Try
from _queue import Empty
import ctypes

#封装相应的dll函数接口 
class BaseApi(object):
    
    BASE_DIR = './'
    
    #异步模式与同步模式
    ASYNC_MODE = 'async'
    SYNC_MODE = 'sync'

    #--------------------------------------------------------------
    def __init__(self):
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
            self.dll_path = self.BASE_DIR + "JLAPI.dll"
            self.dll = windll.LoadLibrary(self.dll_path)
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
#             dll = windll.LoadLibrary(self.dll_path)
            clientId = self.dll.JL_Login(bytes(tradeIp, 'ascii'),
                                         port,
                                         bytes(version, 'ascii'), 
                                         bytes(usrName, 'ascii'),
                                         bytes(psWord, 'ascii'),
                                         bytes(txWord, 'ascii'),
                                         bytes(yyb, 'ascii'))
            params['clientId'] = clientId
            data['status'] = 'ok'
            data['data'] = (usrName,params)
            return True,data
        except Exception as e:
            data['status'] = 'false'
            data['data'] = 'error login'
            return False,data
    #--------------------------------------------------------------
    def getLogin(self,ip,version,username,password,txword,yyb,sz,sh):
        """用户登录"""
        params = {
                    'ip':ip,
                    'version':version,
                    'username':username,
                    'password':password,
                    'txword':' ',
                    'yyb':yyb,
                    'sz':sz,
                    'sh':sh,
                    }
        func = self.login
        callback = self.onGetLogin
        return self.addReq(params, func, callback)

    #--------------------------------------------------------------
    def onGetLogin(self,data,reqid):
        """用户重载"""
        pass

    
    #--------------------------------------------------------------
    def queryData(self):
        pass
    
    #--------------------------------------------------------------
    def cancelOrder(self,params):
        data = {}
        userName = params['username']
        bookCode = params['bookcode']
        exchangeType = params['exchangetype']
        clientId = params['clientid']
        try:
            output = create_string_buffer(1024*1024)
            memset(ctypes.byref(output),0x0,1024*1024)
            self.dll.JL_CancelOrder(clientId,
                                    bytes(userName,'ascii'),
                                    bytes(bookCode,'ascii'),
                                    exchangeType,
                                    output
                                    )
            output = output.value.decode('gbk')
            if output.__eq__('ok'):
                data['status'] = 'ok'
                data['data'] = (userName,bookCode,1)
                return True,data
            else:
                data['status'] = 'ok'
                data['data'] = (userName,bookCode,0)
            return True,data
        except Exception as e:
            data['status'] = 'false'
            data['data'] = 'error cancel'
            return False,data
    #--------------------------------------------------------------
    def getCancelOrder(self,username,bookcode,exchangetype,clientId):

        params = {
                   'username' :username,
                   'bookcode':bookcode,
                   'exchangetype':exchangetype,
                   'clientid':clientId,
                   }

        func = self.cancelOrder
        callback = self.onCancelOrder
        return self.addReq(params, func, callback)
    
    #--------------------------------------------------------------
    def onCancelOrder(self,data,reqid):
        pass
    #--------------------------------------------------------------
    #发送相应的下单命令
    #stock_code 交易股票代号
    #stock_price 交易股票价格
    #stock_amount 交易股票数量
    #trade_side 交易方向
    #holder_code 用户股东账号
    def sendOrder(self,params):
        #输出返回结果
        data = {}
        #获取相应的参数
        username = params['username']
        holderCode = params['holdercode']
        stockCode = params['stockcode']
        stockPrice = params['stockprice']
        stockAmount = params['stockamount']
        stockSide = params['stockside']
        clientId = params['clientid']
        #相应输出内容
        output = create_string_buffer(1024*1024)
        memset(ctypes.byref(output),0x0,1024*1024)
        try:
            self.dll.JL_SendOrder(clientId,
                                  0,
                                  bytes(username,'ascii'),
                                  bytes(holderCode,'ascii'),
                                  bytes(stockCode,'ascii'),
                                  stockAmount,
                                  c_float(stockPrice),
                                  output
                                  )
            output = output.value.decode('gbk')
            data['status'] = 'ok'
            data['data'] = (username,output,stockCode,clientId)
            return True,data
        except Exception as e:
            data['status'] = 'false'
            data['data'] = 'error login'
 
        return output
    #--------------------------------------------------------------
    def getSendOrder(self,username,holderCode,stockCode,stockPrice,stockAmount,stockSide,clientId):

        params = {
                   'username' :username,
                   'holdercode':holderCode,
                   'stockcode':stockCode,
                   'stockprice':stockPrice,
                   'stockamount':stockAmount,
                   'stockside':stockSide,
                   'clientid':clientId
                   }

        func = self.sendOrder
        #onSendOrder用户实现
        callback = self.onSendOrder
        return self.addReq(params, func, callback)
    #--------------------------------------------------------------
    def onSendOrder(self,data,reqid):
        pass
        
if __name__ == "__main__":

    tradeApi = BaseApi()
    tradeApi.init()
    clientId = tradeApi.dll.JL_Login(bytes('113.105.77.163', 'ascii'),
                                         7708,
                                         bytes('2.28', 'ascii'), 
                                         bytes('50506031', 'ascii'),
                                         bytes('375228', 'ascii'),
                                         bytes('', 'ascii'),
                                         bytes('0', 'ascii'))
    ree = create_string_buffer(1024*1024)
    memset(ctypes.byref(ree),0x0,1024*1024)
#     status = tradeApi.dll.JL_SendOrder(clientId,
#                                        0,
#                                        bytes('50506031', 'ascii'),
#                                        bytes('','ascii'),
#                                        bytes('000001', 'ascii'),
#                                        100,
#                                        c_float(10),
#                                        ree
#                                        )
#     status = tradeApi.dll.JL_QueryData(clientId,bytes('50506031','ascii'),104,ree)
    status = tradeApi.dll.JL_CancelOrder(clientId,
                                         bytes('50506031','ascii'),
                                         bytes('86','ascii'),
                                         1,
                                         ree
                                         )
    print(status)
    print(status,ree.value.decode('gbk'))


#     print(clientId)


