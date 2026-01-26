from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class MessageHandlerClass:
    def __init__(self):
        self.messages = []  # 存储消息队列

    def send_message(self, msg: str):
        self.messages.append(msg)

    def get_messages(self):
        msgs = self.messages.copy()
        self.messages.clear()  # 取完就清空
        return msgs
    
