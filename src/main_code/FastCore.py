import sys
import os
from fastapi import FastAPI, WebSocket,WebSocketDisconnect
from pydantic import BaseModel
import pandas as pd
import time
import datetime
import threading
from src.main_code.Core import Main as main
stop_flag = False
from fastapi.responses import FileResponse
import src.main_code.Core.Const as const_proj
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
import asyncio
from src.main_code.Core.Message.MessageHandle import router as action_router
from src.main_code.Core.Message.WebSocketHandle import register_ws
app = FastAPI()
app.mount("/static", StaticFiles(directory="src/main_code/Web"), name="static")
#app.mount(
#    "/web",
#    StaticFiles(directory="src/main_code/Web"),
#    name="web"
#)
app.include_router(action_router, prefix="/api")
register_ws(app)

#@app.websocket("/ws")
#async def websocket_endpoint(ws: WebSocket):
#    await ws.accept()
#    print("客户端已连接")

#    try:
#        while True:
#            # 接收前端消息
#            data = await ws.receive_text()
#            print("收到前端:", data)

#            # 回传消息
#            await ws.send_text(f"后端已收到：{data}")

#    except WebSocketDisconnect:
#        print("客户端断开连接")


process = None

def update_loop():
    global stop_flag, process
    while not stop_flag:
        process.planner.UpdatePlane()
        time.sleep(1)

@app.on_event("startup")

def startup_event():
    global process
    process = main.processor()  # 延迟创建
    process.Init()

    # 后台线程循环
    t = threading.Thread(target=update_loop, daemon=True)
    t.start()



## 提供接口来控制停止
#@app.post("/stop")
#def stop():
#    global stop_flag
#    stop_flag = True
#    return {"msg": "程序已设置停止"}





#class actData(BaseModel):
#    message:str

## 服务器接受数据
#@app.post("/To_Server")
#async def act(data: actData):
#    print(f"接受到了数据  {data.message}")
#    return {"response": "执行动作aaaaaa"}

##服务器发送数据
#@app.get("/To_Web")
#def get_messages():
#    if process is None: return ""
#async def to_frontend():
#    return {
#        "code": "000001.SZ",
#        "price": 12.34
#    }


#@app.post("/send")
#def send(msg: str):
#    if process is None: return ""
#    [process.messageHandler].send_message(msg)
#    return {"msg": f"消息已发送: {msg}"}



# 提供首页
@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), const_proj.IndexHtmlPath))