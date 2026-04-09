from typing import TYPE_CHECKING
from datetime import date, datetime, timedelta
from src.main_code.Core.Calculate import CalculationDataHandle
if TYPE_CHECKING:
    from src.main_code.Core import Main

class BaseClass:
    startDate : str         #开始日期
    endDate : str         #结束日期
    daysContains:int       #日期区间
    targetChange:float      #目标涨跌幅

    isOutST : bool
    isOutCY : bool
    isOutKC : bool


    def Init(self, main:"Main.processor"):
        print("模式匹配模块初始化成功")
        self.main = main

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

        #同样和回测一样，一天一天的往下执行向下一天移动时，保留240+判断区间 + 20天
        #然后用windows类，判断前0天到前self.daysContains的涨跌幅， 大于self.targetChange， 那就记录下当前的日期
        #开始天是self.daysContains前，结束天是今天，历史蜡烛图直接拿开始天的list240，蜡烛结束图在行进到下一天进行记录，直到记录够240天
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

        while nextDayStd < stopDayStd:
            #移动到下一天
            nextDayStr = await matchCalculationHandle.MoveDateToNextDay()
            if(nextDayStr == ""):
                return
            nextDayStd = datetime.strptime(nextDayStr, date_format)



        self.isInMatch = False
        self.main.SetIsInHandle(False)
        print("模式匹配结束")

    def SendMatchResult(self):
        print("结束模式匹配")


    def StartHandleResult(self, msg):
        print("开始结果处理")


    def SendHandleResult(self):
        print("结果处理完毕发送")
    