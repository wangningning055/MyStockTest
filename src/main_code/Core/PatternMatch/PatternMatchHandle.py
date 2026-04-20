from typing import TYPE_CHECKING
from datetime import date, datetime, timedelta
from src.main_code.Core.Calculate import CalculationDataHandle
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
import src.main_code.Core.PatternMatch.MatchResStruct as MatchResStruct
from typing import List, Optional, Callable, Dict, Any, Union
import asyncio
from dataclasses import dataclass, field, asdict
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
    ConditionList:List[Dict]    #涨跌幅条件列表

    matchRes: MatchResStruct.Response

    isOutST : bool
    isOutCY : bool
    isOutKC : bool
    isNeedStop : bool


    def Init(self, main:"Main.processor"):
        print("模式匹配模块初始化成功")
        self.main = main
        self.isNeedStop = False
        self.ValueWindow = []
        self.PriceWindow = []
        self.ConditionList = []
        self.ValueWindow.append(-1)
        self.ValueWindow.append(-1)
        self.PriceWindow.append(-1)
        self.PriceWindow.append(-1)
        self.matchRes = MatchResStruct.Response()
        self.matchRes.matches = []



    async def StartMatch(self, msg):
        print(f"开始模式匹配: {msg}")
        totalMatchDic = []

        self.matchRes = MatchResStruct.Response()
        self.matchRes.matches = []
        self.startDate = msg["start_date"]
        endDate = msg["end_date"]
        if endDate == "":
            endDate = self.main.calculationDataHandle.todayStr
        self.endDate = endDate
        self.isOutCY = msg["exclude_cy"]
        self.isOutKC = msg["exclude_kc"]
        self.isOutST = msg["exclude_st"]

        minValue = msg["market_cap_range"]["min"]
        maxValue = msg["market_cap_range"]["max"]
        valueIsUnlimited = msg["market_cap_range"]["unlimited"]
        if valueIsUnlimited == True or maxValue is None:
            maxValue = -1

        if minValue > maxValue and maxValue != -1:
            minValue = -1
            maxValue = -1

        minPrice = msg["price_range"]["min"]
        maxPrice = msg["price_range"]["max"]
        priceIsUnlimited = msg["price_range"]["unlimited"]
        if priceIsUnlimited == True or maxPrice is None:
            maxPrice = -1

        if minPrice > maxPrice and maxPrice != -1:
            minPrice = -1
            maxPrice = -1

        self.ValueWindow.append(minValue)
        self.ValueWindow.append(maxValue)
        self.PriceWindow.append(minPrice)
        self.PriceWindow.append(maxPrice)
        
        maxDayCount, conditionList = self.InitConditions(msg["conditions"])


        self.daysContains = maxDayCount
        self.ConditionList = conditionList

        if len(self.ConditionList) <= 0:
            self.main.BoardCast("条件列表中没有有效的条件")
            print("条件列表中没有有效的条件")
            #记得发送匹配结束的消息
            self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_PATTERN_MATCH, "none")
            return



        #更新新的缓存长度
        #oldLength = Const.dateListLength_PatternMatch
        #Const.dateListLength_PatternMatch = oldLength + self.daysContains + 20

        self.isInMatch = True
        self.main.calculationDataHandle.ClearDic()
        self.main.calculationDataHandle.isPreheating = False
        print("开始执行模式匹配")

        self.main.SetIsInHandle(True)
        matchCalculationHandle = CalculationDataHandle.BaseClass(2)
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


        totalDay = (stopDayStd - starDayStd).days
        
        newAdd = []  #code, count
        removeList = []
        passDayCount = 0

        refreshLength = Const.dateListRefreshLength_PatternMatch
        refreshCount = 0
        
        while nextDayStd < stopDayStd:
            await asyncio.sleep(0)
            if self.isNeedStop:
                break

            if refreshCount < refreshLength:
                refreshCount += 1
            else:
                if stopStr not in self.matchCalculationHandle.totalDateList:
                    print("重初始化")
                    refreshCount = 0
                    now = self.matchCalculationHandle.todayStr
                    self.matchCalculationHandle.ClearDic()
                    matchCalculationHandle = CalculationDataHandle.BaseClass(2)
                    self.matchCalculationHandle = matchCalculationHandle
                    matchCalculationHandle.isOutST = self.isOutST
                    matchCalculationHandle.isOutCY = self.isOutCY
                    matchCalculationHandle.isOutKC = self.isOutKC
                    matchCalculationHandle.Init(self.main, now)
                    await matchCalculationHandle.DataPreheating()



                
            #这里记得再更新已有的结果列表，把蜡烛图更新够240天
            for singleMatch in self.matchRes.matches:
                    if singleMatch.klineLength < 240:
                        clsSingle = self.matchCalculationHandle.GetBaseDataClass(singleMatch.code, self.matchCalculationHandle.todayStr)
                        if clsSingle == None:
                            continue
                        klineData = MatchResStruct.KlineData()
                        dt = datetime.strptime(clsSingle.trade_date, "%Y%m%d")
                        klineData.date = dt.strftime("%Y-%m-%d")
                        klineData.open = clsSingle.open
                        klineData.close = clsSingle.close
                        klineData.high = clsSingle.high
                        klineData.low = clsSingle.low
                        klineData.volume = clsSingle.volume / 10000           #手
                        klineData.turn = clsSingle.turn
                        klineData.change_Ratio = clsSingle.change_Ratio
                        singleMatch.kline.append(asdict(klineData))
                        singleMatch.klineLength += 1


            for pairs in newAdd:
                pairs[1] += 1
                if(pairs[1] > self.daysContains + 20):
                    removeList.append(pairs)
            
            for pairs in removeList:
                newAdd.remove(pairs)

            removeList.clear()
            await asyncio.sleep(0)
            res = self.main.analysisHandle.RunGetStockListByPatternMatch(self.matchCalculationHandle, self.isOutKC, self.isOutCY, self.isOutST, self.ValueWindow, self.PriceWindow, self.ConditionList, newAdd)
            await asyncio.sleep(0)
            
            for cls in res:
                pairs = [cls.code, 0]
                newAdd.append(pairs)

            #这里处理res，记录完整的响应数据,不要依赖cls
            self.SaveResult(res)

            await asyncio.sleep(0)

            self.matchCalculationHandle.totalBaseWindowData.clear()
            #移动到下一天



            nextDayStr = await matchCalculationHandle.MoveDateToNextDaySample()

            
            await asyncio.sleep(0)
            if(nextDayStr == ""):
                break
            nextDayStd = datetime.strptime(nextDayStr, date_format)
            passDayCount = (nextDayStd - starDayStd).days
            self.main.SetIsInHandle(True)
            progress = passDayCount / totalDay if totalDay > 0 else 1
            print("")
            print(f"    ######移动到下一天，进度：{progress} 当前天是：{nextDayStr}, 结束天是：{stopStr},已经过去：{passDayCount}， 总共有：{totalDay} 匹配数量：{len(self.matchRes.matches)}")
            print("")
            self.main.SendProgress(progress)


        #再执行消息发送

        totalMatchDic = []
        for match in self.matchRes.matches:
            totalMatchDic.append(asdict(match))
        
        self.matchRes.matches = totalMatchDic
        self.matchRes = asdict(self.matchRes)
        self.main.fileProcessor.SaveJson(self.matchRes)

        self.isInMatch = False
        self.main.SetIsInHandle(False)
        #Const.dateListLength_PatternMatch = oldLength
        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_PATTERN_MATCH, self.matchRes)

        print("模式匹配结束")
        self.matchCalculationHandle.ClearDic()
        self.matchCalculationHandle = {}

    def InitConditions(self, conditions):
        totalMaxDay = 0
        resConditionList = []
        for condition in conditions:
            minDay = condition["days_min"]
            maxDay = condition["days_max"]
            minChange = condition["change_min"]
            maxChange = condition["change_max"]
            isUnLimited = condition["unlimited"]
            if maxChange is None:
                maxChange = -99999
                isUnLimited = True
            if minDay > maxDay:
                continue
            if minChange > maxChange and isUnLimited == False:
                continue
            if maxDay > totalMaxDay:
                totalMaxDay = maxDay
            if isUnLimited == True:
                maxChange = -99999
            res = {
                "startDay" : minDay,
                "toDay" : maxDay,
                "minChange" : minChange,
                "maxChange" : maxChange
            }
            resConditionList.append(res)
        return totalMaxDay,resConditionList

    def StopMatch(self):
        if self.isInMatch == True:
            self.isNeedStop = True
            print("回测停止")


    def SaveResult(self,res:List[CalculationDataStruct.StructBaseClass]):
        for cls in res:
            match = MatchResStruct.Match()
            match.klineLength = 0
            self.matchRes.matches.append(match)
            match.code = cls.code
            match.name = cls.componyInfo.Name

            if len(cls.dataList_240) <= 0:
                continue

            endCls = cls.dataList_240[-1]

            if len(endCls.dataList_240) <= 0:
                continue

            if len(cls.dataList_240) > self.daysContains:
                endCls = cls.dataList_240[self.daysContains]

            dt_start = datetime.strptime(endCls.trade_date, "%Y%m%d")
            dt_end = datetime.strptime(cls.trade_date, "%Y%m%d")

            start_date = dt_start.strftime("%Y-%m-%d")
            end_date = dt_end.strftime("%Y-%m-%d")


            match.match_start = start_date
            match.match_end = end_date
            match.days = self.daysContains

            match.change_pct = (cls.close - endCls.close) / endCls.close
            match.change_pct *= 100

            match.kline = []
            #print(f"{match.name} 天数从：{match.match_start} 到{match.match_end }， 涨跌幅是：{ match.change_pct}")

            for clsSingle in cls.dataList_240:
                klineData = MatchResStruct.KlineData()
                dt = datetime.strptime(clsSingle.trade_date, "%Y%m%d")
                klineData.date = dt.strftime("%Y-%m-%d")
                klineData.open = clsSingle.open
                klineData.close = clsSingle.close
                klineData.high = clsSingle.high
                klineData.low = clsSingle.low
                klineData.volume = clsSingle.volume / 10000           #万手
                klineData.turn = clsSingle.turn
                klineData.change_Ratio = clsSingle.change_Ratio
                match.kline.append(asdict(klineData))
            
            match.params = self.CreateParam(self.matchCalculationHandle.GetBaseDataClass(cls.code, endCls.trade_date))
            match.kline.reverse()

    def CreateParam(self, cls: CalculationDataStruct.StructBaseClass):
        params ={
            "groups": [
            {
                "name": "基础标识",
                "items": [
                    {
                        "label": "股票代码",
                        "value": cls.code,
                        "type": "text"
                    },
                    {
                        "label": "交易日期",
                        "value": cls.trade_date,
                        "type": "text"
                    },
                    {
                        "label": "所属行业",
                        "value": cls.industry,
                        "type": "text"
                    },
                    {
                        "label": "是否ST",
                        "value": cls.isST,
                        "type": "number"
                    },
                    {
                        "label": "交易状态",
                        "value": cls.trade_state,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "股票评分",
                "items": [
                    {
                        "label": "价值股评分",
                        "value": cls.ValueScore,
                        "type": "number"
                    },
                    {
                        "label": "成长股评分",
                        "value": cls.GrowScore,
                        "type": "number"
                    },
                    {
                        "label": "是否行业上涨周期",
                        "value": cls.isInIndustryUp,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "价格数据(复权)",
                "items": [
                    {
                        "label": "开盘价",
                        "value": cls.open,
                        "type": "number"
                    },
                    {
                        "label": "收盘价",
                        "value": cls.close,
                        "type": "number"
                    },
                    {
                        "label": "昨收价",
                        "value": cls.last_close,
                        "type": "number"
                    },
                    {
                        "label": "最高价",
                        "value": cls.high,
                        "type": "number"
                    },
                    {
                        "label": "最低价",
                        "value": cls.low,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "价格数据(原始)",
                "items": [
                    {
                        "label": "开盘价(原始)",
                        "value": cls.open_ori,
                        "type": "number"
                    },
                    {
                        "label": "收盘价(原始)",
                        "value": cls.close_ori,
                        "type": "number"
                    },
                    {
                        "label": "最高价(原始)",
                        "value": cls.high_ori,
                        "type": "number"
                    },
                    {
                        "label": "最低价(原始)",
                        "value": cls.low_ori,
                        "type": "number"
                    },
                    {
                        "label": "均价(原始)",
                        "value": cls.avg_ori,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "均价与比值",
                "items": [
                    {
                        "label": "当日均价",
                        "value": cls.avg,
                        "type": "number"
                    },
                    {
                        "label": "均价涨跌幅",
                        "value": cls.avg_ratio,
                        "type": "percent"
                    },
                    {
                        "label": "5日均价",
                        "value": cls.avg_5,
                        "type": "number"
                    },
                    {
                        "label": "10日均价",
                        "value": cls.avg_10,
                        "type": "number"
                    },
                    {
                        "label": "20日均价",
                        "value": cls.avg_20,
                        "type": "number"
                    },
                    {
                        "label": "40日均价",
                        "value": cls.avg_40,
                        "type": "number"
                    },
                    {
                        "label": "60日均价",
                        "value": cls.avg_60,
                        "type": "number"
                    },
                    {
                        "label": "120日均价",
                        "value": cls.avg_120,
                        "type": "number"
                    },
                    {
                        "label": "240日均价",
                        "value": cls.avg_240,
                        "type": "number"
                    },
                    {
                        "label": "均价/5日均价比值",
                        "value": cls.avg_ratio_5,
                        "type": "number"
                    },
                    {
                        "label": "均价/10日均价比值",
                        "value": cls.avg_ratio_10,
                        "type": "number"
                    },
                    {
                        "label": "均价/20日均价比值",
                        "value": cls.avg_ratio_20,
                        "type": "number"
                    },
                    {
                        "label": "均价/40日均价比值",
                        "value": cls.avg_ratio_40,
                        "type": "number"
                    },
                    {
                        "label": "均价/60日均价比值",
                        "value": cls.avg_ratio_60,
                        "type": "number"
                    },
                    {
                        "label": "均价/120日均价比值",
                        "value": cls.avg_ratio_120,
                        "type": "number"
                    },
                    {
                        "label": "均价/240日均价比值",
                        "value": cls.avg_ratio_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "涨跌幅",
                "items": [
                    {
                        "label": "当日涨跌幅",
                        "value": cls.change_Ratio,
                        "type": "percent"
                    },
                    {
                        "label": "3日涨跌幅",
                        "value": cls.change_Ratio_3,
                        "type": "percent"
                    },
                    {
                        "label": "5日涨跌幅",
                        "value": cls.change_Ratio_5,
                        "type": "percent"
                    },
                    {
                        "label": "10日涨跌幅",
                        "value": cls.change_Ratio_10,
                        "type": "percent"
                    },
                    {
                        "label": "20日涨跌幅",
                        "value": cls.change_Ratio_20,
                        "type": "percent"
                    },
                    {
                        "label": "40日涨跌幅",
                        "value": cls.change_Ratio_40,
                        "type": "percent"
                    },
                    {
                        "label": "60日涨跌幅",
                        "value": cls.change_Ratio_60,
                        "type": "percent"
                    },
                    {
                        "label": "120日涨跌幅",
                        "value": cls.change_Ratio_120,
                        "type": "percent"
                    },
                    {
                        "label": "240日涨跌幅",
                        "value": cls.change_Ratio_240,
                        "type": "percent"
                    },
                    {
                        "label": "3日距今涨跌幅",
                        "value": cls.change_Ratio_single_3,
                        "type": "percent"
                    },
                    {
                        "label": "5日距今涨跌幅",
                        "value": cls.change_Ratio_single_5,
                        "type": "percent"
                    },
                    {
                        "label": "10日距今涨跌幅",
                        "value": cls.change_Ratio_single_10,
                        "type": "percent"
                    },
                    {
                        "label": "20日距今涨跌幅",
                        "value": cls.change_Ratio_single_20,
                        "type": "percent"
                    },
                    {
                        "label": "40日距今涨跌幅",
                        "value": cls.change_Ratio_single_40,
                        "type": "percent"
                    },
                    {
                        "label": "60日距今涨跌幅",
                        "value": cls.change_Ratio_single_60,
                        "type": "percent"
                    },
                    {
                        "label": "120日距今涨跌幅",
                        "value": cls.change_Ratio_single_120,
                        "type": "percent"
                    },
                    {
                        "label": "240日距今涨跌幅",
                        "value": cls.change_Ratio_single_240,
                        "type": "percent"
                    }
                ]
            },
            {
                "name": "振幅",
                "items": [
                    {
                        "label": "当日振幅",
                        "value": cls.amplitude,
                        "type": "percent"
                    },
                    {
                        "label": "3日振幅",
                        "value": cls.amplitude_3,
                        "type": "percent"
                    },
                    {
                        "label": "5日振幅",
                        "value": cls.amplitude_5,
                        "type": "percent"
                    },
                    {
                        "label": "10日振幅",
                        "value": cls.amplitude_10,
                        "type": "percent"
                    }
                ]
            },
            {
                "name": "成交量",
                "items": [
                    {
                        "label": "当日成交量(万手)",
                        "value": cls.volume / 10000,
                        "type": "number"
                    },
                    {
                        "label": "成交量涨跌幅",
                        "value": cls.volume_ratio,
                        "type": "percent"
                    },
                    {
                        "label": "3日成交量涨跌幅",
                        "value": cls.volume_ratio_3,
                        "type": "percent"
                    },
                    {
                        "label": "5日成交量涨跌幅",
                        "value": cls.volume_ratio_5_percent,
                        "type": "percent"
                    },
                    {
                        "label": "10日成交量涨跌幅",
                        "value": cls.volume_ratio_10,
                        "type": "percent"
                    },
                    {
                        "label": "20日成交量涨跌幅",
                        "value": cls.volume_ratio_20,
                        "type": "percent"
                    },
                    {
                        "label": "40日成交量涨跌幅",
                        "value": cls.volume_ratio_40,
                        "type": "percent"
                    },
                    {
                        "label": "当日量比",
                        "value": cls.volume_ratio_5,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "成交额",
                "items": [
                    {
                        "label": "当日成交额（亿）",
                        "value": cls.volume_price / 100000000,
                        "type": "currency"
                    },
                    {
                        "label": "成交额涨跌幅",
                        "value": cls.volume_price_ratio,
                        "type": "percent"
                    },
                    {
                        "label": "3日成交额涨跌幅",
                        "value": cls.volume_price_ratio_3,
                        "type": "percent"
                    },
                    {
                        "label": "5日成交额涨跌幅",
                        "value": cls.volume_price_ratio_5,
                        "type": "percent"
                    },
                    {
                        "label": "10日成交额涨跌幅",
                        "value": cls.volume_price_ratio_10,
                        "type": "percent"
                    },
                    {
                        "label": "20日成交额涨跌幅",
                        "value": cls.volume_price_ratio_20,
                        "type": "percent"
                    },
                    {
                        "label": "40日成交额涨跌幅",
                        "value": cls.volume_price_ratio_40,
                        "type": "percent"
                    }
                ]
            },
            {
                "name": "换手率与流通",
                "items": [
                    {
                        "label": "当日换手率",
                        "value": cls.turn,
                        "type": "percent"
                    },
                    {
                        "label": "资金流通率",
                        "value": cls.turn_value,
                        "type": "percent"
                    },
                    {
                        "label": "换手率涨跌幅",
                        "value": cls.turn_ratio,
                        "type": "percent"
                    }
                ]
            },
            {
                "name": "市值与估值",
                "items": [
                    {
                        "label": "总市值（亿）",
                        "value": cls.total_value / 100000000,
                        "type": "market_cap"
                    },
                    {
                        "label": "市盈率",
                        "value": cls.earn,
                        "type": "number"
                    },
                    {
                        "label": "市净率",
                        "value": cls.clean,
                        "type": "number"
                    },
                    {
                        "label": "市销率",
                        "value": cls.cash,
                        "type": "number"
                    },
                    {
                        "label": "市现率",
                        "value": cls.sale,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "压力位数值",
                "items": [
                    {
                        "label": "20日上压力位",
                        "value": cls.up_pressure_20,
                        "type": "number"
                    },
                    {
                        "label": "20日下压力位",
                        "value": cls.down_pressure_20,
                        "type": "number"
                    },
                    {
                        "label": "40日上压力位",
                        "value": cls.up_pressure_40,
                        "type": "number"
                    },
                    {
                        "label": "40日下压力位",
                        "value": cls.down_pressure_40,
                        "type": "number"
                    },
                    {
                        "label": "60日上压力位",
                        "value": cls.up_pressure_60,
                        "type": "number"
                    },
                    {
                        "label": "60日下压力位",
                        "value": cls.down_pressure_60,
                        "type": "number"
                    },
                    {
                        "label": "120日上压力位",
                        "value": cls.up_pressure_120,
                        "type": "number"
                    },
                    {
                        "label": "120日下压力位",
                        "value": cls.down_pressure_120,
                        "type": "number"
                    },
                    {
                        "label": "240日上压力位",
                        "value": cls.up_pressure_240,
                        "type": "number"
                    },
                    {
                        "label": "240日下压力位",
                        "value": cls.down_pressure_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "单日突破压力位",
                "items": [
                    {
                        "label": "突破20日上压力位",
                        "value": cls.is_break_upper_20,
                        "type": "number"
                    },
                    {
                        "label": "跌破20日下压力位",
                        "value": cls.is_break_lower_20,
                        "type": "number"
                    },
                    {
                        "label": "突破40日上压力位",
                        "value": cls.is_break_upper_40,
                        "type": "number"
                    },
                    {
                        "label": "跌破40日下压力位",
                        "value": cls.is_break_lower_40,
                        "type": "number"
                    },
                    {
                        "label": "突破60日上压力位",
                        "value": cls.is_break_upper_60,
                        "type": "number"
                    },
                    {
                        "label": "跌破60日下压力位",
                        "value": cls.is_break_lower_60,
                        "type": "number"
                    },
                    {
                        "label": "突破120日上压力位",
                        "value": cls.is_break_upper_120,
                        "type": "number"
                    },
                    {
                        "label": "跌破120日下压力位",
                        "value": cls.is_break_lower_120,
                        "type": "number"
                    },
                    {
                        "label": "突破240日上压力位",
                        "value": cls.is_break_upper_240,
                        "type": "number"
                    },
                    {
                        "label": "跌破240日下压力位",
                        "value": cls.is_break_lower_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "连续2日突破压力位",
                "items": [
                    {
                        "label": "连续2日突破20日上压力位",
                        "value": cls.is_break_upper_20_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日跌破20日下压力位",
                        "value": cls.is_break_lower_20_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日突破40日上压力位",
                        "value": cls.is_break_upper_40_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日跌破40日下压力位",
                        "value": cls.is_break_lower_40_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日突破60日上压力位",
                        "value": cls.is_break_upper_60_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日跌破60日下压力位",
                        "value": cls.is_break_lower_60_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日突破120日上压力位",
                        "value": cls.is_break_upper_120_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日跌破120日下压力位",
                        "value": cls.is_break_lower_120_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日突破240日上压力位",
                        "value": cls.is_break_upper_240_2,
                        "type": "number"
                    },
                    {
                        "label": "连续2日跌破240日下压力位",
                        "value": cls.is_break_lower_240_2,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "连续3日突破压力位",
                "items": [
                    {
                        "label": "连续3日突破20日上压力位",
                        "value": cls.is_break_upper_20_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日跌破20日下压力位",
                        "value": cls.is_break_lower_20_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日突破40日上压力位",
                        "value": cls.is_break_upper_40_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日跌破40日下压力位",
                        "value": cls.is_break_lower_40_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日突破60日上压力位",
                        "value": cls.is_break_upper_60_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日跌破60日下压力位",
                        "value": cls.is_break_lower_60_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日突破120日上压力位",
                        "value": cls.is_break_upper_120_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日跌破120日下压力位",
                        "value": cls.is_break_lower_120_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日突破240日上压力位",
                        "value": cls.is_break_upper_240_3,
                        "type": "number"
                    },
                    {
                        "label": "连续3日跌破240日下压力位",
                        "value": cls.is_break_lower_240_3,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "连续5日突破压力位",
                "items": [
                    {
                        "label": "连续5日突破20日上压力位",
                        "value": cls.is_break_upper_20_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日跌破20日下压力位",
                        "value": cls.is_break_lower_20_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日突破40日上压力位",
                        "value": cls.is_break_upper_40_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日跌破40日下压力位",
                        "value": cls.is_break_lower_40_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日突破60日上压力位",
                        "value": cls.is_break_upper_60_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日跌破60日下压力位",
                        "value": cls.is_break_lower_60_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日突破120日上压力位",
                        "value": cls.is_break_upper_120_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日跌破120日下压力位",
                        "value": cls.is_break_lower_120_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日突破240日上压力位",
                        "value": cls.is_break_upper_240_5,
                        "type": "number"
                    },
                    {
                        "label": "连续5日跌破240日下压力位",
                        "value": cls.is_break_lower_240_5,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "收盘价/压力位比值",
                "items": [
                    {
                        "label": "收盘价/20日上压力位",
                        "value": cls.ratio_close_upper_20,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/20日下压力位",
                        "value": cls.ratio_close_lower_20,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/40日上压力位",
                        "value": cls.ratio_close_upper_40,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/40日下压力位",
                        "value": cls.ratio_close_lower_40,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/60日上压力位",
                        "value": cls.ratio_close_upper_60,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/60日下压力位",
                        "value": cls.ratio_close_lower_60,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/120日上压力位",
                        "value": cls.ratio_close_upper_120,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/120日下压力位",
                        "value": cls.ratio_close_lower_120,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/240日上压力位",
                        "value": cls.ratio_close_upper_240,
                        "type": "number"
                    },
                    {
                        "label": "收盘价/240日下压力位",
                        "value": cls.ratio_close_lower_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "2日均价/压力位比值",
                "items": [
                    {
                        "label": "2日均价/20日上压力位",
                        "value": cls.ratio_close_upper_2_20,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/20日下压力位",
                        "value": cls.ratio_close_lower_2_20,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/40日上压力位",
                        "value": cls.ratio_close_upper_2_40,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/40日下压力位",
                        "value": cls.ratio_close_lower_2_40,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/60日上压力位",
                        "value": cls.ratio_close_upper_2_60,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/60日下压力位",
                        "value": cls.ratio_close_lower_2_60,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/120日上压力位",
                        "value": cls.ratio_close_upper_2_120,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/120日下压力位",
                        "value": cls.ratio_close_lower_2_120,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/240日上压力位",
                        "value": cls.ratio_close_upper_2_240,
                        "type": "number"
                    },
                    {
                        "label": "2日均价/240日下压力位",
                        "value": cls.ratio_close_lower_2_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "3日均价/压力位比值",
                "items": [
                    {
                        "label": "3日均价/20日上压力位",
                        "value": cls.ratio_close_upper_3_20,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/20日下压力位",
                        "value": cls.ratio_close_lower_3_20,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/40日上压力位",
                        "value": cls.ratio_close_upper_3_40,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/40日下压力位",
                        "value": cls.ratio_close_lower_3_40,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/60日上压力位",
                        "value": cls.ratio_close_upper_3_60,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/60日下压力位",
                        "value": cls.ratio_close_lower_3_60,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/120日上压力位",
                        "value": cls.ratio_close_upper_3_120,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/120日下压力位",
                        "value": cls.ratio_close_lower_3_120,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/240日上压力位",
                        "value": cls.ratio_close_upper_3_240,
                        "type": "number"
                    },
                    {
                        "label": "3日均价/240日下压力位",
                        "value": cls.ratio_close_lower_3_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "5日均价/压力位比值",
                "items": [
                    {
                        "label": "5日均价/20日上压力位",
                        "value": cls.ratio_close_upper_5_20,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/20日下压力位",
                        "value": cls.ratio_close_lower_5_20,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/40日上压力位",
                        "value": cls.ratio_close_upper_5_40,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/40日下压力位",
                        "value": cls.ratio_close_lower_5_40,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/60日上压力位",
                        "value": cls.ratio_close_upper_5_60,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/60日下压力位",
                        "value": cls.ratio_close_lower_5_60,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/120日上压力位",
                        "value": cls.ratio_close_upper_5_120,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/120日下压力位",
                        "value": cls.ratio_close_lower_5_120,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/240日上压力位",
                        "value": cls.ratio_close_upper_5_240,
                        "type": "number"
                    },
                    {
                        "label": "5日均价/240日下压力位",
                        "value": cls.ratio_close_lower_5_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "行业排名",
                "items": [
                    {
                        "label": "总市值行业排名",
                        "value": cls.total_value_ratio,
                        "type": "number"
                    },
                    {
                        "label": "市盈率行业排名",
                        "value": cls.earn_ratio,
                        "type": "number"
                    },
                    {
                        "label": "市净率行业排名",
                        "value": cls.clean_ratio,
                        "type": "number"
                    },
                    {
                        "label": "市销率行业排名",
                        "value": cls.cash_ratio,
                        "type": "number"
                    },
                    {
                        "label": "市现率行业排名",
                        "value": cls.sale_ratio,
                        "type": "number"
                    },
                    {
                        "label": "成交量行业排名",
                        "value": cls.volume_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "成交额行业排名",
                        "value": cls.total_price_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "成交额涨跌幅行业排名",
                        "value": cls.total_price_ratio_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "成交量涨跌幅行业排名",
                        "value": cls.volume_ratio_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "涨跌幅行业排名",
                        "value": cls.ratio_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "振幅行业排名",
                        "value": cls.amplitude_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "换手率行业排名",
                        "value": cls.turn_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "换手率涨跌幅行业排名",
                        "value": cls.turn_ratio_industry_rank,
                        "type": "number"
                    },
                    {
                        "label": "均价涨跌幅行业排名",
                        "value": cls.avg_industry_rank,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "成交量状态",
                "items": [
                    {
                        "label": "成交量状态_1日",
                        "value": cls.volumeState_1,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_3日",
                        "value": cls.volumeState_3,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_5日",
                        "value": cls.volumeState_5,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_10日",
                        "value": cls.volumeState_10,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_20日",
                        "value": cls.volumeState_20,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_40日",
                        "value": cls.volumeState_40,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_60日",
                        "value": cls.volumeState_60,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_120日",
                        "value": cls.volumeState_120,
                        "type": "number"
                    },
                    {
                        "label": "成交量状态_240日",
                        "value": cls.volumeState_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "价格状态",
                "items": [
                    {
                        "label": "价格状态_1日",
                        "value": cls.priceState_1,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_3日",
                        "value": cls.priceState_3,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_5日",
                        "value": cls.priceState_5,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_10日",
                        "value": cls.priceState_10,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_20日",
                        "value": cls.priceState_20,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_40日",
                        "value": cls.priceState_40,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_60日",
                        "value": cls.priceState_60,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_120日",
                        "value": cls.priceState_120,
                        "type": "number"
                    },
                    {
                        "label": "价格状态_240日",
                        "value": cls.priceState_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "振幅状态",
                "items": [
                    {
                        "label": "振幅状态_1日",
                        "value": cls.amplitudeState_1,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_3日",
                        "value": cls.amplitudeState_3,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_5日",
                        "value": cls.amplitudeState_5,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_10日",
                        "value": cls.amplitudeState_10,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_20日",
                        "value": cls.amplitudeState_20,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_40日",
                        "value": cls.amplitudeState_40,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_60日",
                        "value": cls.amplitudeState_60,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_120日",
                        "value": cls.amplitudeState_120,
                        "type": "number"
                    },
                    {
                        "label": "振幅状态_240日",
                        "value": cls.amplitudeState_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "1日量价形态",
                "items": [
                    {
                        "label": "放量增长",
                        "value": cls.is_up_up,
                        "type": "number"
                    },
                    {
                        "label": "缩量增长",
                        "value": cls.is_low_up,
                        "type": "number"
                    },
                    {
                        "label": "放量降低",
                        "value": cls.is_up_low,
                        "type": "number"
                    },
                    {
                        "label": "缩量降低",
                        "value": cls.is_low_low,
                        "type": "number"
                    },
                    {
                        "label": "放量横盘",
                        "value": cls.is_up_mid,
                        "type": "number"
                    },
                    {
                        "label": "缩量横盘",
                        "value": cls.is_low_mid,
                        "type": "number"
                    },
                    {
                        "label": "平量增长",
                        "value": cls.is_mid_up,
                        "type": "number"
                    },
                    {
                        "label": "平量降低",
                        "value": cls.is_mid_low,
                        "type": "number"
                    },
                    {
                        "label": "震荡上行",
                        "value": cls.is_pop_up,
                        "type": "number"
                    },
                    {
                        "label": "震荡下行",
                        "value": cls.is_pop_down,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "3日量价形态",
                "items": [
                    {
                        "label": "3日放量增长",
                        "value": cls.is_up_up_3,
                        "type": "number"
                    },
                    {
                        "label": "3日缩量增长",
                        "value": cls.is_low_up_3,
                        "type": "number"
                    },
                    {
                        "label": "3日放量降低",
                        "value": cls.is_up_low_3,
                        "type": "number"
                    },
                    {
                        "label": "3日缩量降低",
                        "value": cls.is_low_low_3,
                        "type": "number"
                    },
                    {
                        "label": "3日放量横盘",
                        "value": cls.is_up_mid_3,
                        "type": "number"
                    },
                    {
                        "label": "3日缩量横盘",
                        "value": cls.is_low_mid_3,
                        "type": "number"
                    },
                    {
                        "label": "3日平量增长",
                        "value": cls.is_mid_up_3,
                        "type": "number"
                    },
                    {
                        "label": "3日平量降低",
                        "value": cls.is_mid_low_3,
                        "type": "number"
                    },
                    {
                        "label": "3日震荡上行",
                        "value": cls.is_pop_up_3,
                        "type": "number"
                    },
                    {
                        "label": "3日震荡下行",
                        "value": cls.is_pop_down_3,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "5日量价形态",
                "items": [
                    {
                        "label": "5日放量增长",
                        "value": cls.is_up_up_5,
                        "type": "number"
                    },
                    {
                        "label": "5日缩量增长",
                        "value": cls.is_low_up_5,
                        "type": "number"
                    },
                    {
                        "label": "5日放量降低",
                        "value": cls.is_up_low_5,
                        "type": "number"
                    },
                    {
                        "label": "5日缩量降低",
                        "value": cls.is_low_low_5,
                        "type": "number"
                    },
                    {
                        "label": "5日放量横盘",
                        "value": cls.is_up_mid_5,
                        "type": "number"
                    },
                    {
                        "label": "5日缩量横盘",
                        "value": cls.is_low_mid_5,
                        "type": "number"
                    },
                    {
                        "label": "5日平量增长",
                        "value": cls.is_mid_up_5,
                        "type": "number"
                    },
                    {
                        "label": "5日平量降低",
                        "value": cls.is_mid_low_5,
                        "type": "number"
                    },
                    {
                        "label": "5日震荡上行",
                        "value": cls.is_pop_up_5,
                        "type": "number"
                    },
                    {
                        "label": "5日震荡下行",
                        "value": cls.is_pop_down_5,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "10日量价形态",
                "items": [
                    {
                        "label": "10日放量增长",
                        "value": cls.is_up_up_10,
                        "type": "number"
                    },
                    {
                        "label": "10日缩量增长",
                        "value": cls.is_low_up_10,
                        "type": "number"
                    },
                    {
                        "label": "10日放量降低",
                        "value": cls.is_up_low_10,
                        "type": "number"
                    },
                    {
                        "label": "10日缩量降低",
                        "value": cls.is_low_low_10,
                        "type": "number"
                    },
                    {
                        "label": "10日放量横盘",
                        "value": cls.is_up_mid_10,
                        "type": "number"
                    },
                    {
                        "label": "10日缩量横盘",
                        "value": cls.is_low_mid_10,
                        "type": "number"
                    },
                    {
                        "label": "10日平量增长",
                        "value": cls.is_mid_up_10,
                        "type": "number"
                    },
                    {
                        "label": "10日平量降低",
                        "value": cls.is_mid_low_10,
                        "type": "number"
                    },
                    {
                        "label": "10日震荡上行",
                        "value": cls.is_pop_up_10,
                        "type": "number"
                    },
                    {
                        "label": "10日震荡下行",
                        "value": cls.is_pop_down_10,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "20日量价形态",
                "items": [
                    {
                        "label": "20日放量增长",
                        "value": cls.is_up_up_20,
                        "type": "number"
                    },
                    {
                        "label": "20日缩量增长",
                        "value": cls.is_low_up_20,
                        "type": "number"
                    },
                    {
                        "label": "20日放量降低",
                        "value": cls.is_up_low_20,
                        "type": "number"
                    },
                    {
                        "label": "20日缩量降低",
                        "value": cls.is_low_low_20,
                        "type": "number"
                    },
                    {
                        "label": "20日放量横盘",
                        "value": cls.is_up_mid_20,
                        "type": "number"
                    },
                    {
                        "label": "20日缩量横盘",
                        "value": cls.is_low_mid_20,
                        "type": "number"
                    },
                    {
                        "label": "20日平量增长",
                        "value": cls.is_mid_up_20,
                        "type": "number"
                    },
                    {
                        "label": "20日平量降低",
                        "value": cls.is_mid_low_20,
                        "type": "number"
                    },
                    {
                        "label": "20日震荡上行",
                        "value": cls.is_pop_up_20,
                        "type": "number"
                    },
                    {
                        "label": "20日震荡下行",
                        "value": cls.is_pop_down_20,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "40日量价形态",
                "items": [
                    {
                        "label": "40日放量增长",
                        "value": cls.is_up_up_40,
                        "type": "number"
                    },
                    {
                        "label": "40日缩量增长",
                        "value": cls.is_low_up_40,
                        "type": "number"
                    },
                    {
                        "label": "40日放量降低",
                        "value": cls.is_up_low_40,
                        "type": "number"
                    },
                    {
                        "label": "40日缩量降低",
                        "value": cls.is_low_low_40,
                        "type": "number"
                    },
                    {
                        "label": "40日放量横盘",
                        "value": cls.is_up_mid_40,
                        "type": "number"
                    },
                    {
                        "label": "40日缩量横盘",
                        "value": cls.is_low_mid_40,
                        "type": "number"
                    },
                    {
                        "label": "40日平量增长",
                        "value": cls.is_mid_up_40,
                        "type": "number"
                    },
                    {
                        "label": "40日平量降低",
                        "value": cls.is_mid_low_40,
                        "type": "number"
                    },
                    {
                        "label": "40日震荡上行",
                        "value": cls.is_pop_up_40,
                        "type": "number"
                    },
                    {
                        "label": "40日震荡下行",
                        "value": cls.is_pop_down_40,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "60日量价形态",
                "items": [
                    {
                        "label": "60日放量增长",
                        "value": cls.is_up_up_60,
                        "type": "number"
                    },
                    {
                        "label": "60日缩量增长",
                        "value": cls.is_low_up_60,
                        "type": "number"
                    },
                    {
                        "label": "60日放量降低",
                        "value": cls.is_up_low_60,
                        "type": "number"
                    },
                    {
                        "label": "60日缩量降低",
                        "value": cls.is_low_low_60,
                        "type": "number"
                    },
                    {
                        "label": "60日放量横盘",
                        "value": cls.is_up_mid_60,
                        "type": "number"
                    },
                    {
                        "label": "60日缩量横盘",
                        "value": cls.is_low_mid_60,
                        "type": "number"
                    },
                    {
                        "label": "60日平量增长",
                        "value": cls.is_mid_up_60,
                        "type": "number"
                    },
                    {
                        "label": "60日平量降低",
                        "value": cls.is_mid_low_60,
                        "type": "number"
                    },
                    {
                        "label": "60日震荡上行",
                        "value": cls.is_pop_up_60,
                        "type": "number"
                    },
                    {
                        "label": "60日震荡下行",
                        "value": cls.is_pop_down_60,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "120日量价形态",
                "items": [
                    {
                        "label": "120日放量增长",
                        "value": cls.is_up_up_120,
                        "type": "number"
                    },
                    {
                        "label": "120日缩量增长",
                        "value": cls.is_low_up_120,
                        "type": "number"
                    },
                    {
                        "label": "120日放量降低",
                        "value": cls.is_up_low_120,
                        "type": "number"
                    },
                    {
                        "label": "120日缩量降低",
                        "value": cls.is_low_low_120,
                        "type": "number"
                    },
                    {
                        "label": "120日放量横盘",
                        "value": cls.is_up_mid_120,
                        "type": "number"
                    },
                    {
                        "label": "120日缩量横盘",
                        "value": cls.is_low_mid_120,
                        "type": "number"
                    },
                    {
                        "label": "120日平量增长",
                        "value": cls.is_mid_up_120,
                        "type": "number"
                    },
                    {
                        "label": "120日平量降低",
                        "value": cls.is_mid_low_120,
                        "type": "number"
                    },
                    {
                        "label": "120日震荡上行",
                        "value": cls.is_pop_up_120,
                        "type": "number"
                    },
                    {
                        "label": "120日震荡下行",
                        "value": cls.is_pop_down_120,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "240日量价形态",
                "items": [
                    {
                        "label": "240日放量增长",
                        "value": cls.is_up_up_240,
                        "type": "number"
                    },
                    {
                        "label": "240日缩量增长",
                        "value": cls.is_low_up_240,
                        "type": "number"
                    },
                    {
                        "label": "240日放量降低",
                        "value": cls.is_up_low_240,
                        "type": "number"
                    },
                    {
                        "label": "240日缩量降低",
                        "value": cls.is_low_low_240,
                        "type": "number"
                    },
                    {
                        "label": "240日放量横盘",
                        "value": cls.is_up_mid_240,
                        "type": "number"
                    },
                    {
                        "label": "240日缩量横盘",
                        "value": cls.is_low_mid_240,
                        "type": "number"
                    },
                    {
                        "label": "240日平量增长",
                        "value": cls.is_mid_up_240,
                        "type": "number"
                    },
                    {
                        "label": "240日平量降低",
                        "value": cls.is_mid_low_240,
                        "type": "number"
                    },
                    {
                        "label": "240日震荡上行",
                        "value": cls.is_pop_up_240,
                        "type": "number"
                    },
                    {
                        "label": "240日震荡下行",
                        "value": cls.is_pop_down_240,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "涨跌停特征",
                "items": [
                    {
                        "label": "是否涨停",
                        "value": cls.is_up_stop,
                        "type": "number"
                    },
                    {
                        "label": "是否跌停",
                        "value": cls.is_down_stop,
                        "type": "number"
                    },
                    {
                        "label": "是否触及涨停",
                        "value": cls.is_touch_up_stop,
                        "type": "number"
                    },
                    {
                        "label": "是否触及跌停",
                        "value": cls.is_touch_down_stop,
                        "type": "number"
                    },
                    {
                        "label": "是否一字板",
                        "value": cls.is_one_ban,
                        "type": "number"
                    }
                ]
            },
            {
                "name": "K线形态",
                "items": [
                    {
                        "label": "是否短实体",
                        "value": cls.is_short_entity,
                        "type": "number"
                    },
                    {
                        "label": "是否长上影线",
                        "value": cls.is_long_shadow_up,
                        "type": "number"
                    },
                    {
                        "label": "是否长下影线",
                        "value": cls.is_long_shadow_down,
                        "type": "number"
                    },
                    {
                        "label": "是否长十字",
                        "value": cls.is_long_cross,
                        "type": "number"
                    },
                    {
                        "label": "是否短十字",
                        "value": cls.is_short_cross,
                        "type": "number"
                    },
                    {
                        "label": "是否正T字",
                        "value": cls.is_T_up,
                        "type": "number"
                    },
                    {
                        "label": "是否倒T字",
                        "value": cls.is_T_down,
                        "type": "number"
                    }
                ]
            }
        ]
        }
        return params
    
