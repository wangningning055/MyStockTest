# ws_routes.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from enum import Enum
import json
import asyncio
import datetime
from starlette.websockets import WebSocketState
from typing import TYPE_CHECKING
# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core import Main

clients: set[WebSocket] = set()
mainProcessor : "Main.processor"
pending_messages = []

class MessageType(str, Enum):
    Log = "log"#服务器发送上次更新日期
    Test = "test"#测试
    SC_IN_BUSY = "sc_in_busy"               # #服务器返回是否忙碌
    SC_IN_PROGRESS = "sc_in_progress"       # #服务器返回进度
    LAST_UPDATE_DATA = "last_update_data_time"#服务器发送上次更新日期

    LAST_UPDATE_INDUSTRY = "last_update_data_industry"#服务器发送行业更新
    LAST_UPDATE_GROW_VALUE = "last_update_grow_value"#服务器发送价值成长股列表

    EXPORT_VALUE = "export_value"                  #//导入价值数据
    IMPORT_VALUE = "import_value"                  #//导出价值数据


    CS_UPDATE_DATA = "cs_update_data"               #客户端请求拉取数据
    CS_Stop_UPDATE_DATA = "cs_stop_update_data"               #客户端请求停止拉取数据
    CS_PREHEAT_DATA = "cs_preheat_data"               #客户端请求预热数据

    CS_INDUSTRY_ROTATION = "cs_industry_rotation",  # 客户端请求行业轮动分析
    SC_INDUSTRY_ROTATION = "sc_industry_rotation",  # 服务器返回行业轮动分析结果


    CS_QUERY_STOCKS = 'CS_QUERY_STOCKS',             # 客户端请求股票查询
    SC_QUERY_STOCKS_RESPONSE = 'SC_QUERY_STOCKS_RESPONSE',# 服务器返回股票查询结果


    CS_REQUEST_KLINE = 'cs_request_kline',      # 请求K线数据

    SC_KLINE_CHUNK = 'sc_kline_chunk',           # 流式K线数据块
    SC_KLINE_DATA = 'sc_kline_data',             # 一次性K线数据




    CS_SELECT_STOCKS = "cs_select_stocks"           #客户端请求执行股票筛选
    SC_SELECT_STOCKS = "sc_select_stocks",            # 客户端返回股票筛选



    CS_BACK_TEST = "cs_back_test"                   #客户端请求执行回测
    SC_BACK_TEST = "sc_back_test"                   #服务器返回回测
    CS_BACK_TEST_STOP = "cs_back_test_stop"                   #客户端请求停止回测



    CS_PATTERN_MATCH = "cs_pattern_match",                  #客户端请求模式匹配
    SC_PATTERN_MATCH = "sc_pattern_match",                  #服务器返回模式匹配
    CS_PATTERN_MATCH_STOP = 'cs_pattern_match_stop'

    #暂不实现
    CS_PATTERN_EXPORT_PARAMS = "cs_pattern_export_params",  #客户端请求参数分析
    SC_PATTERN_EXPORT_PARAMS = "sc_pattern_export_params"   #服务器返回参数分析






##发送消息
async def SendMessage(msg_type, content):
    if msg_type is not MessageType.SC_IN_PROGRESS and  msg_type is not MessageType.SC_IN_BUSY:
        print(f"发送消息：{msg_type}")
    data = json.dumps({"type": msg_type, "msg": content}, ensure_ascii=False, indent=2)

    dead_ws = []
    isSuccess = False

    for ws in clients:
        isSuccess = False
        try:
            if ws.client_state != WebSocketState.CONNECTED:
                print(f"发送失败1：{msg_type}")
                dead_ws.append(ws)
                continue
            try:
                await ws.send_text(data)
            except e:
                print(f"发送失败2：{msg_type}")
            isSuccess = True

        except RuntimeError:
            # ws 已关闭
            print(f"发送失败3：{msg_type}")
            dead_ws.append(ws)
        except Exception as e:
            print(f"发送失败4：{msg_type}")
            dead_ws.append(ws)

    if isSuccess == False:
        pending_messages.append(data)

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
        await ws.accept()
        clients.add(ws)
        print("客户端已连接")
        SendLastUpdateTime()
        SendLastUpdateIndustry()
        SendLastUpdateIndustryRotation()
        #在这里发送缓存的消息：
        for data in pending_messages:
            await ws.send_text(data)
        pending_messages.clear()


        try:
            while True:
                data = await ws.receive_text()
                #print("收到前端:", data)
                msg = json.loads(data)
                HandleMsg(msg)
        except WebSocketDisconnect:
            print("客户端断开连接")
        finally:
            clients.discard(ws)

