import src.main_code.Core.BackTest.StockTotal as StockTotal
from src.main_code.Core import Main
import traceback
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from datetime import date, datetime, timedelta
import time
import asyncio
from src.main_code.Core.Calculate import CalculationDataHandle
import json
from dataclasses import dataclass, field, asdict
from src.main_code.Core import Const
class BaseClass:
    totalStock : StockTotal.BaseClass
    startDate : str     #开始日期
    stopDate : str      #结束日期
    isOutST : bool
    isOutCY : bool
    isOutKC : bool
    isInit :bool

    isNeedStop : bool
    isInBackTest : bool

    def __init__(self):
        self.isOutCY = False
        self.isOutKC = False
        self.isOutCY = False
        self.Stock = None
        self.startDate = "20220104"
        self.stopDate = "20220204"
        self.isInit = False
    def Init(self, main):
        self.main : Main.processor = main
        print("回测模块初始化完毕")

    async def CreateStockByJson(self, jsonStr):
        #这里解析json
        try:
            print(f"回测数据验证:{jsonStr}")
            msgCls = BackTestMsgDataStruct.Msg_Base(**jsonStr)
            print("回测数据验证成功")
            self.main.BoardCast("回测数据验证成功")
            self.isOutCY = msgCls.isExcludeCY
            self.isOutKC = msgCls.isExcludeKC
            self.isOutST = msgCls.isExcludeST
            self.totalStock = StockTotal.BaseClass(self)
            self.isInit =  self.totalStock.Init(msgCls.config)
            self.startDate = msgCls.start_date
            self.stopDate = msgCls.end_date
            if self.isInit == False:
                print("回测仓位初始化失败")
                self.main.BoardCast("回测仓位初始化失败")
                return
            print("仓位初始化完毕")

            self.isNeedStop = False
            await self.StartBackTest()
        except Exception as e:
            print(f"❌ 回测数据验证失败: {e}")
            self.main.BoardCast(f"❌ 回测数据验证失败: {e}")
            full_trace = traceback.format_exc()

            print(f"❌ 回测数据验证失败: {full_trace}")


    async def StartBackTest(self):
        self.isInBackTest = True
        self.main.calculationDataHandle.ClearDic()
        self.main.calculationDataHandle.isPreheating = False
        print("开始执行回测")
        # 20210104
        self.main.SetIsInHandle(True)
        backTestCalculationHandle = CalculationDataHandle.BaseClass(1)
        self.backTestCalculationHandle = backTestCalculationHandle
        backTestCalculationHandle.isOutST = self.isOutST
        backTestCalculationHandle.isOutCY = self.isOutCY
        backTestCalculationHandle.isOutKC = self.isOutKC
        
        backTestCalculationHandle.Init(self.main, self.startDate)
        await backTestCalculationHandle.DataPreheating()

        #初始化数据
        nextDayStr = self.startDate
        starDayStr = self.startDate
        date_format = "%Y%m%d"
        nextDayStd = datetime.strptime(nextDayStr, date_format)
        starDayStd = datetime.strptime(starDayStr, date_format)

        stopStr = self.stopDate
        stopDayStd = datetime.strptime(stopStr, date_format)

        tempStop = 0

        totalDay = (stopDayStd - starDayStd).days

        refreshLength = Const.dateListRefreshLength_BackTest
        refreshCount = 0
        #鉴于源数据源的滞后性，先依据昨天的数据执行买卖，再更新新一天的数据
        while nextDayStd < stopDayStd:
            if self.isNeedStop == True:
                print("回测被停止")
                self.main.BoardCast("回测被停止")
                self.isNeedStop = False
                break

            if refreshCount < refreshLength:
                refreshCount += 1
            else:
                if stopStr not in self.backTestCalculationHandle.totalDateList:
                    print("重初始化")
                    refreshCount = 0
                    now = self.backTestCalculationHandle.todayStr
                    self.backTestCalculationHandle.ClearDic()
                    backTestCalculationHandle = CalculationDataHandle.BaseClass(1)
                    self.backTestCalculationHandle = backTestCalculationHandle
                    backTestCalculationHandle.isOutST = self.isOutST
                    backTestCalculationHandle.isOutCY = self.isOutCY
                    backTestCalculationHandle.isOutKC = self.isOutKC
                    backTestCalculationHandle.Init(self.main, now)
                    self.main.analysisHandle.evaluator = None
                    await backTestCalculationHandle.DataPreheating()
                    self.main.analysisHandle.InitEvaluator(backTestCalculationHandle)



            passDayCount = (nextDayStd - starDayStd).days
            print(f"------------------------开始新的一轮，这天是：{nextDayStr}， 结束天是：{stopStr}--过去了{passDayCount}天----总共是{totalDay}天------------------------------")
            self.main.SetIsInHandle(True)
            self.main.SendProgress(passDayCount / totalDay if totalDay > 0 else 1)
            await asyncio.sleep(0)

            #当天执行卖
            await self.ExecuteSell()
            await asyncio.sleep(0)


            #当天执行选股
            await self.ExecuteBuySelect()
            await asyncio.sleep(0)


            #更新今天的数据
            await self.UpdateStock(nextDayStr)
            await asyncio.sleep(0)


            #移动到下一天
            nextDayStr = await backTestCalculationHandle.MoveDateToNextDaySample()
            await asyncio.sleep(0)
            if(nextDayStr == ""):
                return
            nextDayStd = datetime.strptime(nextDayStr, date_format)

            #下一天用前一天的选股结果以收盘价买入
            await self.ExecuteBuy()
            await asyncio.sleep(0)

        #这里需要整理结果数据，然后传给前端
        res = self.totalStock.GetResult(nextDayStr)

        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_BACK_TEST, res)


        #结束
        self.isInBackTest = False
        self.main.SetIsInHandle(False)
        print("回测结束")
        self.backTestCalculationHandle.ClearDic()
        self.backTestCalculationHandle = {}


    def StopBackTest(self):
        if self.isInBackTest == True:
            self.isNeedStop = True
            print("回测停止")

    async def ExecuteBuySelect(self):
        await self.totalStock.ExecuteBuySelect()

    async def ExecuteBuy(self):
        await self.totalStock.ExecuteBuy()
        
    async def ExecuteSell(self):
        await self.totalStock.ExecuteSell()

    async def UpdateStock(self, date):
        self.totalStock.UpdateStock(date)



