# ws_routes.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import asyncio
clients = set()


# 广播函数
async def broadcast(message: str):
    print("发送消息：",json.dumps({"type": "ping", "msg": message}))
    for client in clients:
        await client.send_text(json.dumps({"type": "ping", "msg": message}))

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
                if msg["type"] == "ping":
                    print("接受到前端消息：", msg["msg"])
                    await broadcast("你好前端")
        except WebSocketDisconnect:
            print("客户端断开连接")





