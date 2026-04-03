# ws_routes.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from enum import Enum
import json
import asyncio

from typing import TYPE_CHECKING
# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core import Main

clients: set[WebSocket] = set()
mainProcessor : "Main.processor"
class MessageType(str, Enum):
    Log = "log"#服务器发送上次更新日期
    Test = "test"#测试
    SC_IN_BUSY = "sc_in_busy"               # #服务器返回是否忙碌
    SC_IN_PROGRESS = "sc_in_progress"       # #服务器返回进度
    LAST_UPDATE_DATA = "last_update_data_time"#服务器发送上次更新日期

    LAST_UPDATE_INDUSTRY = "last_update_data_industry"#服务器发送行业更新
    LAST_UPDATE_GROW_VALUE = "last_update_grow_value"#服务器发送价值成长股列表


    CS_UPDATE_DATA = "cs_update_data"               #客户端请求拉取数据
    CS_Stop_UPDATE_DATA = "cs_stop_update_data"               #客户端请求停止拉取数据
    CS_PREHEAT_DATA = "cs_preheat_data"               #客户端请求预热数据

    #未实现
    CS_INDUSTRY_ROTATION = "cs_industry_rotation",  # 客户端请求行业轮动分析
    SC_INDUSTRY_ROTATION = "sc_industry_rotation",  # 服务器返回行业轮动分析结果
    CS_QUERY_STOCKS = 'CS_QUERY_STOCKS',             # 客户端请求股票查询
    SC_QUERY_STOCKS_RESPONSE = 'SC_QUERY_STOCKS_RESPONSE',# 服务器返回股票查询结果




    CS_SELECT_STOCKS = "cs_select_stocks"           #客户端请求执行股票筛选
    CS_BACK_TEST = "cs_back_test"                   #客户端请求执行回测
    CS_BACK_TEST_STOP = "cs_back_test_stop"                   #客户端请求停止回测









    CS_DIAGNOSE = "cs_diagnose"                     #客户端请求出仓判断


##发送消息
async def SendMessage(msg_type, content):
    print(f"发送消息：{msg_type}")
    data = json.dumps({"type": msg_type, "msg": content})


    dead_ws = []

    for ws in clients:
        try:
            await ws.send_text(data)
        except RuntimeError:
            # ws 已关闭
            print(f"发送失败1：{msg_type}")
            dead_ws.append(ws)
        except Exception as e:
            print(f"发送失败2：{msg_type}")
            dead_ws.append(ws)

    # 统一清理
    for ws in dead_ws:
        clients.remove(ws)


async def safe_send(*args):
    try:
        await SendMessage(*args)
    except Exception as e:
        print("发送消息失败:", e)


def SendMessage_A(*args):
    asyncio.get_running_loop().create_task(safe_send(*args))
    


## 广播函数
async def broadcast(message: str):

    data = json.dumps({"type": "log", "msg": message})
    dead = set()
    clients_copy = list(clients)

    for ws in clients_copy:
        try:
            #print(f"log测试：{message}")
            await ws.send_text(data)
        except Exception:
            dead.add(ws)

    for ws in dead:
        clients.discard(ws)





#async def broadcast(message: str):
#    print("广播消息：",json.dumps({"type": "ping", "msg": message}))
#    for client in clients:
#        await client.send_text(json.dumps({"type": "ping", "msg": message}))

def register_ws(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        clients.add(ws)
        await ws.accept()
        print("客户端已连接")
        SendLastUpdateTime()
        SendLastUpdateIndustry()
        try:
            while True:
                data = await ws.receive_text()
                #print("收到前端:", data)
                msg = json.loads(data)
                HandleMsg(msg)
        except WebSocketDisconnect:
            print("客户端断开连接")

#发送上次更新日期
def SendLastUpdateTime():
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_DATA, mainProcessor.recordHandler.GetRecentRequestDateJsonStr()))

def SendLastUpdateIndustry():

    #jsonStr = json.dumps(mainProcessor.recordDataCls.industry_list, ensure_ascii=False, indent=2)
    #asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_INDUSTRY,jsonStr))
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_INDUSTRY,mainProcessor.recordDataCls.industry_list))

