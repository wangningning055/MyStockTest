import sys
import os
import pandas as pd
import traceback
import time
import psutil
import datetime
import threading
from fastapi import FastAPI
from src.main_code.Core.Plan import Planner,PlanStruct
from src.main_code.Core.FileProcess import FileProcessor
from src.main_code.Core.Request import Requestor
from src.main_code.Core.DB import DBHandler
from src.main_code.Core.Calculate import CalculationDataHandle
from src.main_code.Core.Analysis import AnalysisHandle
from src.main_code.Core.Record import RecordHandler
from src.main_code.Core.BackTest import BackTestHandler
import src.main_code.Core.Const as const_proj
from src.main_code.Core.Test import Test
from fastapi.responses import FileResponse
import src.main_code.Core.Message.WebSocketHandle as ws
import asyncio
from src.main_code.Core.DataStruct.Base import RecordDataStruct
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import tracemalloc
class processor:
    lastDayStr = const_proj.first_Data
    tuShareToken = 0000000
    dbHandler : DBHandler.DBHandlerClass
    isInHandle : False
    recordDataCls : RecordDataStruct.TotalRecordDataCls
    def BoardCast(self, message: str):
        asyncio.get_running_loop().create_task(ws.broadcast(message))


    def Init(self):
        print("开始进行初始化")
        now = datetime.datetime.now()
        todayStr = now.strftime("%Y%m%d")
        print(f"今天是：{todayStr}")
        self.planner = self.InitPlanner()
        #plane.InitPlane(self.planeFunc, PlanStruct.PlanEnum.Daily, "19:00:00")
        #self.planner.AddPlane(plane)

        self.fileProcessor = self.InitFile()
        self.recordHandler = self.InitRecorderHandle()
        self.lastDayStr = self.recordDataCls.daily_list_last_data


        self.websocketHandler = ws

        self.dbHandler :DBHandler.DBHandlerClass = self.InitDB()
        self.requestor = self.InitRequest()
        self.calculationDataHandle : CalculationDataHandle.BaseClass = self.InitCalculationDataHandle()
        self.analysisHandle = self.InitAnalysisHandle()
        self.backTestHandle = self.InitBackTestHandle()
        ws.mainProcessor = self
        self.todayStockDate = self.calculationDataHandle.GetToday()
        self.isInit = True
        self.isInHandle = False
        print(f"初始化完毕, 最近的有效股票数据日期是：{self.todayStockDate}")


        #self.Temp_ImportValue()
        #self.Temp_ExportValue()

    def Temp_ExportValue(self):
        listValue = self.dbHandler.GetAllValueData()
        print(f"长度是：{len(listValue)}")
        print(listValue[0])
        df = pd.DataFrame(listValue)
        self.fileProcessor.SaveCSV(df, "Value", FileProcessor.FileEnum.Basic)
        print("读出完成")

    def Temp_ImportValue(self):
        path4 = self.fileProcessor.GetCSVPath("Value", FileProcessor.FileEnum.Basic)
        df = pd.read_csv(path4)
        classList = self.requestor.api.Df_To_ValueClass_Temp(df)
        self.dbHandler.WriteTableNoWait(classList, DBHandler.TableEnum.Value)
        print("写入完成")


    def SetIsInHandle(self, isIn):
        if self.isInHandle == isIn:
            return
        self.isInHandle = isIn

        mem = psutil.virtual_memory()
        total_memory = mem.total
        tracemalloc.start()


        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)
        mem_info = process.memory_info()
        current, peak = tracemalloc.get_traced_memory()
        #rss_memory = mem_info.rss / (1024 * 1024)
        rss_memory = current / (1024 * 1024)
        available_memory = mem.available /(1024*1024*1024)


        #当前已使用内存
        rss_memory = round(rss_memory, 1)
        #当前可使用内存：
        available_memory = round(available_memory, 1)
        
        if isIn == True:
            res = (1, rss_memory, available_memory)
            self.websocketHandler.SendMessage_A(ws.MessageType.SC_IN_BUSY, res)
        if isIn == False:
            self.requestor.StopRequest()
            res = (0, rss_memory, available_memory)
            self.websocketHandler.SendMessage_A(ws.MessageType.SC_IN_BUSY, res)



    def planeFunc(self):
        self.RequestData()

    #初始化计划任务
    def InitPlanner(self):
        instance = Planner.PlannerClass()
        instance.Init()
        self.BoardCast("计划任务模块初始化完毕")
        return instance
    
    #初始化文件管理
    def InitFile(self):
        instance = FileProcessor.FileProcessorClass()
        instance.Init()
        return instance
    
    #初始化拉取模块
    def InitRequest(self):
        print("拉取模块初始化，尝试登录baoStock......")
        instance = Requestor.RequestorClass()
        instance.Init(self)
        print("拉取模块初始化完毕")
        return instance

    #初始化数据库模块
    def InitDB(self) ->DBHandler.DBHandlerClass :
        instance = DBHandler.DBHandlerClass()
        instance.Init(self)
        print("数据库模块初始化完毕")
        return instance
    #初始化数据处理模块
    def InitCalculationDataHandle(self):
        instance = CalculationDataHandle.BaseClass()
        instance.Init(self)
        print("计算模块初始化完毕")
        return instance
    
    #初始化数据分析模块
    def InitAnalysisHandle(self):
        instance = AnalysisHandle.BaseClass()
        instance.Init(self)
        print("分析模块初始化完毕")
        return instance
    
    def InitRecorderHandle(self):
        instance = RecordHandler.BaseClass()
        instance.Init(self)
        print("记录模块初始化完毕")
        return instance

    def InitBackTestHandle(self):
        instance = BackTestHandler.BaseClass()
        instance.Init(self)
        return instance
    
    def ExecuteTest(self):
        task = asyncio.get_running_loop().create_task(Test.TestCalculate(self.calculationDataHandle))

    def StopTest(self):
        Test.Stop()




    def task_finished_callback(self,task):
        #print("基础数据拉取 执行完毕")
        #self.BoardCast("基础数据拉取 执行完毕")

        if(not self.isInHandle):
            self.BoardCast("流程结束")
            print("流程结束")
            self.recordHandler.WriteRecordData()

        else:
            print("流程异常结束")
            self.BoardCast(f"流程异常结束")
            self.SetIsInHandle(False)
            
        try:
            result = task.result()  # 捕获返回值或异常
            print(f"任务返回值:{result}")
            self.BoardCast(f"任务返回值:{result}")
        except asyncio.CancelledError:
        # 专门捕获取消异常（任务被主动停止）
            print("任务取消")

        except Exception as e:
            print("任务异常:", e)
            full_trace = traceback.format_exc()
            print("任务异常:", full_trace)
