from datetime import date,datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core import Main
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core import Const
class BaseClass :
    def __init__(self):
        pass
    def Init(self, main):
        self.main :Main.processor = main
        self.totalComponyIns : CalculationDataStruct.StructIndustryTotalInfoClass = CalculationDataStruct.StructIndustryTotalInfoClass()
        self.totalBaseDailyData : CalculationDataStruct.AllDateStructBaseClass = CalculationDataStruct.AllDateStructBaseClass()
        self.InitIndustry()
        print("计算模块初始化完毕")
        self.GetBaseDataClass("000001.SZ","20260121", True)

    def InitIndustry(self):
        df = self.main.dbHandler.GetAllBasicData()
        temBasic = BasicDBStruct.DBStructClass()
        sameList = set()
        for key, val in df.items():
            code = key
            industry = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Industry)]
            name = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Name)]
            area = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Area)]
            cn_spell = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Cn_spell)]
            market = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Market)]
            list_status = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.List_Status)]
            list_date = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.List_date)]
            act_name = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Act_name)]
            act_ent_type = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Act_ent_type)]
            product = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Product)]
            business_scope = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Business_Scope)]
            introduction = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Introduction)]
            com_name = val[temBasic.GetNameByEnum(BasicDBStruct.ColumnEnum.Com_name)]


            componyInfoIns = CalculationDataStruct.StructComponyInfoClass()
            componyInfoIns.Code = code
            componyInfoIns.Industry = industry
            componyInfoIns.Name = name
            componyInfoIns.Area = area
            componyInfoIns.Cn_spell = cn_spell
            componyInfoIns.Market = market
            componyInfoIns.List_Status = list_status
            componyInfoIns.List_date = list_date
            componyInfoIns.Act_name = act_name
            componyInfoIns.Act_ent_type = act_ent_type
            componyInfoIns.Product = product
            componyInfoIns.Business_Scope = business_scope
            componyInfoIns.Introduction = introduction
            componyInfoIns.Com_name = com_name
            self.totalComponyIns.allStockList[code] = componyInfoIns
            self.totalComponyIns.code_industryStr_List[code] = industry

            if industry in sameList:
                industryIns = self.totalComponyIns.industryList[industry]
                industryIns.stockList[code] = componyInfoIns
            else:
                industryIns = CalculationDataStruct.StructIndustryInfoClass()
                industryIns.industryName = industry
                industryIns.stockList[code] = componyInfoIns
                self.totalComponyIns.industryList[industry] = industryIns
                sameList.add(industry)

        #print(f"总行业数:{len(self.totalComponyIns.industryList)}    总股数  :  {len(self.totalComponyIns.allStockList)}")
        #industryCls = self.totalComponyIns.GetIndustryClsByIndustryStr("玻璃")
        #INDUSTRY = self.totalComponyIns.GetIndustryStrByCode("000063.SZ")
        #print(f"行业名  {industryCls.industryName}，  行业股数量：{len(industryCls.stockList)},   {INDUSTRY}")
        

    def GetBaseDataClass(self, stockCode, date, isCalculate = False):
        tempDailyCls = DailyDBStruct.DBStructClass()
        tempAdjustCls = AdjustDBStruct.DBStructClass()
        print("开始计算")
        if (stockCode, date) in self.totalBaseDailyData.allDic:
            baseClass = self.totalBaseDailyData.allDic[stockCode, date]
            if isCalculate:
                self.CalculateBaseClass(baseClass)
            print("基础数据计算已在缓存种")
            return baseClass
        else:
            baseClass = CalculationDataStruct.StructBaseClass()
            dailyData = self.main.dbHandler.GetDailyRowByCodeAndDate(stockCode, date)
            if(dailyData == None):
                print("日期不存在")
                return None
            self.totalBaseDailyData.allDic[stockCode, date] = baseClass
            adjustTable = self.main.dbHandler.GetAdjustRowByCodeAndDate(stockCode, date)

            adjust = adjustTable[tempAdjustCls.GetNameByEnum(AdjustDBStruct.ColumnEnum.For_Adjust)]
            cur_date = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)]
            open_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Open_Price)] * adjust
            close_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Close_Price)] * adjust
            high_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.High_Price)] * adjust
            low_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Low_Price)] * adjust
            turn = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Exchange_Hand)]
            change_Ratio = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Change_Ratio)]
            amount = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount)]
            amount_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount_Price)]
            earn_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Earn_TTM)]
            clean = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Clean)]
            cash_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Cash_TTM)]
            sale_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Sale_TTM)]
            is_ST = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_ST)]
            is_Trading = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_Trading)]
            last_close_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Last_Close_Price)]
            average_price = (amount_price / amount) * adjust
            amplitude = (high_price - low_price) / last_close_price


            baseClass.code = stockCode
            baseClass.adjst = adjust
            baseClass.trade_date = cur_date
            baseClass.open = open_price
            baseClass.close = close_price
            baseClass.last_close = last_close_price
            baseClass.high = high_price
            baseClass.low = low_price
            baseClass.volume = amount
            baseClass.change_Ratio = change_Ratio
            baseClass.volume_price = amount_price

            baseClass.turn = turn
            baseClass.total_value = (amount / turn) * average_price
            baseClass.earn = earn_TTM
            baseClass.clean = clean
            baseClass.cash = cash_TTM
            baseClass.sale = sale_TTM

            baseClass.amplitude = amplitude
            baseClass.industry = self.totalComponyIns.GetIndustryStrByCode(stockCode)
            baseClass.isST = is_ST
            baseClass.trade_state = is_Trading
            baseClass.avg = average_price

            print("基础数据计算完毕")
            if(isCalculate):
                self.CalculateBaseClass(baseClass)
            return baseClass

    def CalculateBaseClass(self, baseClass : CalculationDataStruct.StructBaseClass):
        if(baseClass.isCalculate):
            return
        
        baseClass.isCalculate = True
        dataList = self.GetLastTradeDateList(baseClass.code, baseClass.trade_date, 240)
        print(f"开始计算：{len(dataList)}")
        #这里算出了前五天的交易日
        count = 0
        for val in dataList:
            print(val) 
            count = count + 1
            if(count > 5):
                break

        #这下面来计算各种各样的数据
        #volume_ratio:float        #当日成交量涨跌幅
        #volume_price_ratio: Optional[float] = None        #当日成交额涨跌幅
        #volume_ratio_5:float       #当日量比 
        #turn_ratio:float        #当日换手率涨跌幅
        
        #total_value_ratio:float       #总市值排行业前%
        #earn_ratio:float              #当日市盈率排行业前%
        #clean_ratio:float             #当日市净率排行业前%
        #cash_ratio:float              #当日市销率排行业前%
        #sale_ratio:float              #当日市现率排行业前%
        #value_flow_ratio:float        #当日流通市值排行业前%
        #value_ratio:float              #当日总市值排行业前%

        #avg_5:float             #5日均价
        #avg_10:float             #十日均价
        #avg_20:float            #20日均价
        #avg_40:float             #40均价
        #avg_60:float            #60日均价
        #avg_120:float           #120日均价
        #avg_240:float           #240日均价

        #avg_ratio_5:float             #当日均价与其他日均价的比
        #avg_ratio_10:float             #当日均价与其他日均价的比
        #avg_ratio_20:float              #20日均价
        #avg_ratio_40:float             #40均价
        #avg_ratio_60:float               #60日均价
        #avg_ratio_120:float              #120日均价
        #avg_ratio_240:float           #240日均价
        
        
        ##这下面还有行业相关的排名数据没有写
        #volume_industry_rank:float #成交量排名(前%)
        #total_price_industry_rank:float #成交额排名(前%)
        #total_price_ratio_industry_rank:float#成交额涨跌幅排名(前%)
        #volume_ratio_industry_rank:float #成交量涨跌幅排名(前%)
        #ratio_industry_rank:float#涨跌幅排名(前%)
        #amplitude_industry_rank:float#振幅排名(前%)
        #turn_ratio_industry_rank:float#换手率涨跌幅排名(前%)
        #avg_industry_rank:float#均价涨跌幅排名(前%)


        ##快捷指标
        #is_up_up:float#是否放量增长(>或小于1)
        #is_low_up:float#是否缩量增长
        #is_up_low:float#是否放量降低
        #is_low_low:float#是否缩量降低
        #is_up_mid:float#是否放量横盘
        #is_low_mid:float#是否缩量横盘
        #is_mid_up:float#是否平量增长
        #is_mid_low:float#是否平量降低
        pass

    def GetWindowDataClass(self, stockCode, startDate, toDate):
        pass

    def GetIndustryBaseData(self, industryStr):
        pass

    def GetIndustryWindowData(self, industryStr, startDate, toDate):
        pass


    def GetLastTradeDateList(self, code, dateStr, num):
        dayList = []
        dt = datetime.strptime(dateStr, "%Y%m%d")
        end_dt = datetime.strptime(Const.first_Data, "%Y%m%d")
        while len(dayList) < num and dt > end_dt:
            dt -= timedelta(days=1)  # 往前一天
            date_str = dt.strftime("%Y%m%d")
            dailyData = self.GetBaseDataClass(code, date_str)
            if(dailyData != None):
                dayList.append(date_str)
        return dayList


    def ReadDBDataInMemoryNoWait(self):
        print("开始载入数据库数据，这需要花上一段时间......")
        #self.main.BoardCast("开始载入数据库数据，这需要花上一段时间.....")
        #basicData = self.main.dbHandler.GetAllBasicData()
        dailyData = self.main.dbHandler.GetAllDailyDataNoWait()
        print(f"日线数据的长度是：{dailyData.__len__()}")
        dailyClassDic = {}
        for code, date_map in dailyData.items():
            latest_date = max(date_map)
            totalInstance = CalculationDataStruct.AllDateStructBaseClass(code, latest_date)
            totalInstance.code = code
            dailyClassDic[code] = totalInstance
            for date, value in date_map.items():
                instance = CalculationDataStruct.StructBaseClass()
                totalInstance.dateDic[date] = instance







                instance.close = close
                instance.high = high
                instance.trade_date = date
                instance.code = code
                instance.change_Ratio = change_Ratio
                #print(code, date, value["turn"])


        for key, value in dailyClassDic.items():
            #print(key,value)
            today = value.GetTodayData()
            high = today.high
            close = today.close
            change_Ratio = today.change_Ratio
            #print(abs(close/high))
            if change_Ratio >= 9.9:
                print(today.code, today.trade_date, today.change_Ratio)
            #for date, ins in value.dateDic.items():
            #    print(key, date, ins.close)

        self.main.BoardCast("数据库数据载入完成")
        print("数据库数据载入完成")




    async def ReadDBDataInMemory(self):
        print("开始载入数据库数据，这需要花上一段时间......")
        #self.main.BoardCast("开始载入数据库数据，这需要花上一段时间.....")
        #basicData = self.main.dbHandler.GetAllBasicData()
        dailyData = await self.main.dbHandler.GetAllDailyData()
        print(f"日线数据的长度是：{dailyData.__len__()}")
        dailyClassDic = {}
        for code, date_map in dailyData.items():
            latest_date = max(date_map)
            totalInstance = CalculationDataStruct.AllDateStructBaseClass(code, latest_date)
            totalInstance.code = code
            dailyClassDic[code] = totalInstance
            for date, value in date_map.items():
                instance = CalculationDataStruct.StructBaseClass()
                totalInstance.dateDic[date] = instance
                close = value["close"]
                high = value["high"]
                change_Ratio = value["change_ratio"]
                instance.close = close
                instance.high = high
                instance.trade_date = date
                instance.code = code
                instance.change_Ratio = change_Ratio
                #print(code, date, value["turn"])


        for key, value in dailyClassDic.items():
            #print(key,value)
            today = value.GetTodayData()
            high = today.high
            close = today.close
            change_Ratio = today.change_Ratio
            #print(abs(close/high))
            if change_Ratio >= 9.9:
                print(today.code, today.trade_date, today.change_Ratio)
            #for date, ins in value.dateDic.items():
            #    print(key, date, ins.close)



            #print(key, value.trade_date, value.close, value.high)


            


        #self.main.dbHandler.GetAllAdjustData()


        self.main.BoardCast("数据库数据载入完成")
        print("数据库数据载入完成")

