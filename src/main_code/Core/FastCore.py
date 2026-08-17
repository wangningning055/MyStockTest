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


stop_flag = False
process = None
update_thread = None


def get_base_dir():
    # PyInstaller 环境
    if getattr(sys, "frozen", False):
        print(f"软件环境1: {sys._MEIPASS}")
        return sys._MEIPASS
    # 开发环境
    print("开发环境1")
    return os.path.dirname(os.path.abspath(__file__))


def get_web_dir():
    # PyInstaller 环境
    if getattr(sys, "frozen", False):
        print(f"软件环境2: {os.path.join(BASE_DIR, 'src', 'main_code', 'Web')}")
        return os.path.join(BASE_DIR, "src", "main_code", "Web")
    # 开发环境
    print("开发环境2")
    return "src/main_code/Web"


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def open_browser_delay():
    import time
    time.sleep(1.5)

    if not is_port_open(8080):
        return

    #webbrowser.open("http://127.0.0.1:8080")


BASE_DIR = get_base_dir()

WEB_DIR = get_web_dir()
print(f"查找查找{BASE_DIR}         ||||          {WEB_DIR}")
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR),
    name="static"
)

app.include_router(action_router, prefix="/api")
register_ws(app)



process = None

def update_loop():
    global stop_flag, process

    while not stop_flag:
        try:
            if process:
                process.planner.UpdatePlane()
        except Exception as e:
            print("update_loop error:", e)

        time.sleep(1)

@app.on_event("startup")
def startup_event():
    global process, update_thread

    from src.main_code.Core import Main as main

    process = main.processor()
    process.Init()

    update_thread = threading.Thread(
        target=update_loop,
        daemon=True
    )
    update_thread.start()
    threading.Thread(target=open_browser_delay, daemon=True).start()




# 提供首页
@app.get("/")
def root():
    index_path = os.path.join(WEB_DIR, "index.html")
    return FileResponse(index_path)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

#@app.on_event("startup")
#def open_browser():
#    port = 8888

#    # 如果端口已经被占用，说明不是第一次启动（是 reload）
#    if is_port_in_use(port):
#        return

#    webbrowser.open(f"http://127.0.0.1:{port}")