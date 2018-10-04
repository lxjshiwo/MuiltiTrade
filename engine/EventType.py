#encoding: utf8

# 系统相关
EVENT_TIMER = 'eTimer'                  # 计时器事件，每隔1秒发送一次
EVENT_LOG = 'eLog'                      # 日志事件，全局通用

# Gateway相关
EVENT_TICK = 'eTick.'                   # TICK行情事件，可后接具体的vtSymbol
EVENT_TRADE = 'eTrade.'                 # 成交回报事件
EVENT_ORDER = 'eOrder.'                 # 报单回报事件
EVENT_POSITION = 'ePosition.'           # 持仓回报事件
EVENT_ACCOUNT = 'eAccount.'             # 账户回报事件
EVENT_CONTRACT = 'eContract.'           # 合约基础信息回报事件
EVENT_ERROR = 'eError.'                 # 错误回报事件

#相应的调试信息
EVENT_LOGIN = 'eLogin'                  #用于轮询登录
EVENT_TRADE_PLAN ='eTradePlan'          #用于执行单个用户批量交易
EVENT_TRADE_CANCEL = 'eCancelPlan'      #用于执行单个用户的批量撤销