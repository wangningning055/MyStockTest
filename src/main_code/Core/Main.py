import sys
import os
import pandas as pd
import time
import datetime
import threading
from fastapi import FastAPI
from src.main_code.Core.Plan import Planner,PlanStruct
from src.main_code.Core.FileProcess import FileProcessor
from src.main_code.Core.Request import Requestor
from src.main_code.Core.DB import DBHandler
import src.main_code.Core.Const as const_proj
from fastapi.responses import FileResponse
import src.main_code.Core.Message.WebSocketHandle as ws
import asyncio
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class processor:
    isInBase = False
    isInFactor = False
    isInDaily = False
    def BoardCast(self, message: str):
        asyncio.get_running_loop().create_task(ws.broadcast(message))


    def Init(self):
        print("开始进行初始化")
        plane = PlanStruct.PlaneClass()
        self.planner = self.InitPlanner()
        self.fileProcessor = self.InitFile()
        self.dbHandler = self.InitDB()
        self.requestor = self.InitRequest()
        plane.InitPlane(self.planeFunc, PlanStruct.PlanEnum.Daily, "19:00:00")
        ws.mainProcessor = self
        #self.planner.AddPlane(plane)
        #self.RequestData()


    def planeFunc(self):
        self.RequestData()

    #初始化计划任务
    def InitPlanner(self):
        instance = Planner.PlannerClass()
        instance.Init()

        return instance
    
    #初始化文件管理
    def InitFile(self):
        instance = FileProcessor.FileProcessorClass()
        instance.Init()
        return instance
    
    #初始化拉取模块
    def InitRequest(self):
        instance = Requestor.RequestorClass()
        instance.Init(self)
        return instance

    #初始化数据库模块
    def InitDB(self):
        instance = DBHandler.DBHandlerClass()
        instance.Init(self)
        return instance
    


    def RequestData(self):
        #获取当天的日期
        self.BoardCast("开始进行数据拉取")
        print("开始进行数据拉取")
        today_str = datetime.date.today().strftime("%Y%m%d")
        lastDayStr = const_proj.first_Data
        if not os.path.exists(const_proj.Request_Data_rec_FileName):
            lastDayStr = const_proj.first_Data
        else:
            with open(const_proj.Request_Data_rec_FileName, "r", encoding="utf-8") as f:
                lastDayStr = f.read().strip()

        #lastDayStr = first_Data
        if lastDayStr == today_str:
            self.BoardCast("是最新数据，无需拉取")
        else:
            self.BoardCast(f"拉取数据区间为：{lastDayStr}  ----  {today_str}")
            #self.isInDaily = True
            self.isInBase = True
            #self.isInFactor = True
            self.requestor.RequestBasic_ByCSV()

            #self.requestor.RequestBasic()
            #self.requestor.RequestAdjust()
            #self.requestor.RequestDaily(lastDayStr, today_str)

        with open(const_proj.Request_Data_rec_FileName, "w", encoding="utf-8") as f:
            f.write(today_str)



    def task_finished_callback_Basic(self,task):
        print("基础数据拉取 执行完毕")
        self.isInBase = False
        if(not (self.isInBase or self.isInDaily or self.isInFactor)):
            self.BoardCast("股票信息已经拉取完毕")
            print("股票信息已经拉取完毕")
        try:
            result = task.result()  # 捕获返回值或异常
        except Exception as e:
            print("任务异常:", e)

    def task_finished_callback_Factor(self,task):
        print("复权因子数据拉取执行完毕 ")
        self.isInFactor = False
        if(not (self.isInBase or self.isInDaily or self.isInFactor)):
            self.BoardCast("股票信息已经拉取完毕")
            print("股票信息已经拉取完毕")
        try:
            result = task.result()  # 捕获返回值或异常
        except Exception as e:
            print("任务异常:", e)



    def task_finished_callback_Daily(self,task):
        print("日线数据拉取 执行完毕")
        self.isInDaily = False
        if(not (self.isInBase or self.isInDaily or self.isInFactor)):
            self.BoardCast("股票信息已经拉取完毕")
            print("股票信息已经拉取完毕")
        try:
            result = task.result()  # 捕获返回值或异常
        except Exception as e:
            print("任务异常:", e)
