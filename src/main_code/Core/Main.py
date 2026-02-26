import sys
import os
import pandas as pd
import traceback
import time
import datetime
import threading
from fastapi import FastAPI
from src.main_code.Core.Plan import Planner,PlanStruct
from src.main_code.Core.FileProcess import FileProcessor
from src.main_code.Core.Request import Requestor
from src.main_code.Core.DB import DBHandler
from src.main_code.Core.Select import CalculationDataHandle
import src.main_code.Core.Const as const_proj
from fastapi.responses import FileResponse
import src.main_code.Core.Message.WebSocketHandle as ws
import asyncio
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
class processor:
    isInit = False
    isInBase = False
    isInFactor = False
    isInDaily = False
    lastDayStr = const_proj.first_Data
    tuShareToken = 0000000
    dbHandler : DBHandler.DBHandlerClass
    def BoardCast(self, message: str):
        asyncio.get_running_loop().create_task(ws.broadcast(message))


    def Init(self):
        print("开始进行初始化")
        today_str = datetime.date.today().strftime("%Y%m%d")
        print(f"今天的日期是：{today_str}")
        self.InitLastUpdateTime()
        plane = PlanStruct.PlaneClass()
        self.planner = self.InitPlanner()
        self.fileProcessor = self.InitFile()
        self.dbHandler :DBHandler.DBHandlerClass = self.InitDB()
        self.calculationDataHandle = self.InitCalculationDataHandle()
        self.requestor = self.InitRequest()
        plane.InitPlane(self.planeFunc, PlanStruct.PlanEnum.Daily, "19:00:00")
        ws.mainProcessor = self
        #self.planner.AddPlane(plane)
        #self.RequestData()
        print("初始化完毕")
        self.isInit = True

    def InitLastUpdateTime(self):
        if not os.path.exists(const_proj.Request_Data_rec_FileName):
            self.lastDayStr = const_proj.first_Data
        else:
            with open(const_proj.Request_Data_rec_FileName, "r", encoding="utf-8") as f:
                self.lastDayStr = f.read().strip()
        print("日期读取完毕")

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
    def InitDB(self) ->DBHandler.DBHandlerClass :
        instance = DBHandler.DBHandlerClass()
        instance.Init(self)
        return instance
    #初始化数据处理模块
    def InitCalculationDataHandle(self):
        instance = CalculationDataHandle.BaseClass()
        instance.Init(self)
        return instance

    async def RequestData(self):
        try:
            #获取当天的日期
            today_str = datetime.date.today().strftime("%Y%m%d")
            lastDayStr = const_proj.first_Data
            if not os.path.exists(const_proj.Request_Data_rec_FileName):
                lastDayStr = const_proj.first_Data
            else:
                with open(const_proj.Request_Data_rec_FileName, "r", encoding="utf-8") as f:
                    lastDayStr = f.read().strip()
            lastDayStr = "20251201"
            if lastDayStr == today_str:
                self.BoardCast("是最新数据，无需拉取,开始读入数据")
                #await self.calculationDataHandle.ReadDBDataInMemory()
            else:
                self.isInit = False
                self.BoardCast("开始进行数据拉取")
                self.BoardCast(f"拉取数据区间为：{lastDayStr}  ----  {today_str}")

                self.isInDaily = True
                self.isInBase = True
                self.isInFactor = True
                
                #await self.requestor.RequestBasic_ByCSV()


                #await self.requestor.RequestBasic()
                #self.isInBase = False

                #await self.requestor.RequestAdjust()
                #self.isInFactor = False

                #await self.requestor.RequestDaily(lastDayStr, today_str)
                #self.isInDaily = False


                await self.requestor.RequestValue()

                self.isInit = True

        except Exception as e:
            self.isInit = True
            print(f"拉取失败失败: {e}")
            full_trace = traceback.format_exc()
            print(f"拉取失败失败: {full_trace}")
            self.BoardCast(f"拉取失败失败: {e}")



    def pullOver(self):
        today_str = datetime.date.today().strftime("%Y%m%d")
        self.lastDayStr = today_str
        with open(const_proj.Request_Data_rec_FileName, "w", encoding="utf-8") as f:
            f.write(today_str)
        ws.SendLastUpdateTime()

    def task_finished_callback(self,task):
        #print("基础数据拉取 执行完毕")
        #self.BoardCast("基础数据拉取 执行完毕")
        print("股票信息拉取流程结束")

        if(not (self.isInBase or self.isInDaily or self.isInFactor)):
            self.BoardCast("股票信息拉取流程结束")
            print("股票信息拉取流程结束")
            self.pullOver()
        else:
            print("股票信息拉取流程异常结束")
            self.BoardCast(f"股票信息拉取流程异常结束:{self.isInBase}{self.isInFactor}{self.isInDaily}")
            
        try:
            result = task.result()  # 捕获返回值或异常
        except Exception as e:
            print("任务异常:", e)
            full_trace = traceback.format_exc()
            print("任务异常:", full_trace)

    #def task_finished_callback_Factor(self,task):
    #    print("复权因子数据拉取执行完毕 ")
    #    self.BoardCast("复权因子数据拉取执行完毕 ")
    #    self.isInFactor = False
    #    if(not (self.isInBase or self.isInDaily or self.isInFactor)):
    #        self.BoardCast("股票信息已经拉取完毕")
    #        print("股票信息已经拉取完毕")
    #        self.pullOver()
    #    try:
    #        result = task.result()  # 捕获返回值或异常
    #    except Exception as e:
    #        print("任务异常:", e)



    #def task_finished_callback_Daily(self,task):
    #    print("日线数据拉取 执行完毕")
    #    self.BoardCast("日线数据拉取 执行完毕")
    #    self.isInDaily = False
    #    if(not (self.isInBase or self.isInDaily or self.isInFactor)):
    #        self.BoardCast("股票信息已经拉取完毕")
    #        print("股票信息已经拉取完毕")
    #        self.pullOver()
    #    try:
    #        result = task.result()  # 捕获返回值或异常
    #    except Exception as e:
    #        print("任务异常:", e)
