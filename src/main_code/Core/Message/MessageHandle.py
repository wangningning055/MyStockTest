from pydantic import BaseModel
from fastapi import APIRouter
from typing import Optional, Dict, Any
from src.main_code.Core import Const as const_csproj
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect



router = APIRouter()
print("🔥 Socket初始化")
class ActionMessage(BaseModel):
    type: str              # 动作类型
    #payload: Optional[Dict[str, Any]] = None
@router.post("/action")
async def act(data: ActionMessage):
    print(f"接受到了数据 {data.type}")
    return {"response": "执行动作aaaaaa"}