def HandleMsg(msg):
    if(mainProcessor == None):
        print("主程序没有初始化完成")
        return
    if(mainProcessor.isInit == False):
        mainProcessor.BoardCast("主程序没有初始化完成")
        print("主程序没有初始化完成")
        return
    msgType = msg["type"]
    if(msgType == MessageType.Test):
        print("进行数据测试")
        mainProcessor.ExecuteTest()

    if(msgType == MessageType.CS_Stop_UPDATE_DATA):
        print("停止拉取或预热数据")
        mainProcessor.requestor.StopRequest()
        mainProcessor.StopTest()
        return
    
    elif(msgType == MessageType.CS_BACK_TEST_STOP):
        print("停止回测")
        mainProcessor.backTestHandle.StopBackTest()



    if(mainProcessor.isInHandle == True):
        mainProcessor.BoardCast("正在处理，等待处理完成")
        print("正在处理，等待处理完成")
        return


    print("处理消息，消息类型是：" + msg["type"])
    msgType = msg["type"]
    data = msg["payload"]

    if(msgType == MessageType.CS_UPDATE_DATA):
        mainProcessor.tuShareToken = data["token"]
        update_Type = data["type"]
        mainProcessor.requestor.StartRequest(update_Type)
        

    elif(msgType == MessageType.CS_SELECT_STOCKS):
        print("处理筛选的消息")
        mainProcessor.analysisHandle.RunGetStockListByCondition(data)


    elif(msgType == MessageType.CS_PREHEAT_DATA):
        print("进行数据预热")
        task = asyncio.get_running_loop().create_task(mainProcessor.calculationDataHandle.DataPreheating())


    #需要修改成行业轮动分析
    elif(msgType == MessageType.CS_INDUSTRY_UP_DATA):
        print("进行行业分析")
        mainProcessor.calculationDataHandle.AnalyzeIndustry()
        



    elif(msgType == MessageType.CS_BACK_TEST):
        print(f"执行回测, 收到的回测消息：{data}")
        task = asyncio.get_running_loop().create_task(mainProcessor.backTestHandle.CreateStockByJson(data))







    elif(msgType == MessageType.CS_DIAGNOSE):
        pass


    
    elif(msgType == MessageType.LAST_UPDATE_DATA):
        print("请求最近的更新日期")
        SendLastUpdateTime()





#后端处理查询请求
    #    def handle_cs_query_stocks(self, data):
    #'''处理股票查询请求'''
    #query_type = data.get('query_type')   # 'code' | 'letter' | 'keyword'
    #query_value = data.get('query_value')
    
    #if query_type == 'code':
    #    # 代码查询：查询单支股票
    #    stocks = db.query_stock_by_code(query_value)
    #elif query_type == 'letter':
    #    # 字母查询：根据多个字母查询
    #    # 如：SDZX = 首都在线
    #    stocks = db.query_stock_by_letters(query_value)
    #elif query_type == 'keyword':
    #    # 关键字查询：在公司介绍和业务范围中搜索
    #    stocks = db.query_stock_by_keyword(query_value)
    
    ## 构建响应
    #response = {
    #    'query_type': query_type,
    #    'query_value': query_value,
    #    'stocks': [
    #        {
    #            'code': stock.code,
    #            'name': stock.name,
    #            'market_cap': float(stock.market_cap),
    #            'change_3d': float(stock.change_3d),
    #            'change_5d': float(stock.change_5d),
    #            'change_10d': float(stock.change_10d),
    #            'change_20d': float(stock.change_20d),
    #            'change_40d': float(stock.change_40d),
    #            'change_60d': float(stock.change_60d),
    #            'change_120d': float(stock.change_120d),
    #            'change_240d': float(stock.change_240d),
    #            'company_type': stock.company_type,
    #            'company_name': stock.company_name,
    #            'main_products': stock.main_products,
    #            'business_scope': stock.business_scope,
    #            'company_description': stock.company_description
    #        }
    #        for stock in stocks
    #    ],
    #    'timestamp': datetime.now().isoformat()
    #}
    
    ## 发送响应
    #self.send_message(MessageType.SC_QUERY_STOCKS_RESPONSE, response)









    #选股数据结构

    """
============================================================
前后端数据结构契约文档
============================================================

1. 选股结果 (sc_select_stocks_result)
============================================================
"""

