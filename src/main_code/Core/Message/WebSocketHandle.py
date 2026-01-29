# ws_routes.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from enum import Enum
import json
import asyncio
clients: set[WebSocket] = set()
mainProcessor = None

class MessageType(str, Enum):
    CS_UPDATE_DATA = "cs_update_data"               #客户端请求拉取数据
    CS_SELECT_STOCKS = "cs_select_stocks"           #客户端请求执行股票筛选
    CS_BACK_TEST = "cs_back_test"                   #客户端请求执行回测
    CS_DIAGNOSE = "cs_diagnose"                     #客户端请求出仓判断
    CS_SEND_LAST_UPDATE_DATA = "sc_last_update_data"#服务器发送上次更新日期
    Log = "log"#服务器发送上次更新日期
def HandleMsg(msg):
    if(mainProcessor == None):
        print("主程序没有初始化完成")
        return
    if(mainProcessor.isInBase or mainProcessor.isInFactor or mainProcessor.isInDaily ):
        mainProcessor.BoardCast("正在拉取，请勿操作")
        return
    print("处理消息，消息类型是：" + msg["type"])
    msgType = msg["type"]
    if(msgType == MessageType.CS_UPDATE_DATA):
        mainProcessor.RequestData()
    elif(msgType == MessageType.CS_SELECT_STOCKS):
        pass
    elif(msgType == MessageType.CS_BACK_TEST):
        pass
    elif(msgType == MessageType.CS_DIAGNOSE):
        pass
    elif(msgType == MessageType.CS_SEND_LAST_UPDATE_DATA):
        pass

    


## 广播函数
async def broadcast(message: str):
    data = json.dumps({"type": "log", "msg": message})
    dead = set()

    for ws in clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)

    for ws in dead:
        clients.remove(ws)


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
        try:
            while True:
                data = await ws.receive_text()
                print("收到前端:", data)
                msg = json.loads(data)
                HandleMsg(msg)
        except WebSocketDisconnect:
            print("客户端断开连接")





