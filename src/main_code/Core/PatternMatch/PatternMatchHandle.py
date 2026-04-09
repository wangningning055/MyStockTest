from typing import TYPE_CHECKING
from datetime import date, datetime, timedelta
from src.main_code.Core.Calculate import CalculationDataHandle
from typing import List, Optional, Callable, Dict, Any, Union
import asyncio
from src.main_code.Core import Const
if TYPE_CHECKING:
    from src.main_code.Core import Main

class BaseClass:
    startDate : str         #开始日期
    endDate : str         #结束日期
    daysContains:int       #日期区间
    targetChange:float      #目标涨跌幅
    ValueWindow:List[int]        #市值区间
    PriceWindow:List[int]        #价格区间

    isOutST : bool
    isOutCY : bool
    isOutKC : bool
    isNeedStop : bool


    def Init(self, main:"Main.processor"):
        print("模式匹配模块初始化成功")
        self.main = main
        self.isNeedStop = False
        self.ValueWindow.append(-1)
        self.ValueWindow.append(-1)
        self.PriceWindow.append(-1)
        self.PriceWindow.append(-1)

    async def StartMatch(self, msg):
        print(f"开始模式匹配: {msg}")
        self.startDate = msg["start_date"]
        endDate = msg["end_date"]
        if endDate == "":
            endDate = self.main.calculationDataHandle.todayStr
        self.endDate = endDate
        self.daysContains = msg["conditions"][0]["days_min"]
        self.targetChange = msg["conditions"][0]["change_min"]

        self.isOutCY = msg["exclude_cy"]
        self.isOutKC = msg["exclude_kc"]
        self.isOutST = msg["exclude_st"]

        #更新新的缓存长度
        oldLength = Const.dateListLength
        Const.dateListLength = oldLength + self.daysContains

        self.isInMatch = True
        self.main.calculationDataHandle.ClearDic()
        self.main.calculationDataHandle.isPreheating = False
        print("开始执行模式匹配")
        # 20210104
        self.main.SetIsInHandle(True)
        matchCalculationHandle = CalculationDataHandle.BaseClass()
        self.matchCalculationHandle = matchCalculationHandle
        matchCalculationHandle.isOutST = self.isOutST
        matchCalculationHandle.isOutCY = self.isOutCY
        matchCalculationHandle.isOutKC = self.isOutKC
        
        matchCalculationHandle.Init(self.main, self.startDate)
        await matchCalculationHandle.DataPreheating()

        #初始化数据
        nextDayStr = self.startDate
        starDayStr = self.startDate
        date_format = "%Y%m%d"
        nextDayStd = datetime.strptime(nextDayStr, date_format)
        starDayStd = datetime.strptime(starDayStr, date_format)

        stopStr = self.endDate
        stopDayStd = datetime.strptime(stopStr, date_format)

        tempStop = 0

        totalDay = (stopDayStd - starDayStd).days

        
        newAdd = []  #code, count
        removeList = []
        while nextDayStd < stopDayStd:
            await asyncio.sleep(0)
            if self.isNeedStop:
                break




            #这里记得再更新已有的结果列表，把蜡烛图更新够240天


            for pairs in newAdd:
                pairs[1] += 1
                if(pairs[1] > self.daysContains + 20):
                    removeList.append(pairs)
            
            for pairs in removeList:
                newAdd.remove(pairs)

            removeList.clear()
            await asyncio.sleep(0)

            res = self.main.analysisHandle.RunGetStockListByPatternMatch(self.matchCalculationHandle, self.isOutKC, self.isOutCY, self.isOutST, self.ValueWindow, self.PriceWindow, self.daysContains, self.targetChange, newAdd)
            await asyncio.sleep(0)
            
            for cls in res:
                pairs = [cls.code, 0]
                newAdd.append(pairs)

            #这里处理res，记录完整的响应数据



            await asyncio.sleep(0)

            #移动到下一天
            nextDayStr = await matchCalculationHandle.MoveDateToNextDay()
            await asyncio.sleep(0)
            if(nextDayStr == ""):
                return
            nextDayStd = datetime.strptime(nextDayStr, date_format)


        #执行消息发送

        self.isInMatch = False
        self.main.SetIsInHandle(False)
        Const.dateListLength = oldLength

        print("模式匹配结束")

    def SendMatchResult(self):
        print("结束模式匹配")


    def StartHandleResult(self, msg):
        print("开始结果处理")


    def SendHandleResult(self):
        print("结果处理完毕发送")
    