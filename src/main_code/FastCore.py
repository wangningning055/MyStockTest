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
import socket
import webbrowser

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/main_code/Web"), name="static")

app.include_router(action_router, prefix="/api")
register_ws(app)



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




# 提供首页
@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), const_proj.IndexHtmlPath))


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

@app.on_event("startup")
def open_browser():
    port = 8000

    # 如果端口已经被占用，说明不是第一次启动（是 reload）
    if is_port_in_use(port):
        return

    webbrowser.open(f"http://127.0.0.1:{port}")