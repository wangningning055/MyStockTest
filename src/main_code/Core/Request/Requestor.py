from src.main_code.Core.Request.API import RequestAPI
import src.main_code.Core.Const as const_proj
from src.main_code.Core.FileProcess import FileProcessor
from src.main_code.Core.DB import DBHandler
import time
import os
import pandas as pd
import asyncio
class RequestorClass:
    def Init(self, main):
        self.api = RequestAPI.RequestAPIClass()
        self.main = main
        self.api.init(main)

    def RequestBasic(self):
        self.main.BoardCast("处理基础数据")
        self.main.isInBase = True
        df_Basic = self.api.Request_Basic()
        df_Company_SZSE = self.api.Request_Company(const_proj.TradeNameSZSE)
        df_Company_SSE = self.api.Request_Company(const_proj.TradeNameSSE)
        df_Company_BSE = self.api.Request_Company(const_proj.TradeNameBSE)
        self.main.fileProcessor.SaveCSV(df_Basic, "Base", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_SZSE, "SZSE", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_SSE, "SSE", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_BSE, "BSE", FileProcessor.FileEnum.Basic)
        classList = self.api.Df_To_BasicClass(df_Basic, df_Company_SZSE, df_Company_SSE, df_Company_BSE)
        asyncio.get_running_loop().create_task(self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Basic))
        self.main.BoardCast("处理基础数据完成")

    def RequestBasic_ByCSV(self):
        self.main.isInBase = True
        self.main.BoardCast("处理基础数据")
        pathBase = self.main.fileProcessor.GetCSVPath("Base", FileProcessor.FileEnum.Basic)
        path1 = self.main.fileProcessor.GetCSVPath("SZSE", FileProcessor.FileEnum.Basic)
        path2 = self.main.fileProcessor.GetCSVPath("SSE", FileProcessor.FileEnum.Basic)
        path3 = self.main.fileProcessor.GetCSVPath("BSE", FileProcessor.FileEnum.Basic)
        if not os.path.exists(pathBase):
            return None
        if not os.path.exists(path1):
            return None
        if not os.path.exists(path2):
            return None
        if not os.path.exists(path3):
            return None

        df_basic = pd.read_csv(pathBase)
        df_1 = pd.read_csv(path1)
        df_2 = pd.read_csv(path2)
        df_3 = pd.read_csv(path3)
        classList = self.api.Df_To_BasicClass(df_basic, df_1, df_2, df_3)
        self.main.BoardCast(f"基础数据长度为：{len(classList)}")
        #self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Basic)
        task = asyncio.get_running_loop().create_task(self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Basic))
        task.add_done_callback(self.main.task_finished_callback_Basic)
        #self.main.BoardCast("处理基础数据完成")

    def RequestAdjust(self):
        self.main.isInFactor = True
        self.main.BoardCast("处理复权数据")
        count_stock = 0
        dfList = []
        codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()

        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""

        sameList = set()

        for code in codeList:
            if code in sameList:
                self.main.BoardCast("已经拉取过，跳过")
                continue

            t0 = time.perf_counter()

            df = self.api.Request_Adjust(code)
            if df is None:
                continue
            dfList.append(df)
            self.main.fileProcessor.SaveCSV(df, code, FileProcessor.FileEnum.Adjust)

            count_stock = count_stock + 1
            t1 = time.perf_counter()
            totalCostTime = totalCostTime + (t1 - t0)
            preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
            totalCostTimeStr = self.format_seconds(totalCostTime)
            preCostTimeStr = self.format_seconds(preCostTime)
            self.main.BoardCast(f"正在通过api拉取复权数据， 当前第{count_stock}条,数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            sameList.add(code)


        df_all = pd.concat(dfList, ignore_index=True)
        classList = self.api.Df_To_AdjustClass(df_all)
        if classList is None :
            return
        
        task = asyncio.get_running_loop().create_task(self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Adjust))
        task.add_done_callback(self.main.task_finished_callback_Factor)
        self.main.BoardCast("处理复权数据完成")



    def RequestDaily(self, startData, endData):
        self.main.isInDaily = True
        self.main.BoardCast("处理日线数据")
        #获取股票代码列表
        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""

        sameList = set()
        dfList = []
        codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()
        for code in codeList:
            if code in sameList:
                self.main.BoardCast("已经拉取过，跳过")
                continue

            
            t0 = time.perf_counter()

            df = self.api.RequestDaily(code, startData, endData)
            if df is None:
                continue
            dfList.append(df)
            self.main.fileProcessor.SaveCSV(df, code, FileProcessor.FileEnum.Daily)

            count_stock = count_stock + 1
            t1 = time.perf_counter()
            totalCostTime = totalCostTime + (t1 - t0)
            preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
            totalCostTimeStr = self.format_seconds(totalCostTime)
            preCostTimeStr = self.format_seconds(preCostTime)
            self.main.BoardCast(f"正在通过api拉取日线数据， 当前第{count_stock}条,时间为从{startData}  到 {endData}，数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            sameList.add(code)

        
        df_all = pd.concat(dfList, ignore_index=True)
        
        classList = self.api.Df_To_DailyClass(df_all)
        if classList is None:
            return
        task = asyncio.get_running_loop().create_task(self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Daily))
        task.add_done_callback(self.main.task_finished_callback_Daily)
        self.main.BoardCast("处理日线数据完成")



    def format_seconds(self, seconds: float) -> str:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"