## 前端发送：
#CS_SELECT_STOCKS = {
#    "type": "cs_select_stocks",
#    "msg": {
#        "isExcludeST": True,
#        "isExcludeKC": True,
#        "isExcludeCY": True,
#        "isExclude_Value": False,
#        "isExclude_Grow": False,
#        "configs": [
#            # ... 因子配置树 ...
#        ],
#        "threshold": 0.3,
#        "timestamp": "2025-01-15T10:00:00",
#        "version": "1.0"
#    }
#}

## 后端返回：
#SC_SELECT_STOCKS_RESULT = {
#    "type": "sc_select_stocks_result",
#    "msg": {
#        "stocks": [
#            {
#                "code": "600000",            # str: 6位股票代码
#                "name": "浦发银行",           # str: 股票名称
#                "score": 85.30,              # float: 筛选综合得分
#                "industry": "银行",           # str: 所属行业
#                "market_cap": 150000000000,  # float: 流通市值(元)
#                "change_3d": 2.15,           # float: 3日涨跌幅(%)
#                "change_5d": 3.40,           # float: 5日涨跌幅(%)
#                "change_10d": -1.20,         # float: 10日涨跌幅(%)
#                "change_20d": 5.60,          # float: 20日涨跌幅(%)
#                "change_40d": 8.30,          # float: 40日涨跌幅(%)
#                "change_60d": 12.50,         # float: 60日涨跌幅(%)
#                "change_120d": -3.80,        # float: 120日涨跌幅(%)
#                "change_240d": 15.20,        # float: 240日涨跌幅(%)
#                "params": {                  # dict: 详细参数(可选,可在请求K线时返回)
#                    "groups": [
#                        {
#                            "name": "分组名称",  # str: 参数分组名
#                            "items": [
#                                {
#                                    "label": "参数名",      # str: 参数显示名
#                                    "value": 12.34,         # any: 参数值
#                                    "type": "number"        # str: text|number|percent|currency|market_cap
#                                }
#                            ]
#                        }
#                    ]
#                }
#            }
#        ],
#        "total": 120,                        # int: 总数量
#        "timestamp": "2025-01-15T10:30:00"   # str: 时间戳
#    }
#}

#"""
#2. K线数据请求 (cs_request_kline)
#============================================================
#"""

## 前端发送：
#CS_REQUEST_KLINE = {
#    "type": "cs_request_kline",
#    "msg": {
#        "code": "600000",                    # str: 股票代码
#        "days": 240,                         # int: 请求天数
#        "timestamp": "2025-01-15T10:31:00"
#    }
#}

## 后端返回（流式，多次发送）：
#SC_KLINE_CHUNK = {
#    "type": "sc_kline_chunk",
#    "msg": {
#        "code": "600000",                    # str: 股票代码
#        "chunk": [                           # list: 本次发送的K线数据块
#            {
#                "date": "2024-06-15",        # str: 日期 YYYY-MM-DD
#                "open": 8.56,                # float: 开盘价
#                "close": 8.72,               # float: 收盘价
#                "high": 8.85,                # float: 最高价
#                "low": 8.45,                 # float: 最低价
#                "volume": 123456             # float: 成交量
#            }
#        ],
#        "progress": 0.5,                     # float: 进度 0~1
#        "is_last": False,                    # bool: 是否最后一块
#        "total": 240                         # int: 总K线数
#    }
#}

## 后端返回（一次性，单次发送）：
#SC_KLINE_DATA = {
#    "type": "sc_kline_data",
#    "msg": {
#        "code": "600000",
#        "kline": [
#            {
#                "date": "2024-06-15",
#                "open": 8.56,
#                "close": 8.72,
#                "high": 8.85,
#                "low": 8.45,
#                "volume": 123456
#            }
#            # ... 所有K线数据
#        ]
#    }
#}