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
    CS_INDUSTRY_UP_DATA = "cs_industry_up_data"               #客户端请求分析行业上涨

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