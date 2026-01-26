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
from src.main_code.Core.Message import MessageHandle
import src.main_code.Core.Const as const_proj
from fastapi.responses import FileResponse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class processor:
    def Init(self):
        print("开始进行初始化")
        plane = PlanStruct.PlaneClass()
        self.planner = self.InitPlanner()
        self.fileProcessor = self.InitFile()
        self.dbHandler = self.InitDB()
        self.requestor = self.InitRequest()
        self.messageHandler = self.InitMessageHandler()
        plane.InitPlane(self.planeFunc, PlanStruct.PlanEnum.Daily, "19:00:00")

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
        instance.Init()
        return instance
    
    #初始化消息收发
    def InitMessageHandler(self):
        instance = MessageHandle.MessageHandlerClass()
        return instance

    def RequestData(self):
        #获取当天的日期
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
            print("是最新数据，无需拉取")
        else:
            print(f"拉取数据区间为：{lastDayStr}  ----  {today_str}")
            #self.requestor.RequestBasic_ByCSV()

            #self.requestor.RequestBasic()
            self.requestor.RequestAdjust()
            self.requestor.RequestDaily(lastDayStr, today_str)

        with open(const_proj.Request_Data_rec_FileName, "w", encoding="utf-8") as f:
            f.write(today_str)
        print("基本数据和日线数据拉取流程完成，数据已全部写入数据库")