#发送上次更新日期
def SendLastUpdateTime():
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_DATA, mainProcessor.recordHandler.GetRecentRequestDateJsonStr()))

#发送行业列表
def SendLastUpdateIndustry():
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_INDUSTRY,mainProcessor.recordDataCls.industry_list))
    

def SendLastUpdateIndustryRotation():
    print("发送行业轮动分析结果")
    asyncio.get_running_loop().create_task(safe_send(MessageType.SC_INDUSTRY_ROTATION,mainProcessor.recordDataCls.industry_Increase_Month_Dic))


    #for key, value in tempDic.items():
    #    print(f"行业：{key[0]}， 月份：{key[1]}， 出现次数：{value}")

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

    elif(msgType == MessageType.CS_PATTERN_MATCH_STOP):
        print("停止匹配")
        mainProcessor.patternMatchHandle.StopMatch()


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
    
    elif(msgType == MessageType.LAST_UPDATE_DATA):
        print("请求最近的更新日期")
        SendLastUpdateTime()

    elif(msgType == MessageType.EXPORT_VALUE):
        print("导出价值数据")
        mainProcessor.Temp_ExportValue()

    elif(msgType == MessageType.IMPORT_VALUE):
        print("导入价值数据")
        mainProcessor.Temp_ImportValue()

    elif(msgType == MessageType.CS_SELECT_STOCKS):
        print("处理选股消息")
        task = asyncio.get_running_loop().create_task(mainProcessor.analysisHandle.RunGetStockListByCondition(data))


    elif(msgType == MessageType.CS_PREHEAT_DATA):
        print(f"进行数据预热:{data}")
        targetData = data["data"]
        print(f"进行数据预热:{targetData}")
        mainProcessor.calculationDataHandle.SetDate(targetData)
        task = asyncio.get_running_loop().create_task(mainProcessor.calculationDataHandle.DataPreheating())


    #需要修改成行业轮动分析
    elif(msgType == MessageType.CS_INDUSTRY_ROTATION):
        print("进行行业分析")
        mainProcessor.calculationDataHandle.AnalyzeIndustry()
        



    elif(msgType == MessageType.CS_BACK_TEST):
        print(f"执行回测, 收到的回测消息：{data}")
        task = asyncio.get_running_loop().create_task(mainProcessor.backTestHandle.CreateStockByJson(data))



    elif(msgType == MessageType.CS_QUERY_STOCKS):
        mainProcessor.analysisHandle.SearchStock(data)
    
    elif(msgType == MessageType.CS_REQUEST_KLINE):
        mainProcessor.analysisHandle.HandleKLineResponse(data)


    elif(msgType == MessageType.CS_PATTERN_MATCH):
        task = asyncio.get_running_loop().create_task(mainProcessor.patternMatchHandle.StartMatch(data))
       

    
    elif(msgType == MessageType.CS_PATTERN_EXPORT_PARAMS):
        mainProcessor.patternMatchHandle.StartHandleResult(data)
    
    elif(msgType == MessageType.SC_PATTERN_EXPORT_PARAMS):
        mainProcessor.patternMatchHandle.SendHandleResult()



