from datetime import date,datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core.Select import CalculationUtil
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
        self.GetBaseDataClass("300852.SZ","20260213", True)

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
                industryIns : CalculationDataStruct.StructIndustryInfoClass = self.totalComponyIns.industryList[industry]
                industryIns.stockList[code] = componyInfoIns
                industryIns.stockForSortList.append(componyInfoIns)
            else:
                industryIns = CalculationDataStruct.StructIndustryInfoClass()
                industryIns.industryName = industry
                industryIns.stockList[code] = componyInfoIns
                industryIns.stockForSortList.append(componyInfoIns)
                self.totalComponyIns.industryList[industry] = industryIns
                sameList.add(industry)





        #print(f"总行业数:{len(self.totalComponyIns.industryList)}    总股数  :  {len(self.totalComponyIns.allStockList)}")
        #industryCls = self.totalComponyIns.GetIndustryClsByIndustryStr("玻璃")
        #INDUSTRY = self.totalComponyIns.GetIndustryStrByCode("000063.SZ")
        #print(f"行业名  {industryCls.industryName}，  行业股数量：{len(industryCls.stockList)},   {INDUSTRY}")
        

    def GetBaseDataClass(self, stockCode, date, isCalculate = False) -> CalculationDataStruct.StructBaseClass:
        tempDailyCls = DailyDBStruct.DBStructClass()
        tempAdjustCls = AdjustDBStruct.DBStructClass()
        #print("开始计算")
        if (stockCode, date) in self.totalBaseDailyData.allDic:
            baseClass = self.totalBaseDailyData.allDic[stockCode, date]
            if isCalculate:
                self.CalculateBaseClass(baseClass)
            #print("基础数据计算已在缓存中")
            return baseClass
        else:
            baseClass = CalculationDataStruct.StructBaseClass()
            dailyData = self.main.dbHandler.GetDailyRowByCodeAndDate(stockCode, date)
            if(dailyData == None):
                #print("日期不存在")
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
            if(is_Trading != 1):
                average_price = 0
                amplitude = 0
            else:
                average_price = (amount_price / amount) * adjust
                amplitude = ((high_price - low_price) / last_close_price) * 100
                #print(f"成交价：{amount_price}   成交量：{amount}，振幅：{amplitude}, 均价{average_price}， 日期：{date}，上市状态：{is_Trading}")

            baseClass.code = stockCode
            baseClass.adjst = adjust
            baseClass.trade_date = cur_date
            baseClass.open = open_price * adjust
            baseClass.close = close_price * adjust
            baseClass.last_close = last_close_price
            baseClass.high = high_price * adjust
            baseClass.low = low_price * adjust
            baseClass.volume = amount
            baseClass.change_Ratio = change_Ratio
            baseClass.volume_price = amount_price

            baseClass.turn = turn
            if(is_Trading):
                baseClass.total_value = (amount / (turn / 100 )) * average_price
            baseClass.earn = earn_TTM
            baseClass.clean = clean
            baseClass.cash = cash_TTM
            baseClass.sale = sale_TTM

            baseClass.amplitude = amplitude
            baseClass.industry = self.totalComponyIns.GetIndustryStrByCode(stockCode)
            baseClass.isST = is_ST
            baseClass.trade_state = is_Trading
            baseClass.avg = average_price * adjust

            #print(f"复权因子是：{adjust}, 日期是{date}")
            if(isCalculate):
                self.CalculateBaseClass(baseClass)
            return baseClass

    def CalculateBaseClass(self, baseClass : CalculationDataStruct.StructBaseClass):
        if(baseClass.isCalculate):
            return
        
        baseClass.isCalculate = True
        dataList_240:list[CalculationDataStruct.StructBaseClass] = self.GetLastDateDataByNum(baseClass.code, baseClass.trade_date, 240)
        baseClass.dataList_240 = dataList_240
        count = 0
       
        print(f"开始计算前240天：{len(dataList_240)}，交易日当天：{baseClass.trade_date}， 交易日前一天：{dataList_240[0].trade_date}")

        #这下面来计算各种各样的数据amplitude
        print(f"当日涨跌幅是{baseClass.change_Ratio}")
        print(f"当日震幅是{baseClass.amplitude}")

        baseClass.amplitude_3 = CalculationUtil.GetAmplitude_Avg(baseClass, 3)
        baseClass.amplitude_5 = CalculationUtil.GetAmplitude_Avg(baseClass, 5)
        baseClass.amplitude_10 = CalculationUtil.GetAmplitude_Avg(baseClass, 10)


        baseClass.change_Ratio_3 = CalculationUtil.GetChange_Ratio(baseClass, 3)
        print(f"3日涨跌幅是{baseClass.change_Ratio_3}")
        baseClass.change_Ratio_5 = CalculationUtil.GetChange_Ratio(baseClass, 5)
        print(f"5日涨跌幅是{baseClass.change_Ratio_5}")
        baseClass.change_Ratio_10 = CalculationUtil.GetChange_Ratio(baseClass, 10)
        print(f"10日涨跌幅是{baseClass.change_Ratio_10}")
        baseClass.change_Ratio_20 = CalculationUtil.GetChange_Ratio(baseClass, 20)
        print(f"20日涨跌幅是{baseClass.change_Ratio_20}")
        baseClass.change_Ratio_40 = CalculationUtil.GetChange_Ratio(baseClass, 40)
        print(f"40日涨跌幅是{baseClass.change_Ratio_40}")
        baseClass.change_Ratio_60 = CalculationUtil.GetChange_Ratio(baseClass, 60)
        print(f"60日涨跌幅是{baseClass.change_Ratio_60}")
        baseClass.change_Ratio_120 = CalculationUtil.GetChange_Ratio(baseClass, 120)
        print(f"120日涨跌幅是{baseClass.change_Ratio_120}")
        baseClass.change_Ratio_240 = CalculationUtil.GetChange_Ratio(baseClass, 240)
        print(f"240日涨跌幅是{baseClass.change_Ratio_240}")



        baseClass.volume_ratio = CalculationUtil.GetVolume_Ratio(baseClass, 1)
        print(f"成交量涨跌幅是{baseClass.volume_ratio}")

        baseClass.volume_ratio_3 = CalculationUtil.GetVolume_Ratio(baseClass, 3)
        print(f"3日与3日平均成交量相比涨跌幅是{baseClass.volume_ratio_3}")

        baseClass.volume_ratio_5 = CalculationUtil.GetVolume_Ratio(baseClass, 5)
        print(f"5日与5日平均成交量相比涨跌幅是{baseClass.volume_ratio_5}")

        baseClass.volume_ratio_10 = CalculationUtil.GetVolume_Ratio(baseClass, 10)
        print(f"10日与10日平均成交量相比涨跌幅是{baseClass.volume_ratio_10}")

        baseClass.volume_ratio_20 = CalculationUtil.GetVolume_Ratio(baseClass, 20)
        print(f"20日与20日平均成交量相比涨跌幅是{baseClass.volume_ratio_20}")

        baseClass.volume_ratio_40 = CalculationUtil.GetVolume_Ratio(baseClass, 40)
        print(f"40日与40日平均成交量相比涨跌幅是{baseClass.volume_ratio_40}")


        baseClass.volume_price_ratio = CalculationUtil.GetVolume_Price(baseClass, 1)
        print(f"当成交额涨跌幅是{baseClass.volume_price_ratio}")

        baseClass.volume_price_ratio_3 = CalculationUtil.GetVolume_Price(baseClass, 3)
        print(f"与3日平均成交额涨跌幅是{baseClass.volume_price_ratio_3}")

        baseClass.volume_price_ratio_5 = CalculationUtil.GetVolume_Price(baseClass, 5)
        print(f"与5日平均成交额涨跌幅是{baseClass.volume_price_ratio_5}")

        baseClass.volume_price_ratio_10 = CalculationUtil.GetVolume_Price(baseClass, 10)
        print(f"与10日平均成交额涨跌幅是{baseClass.volume_price_ratio_10}")

        baseClass.volume_price_ratio_20 = CalculationUtil.GetVolume_Price(baseClass, 20)
        print(f"与20日平均成交额涨跌幅是{baseClass.volume_price_ratio_20}")

        baseClass.volume_price_ratio_40 = CalculationUtil.GetVolume_Price(baseClass, 40)
        print(f"与40日平均成交额涨跌幅是{baseClass.volume_price_ratio_40}")

        baseClass.volume_ratio_5 = CalculationUtil.GetVolume_5(baseClass)
        print(f"量比是{baseClass.volume_ratio_5}")

        baseClass.avg_ratio = CalculationUtil.GetAvg_Ratio(baseClass)
        print(f"当日均价涨跌幅是：{baseClass.avg_ratio}")


        baseClass.turn_ratio = CalculationUtil.GetTurn_Ratio(baseClass)
        print(f"当日换手率涨跌幅是{baseClass.turn_ratio}")

        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 1)
        #print(f"当日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 5)
        #print(f"5日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 10)
        #print(f"10日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 20)
        #print(f"20日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 60)
        #print(f"60日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 120)
        #print(f"120日资金成交动量是{baseClass.volume_price_energy}")
        baseClass.volume_price_energy = CalculationUtil.GetVolume_Energy(baseClass, 240)
        #print(f"240日资金成交动量是{baseClass.volume_price_energy}")


        baseClass.total_value_ratio = CalculationUtil.GetIndustry_Rank_Value(baseClass, self)
        print(f"流通市值排名是：{baseClass.total_value_ratio}%")
        baseClass.earn_ratio = CalculationUtil.GetIndustry_Rank_Earn(baseClass, self)
        print(f"市盈率排名是：{baseClass.earn_ratio}%")
        baseClass.clean_ratio = CalculationUtil.GetIndustry_Rank_Clean(baseClass, self)
        print(f"市净率排名是：{baseClass.clean_ratio}%")
        baseClass.cash_ratio = CalculationUtil.GetIndustry_Rank_Cash(baseClass, self)
        print(f"市现率排名是：{baseClass.cash_ratio}%")
        baseClass.sale_ratio = CalculationUtil.GetIndustry_Rank_Sale(baseClass, self)
        print(f"市销率排名是：{baseClass.sale_ratio}%")

        baseClass.avg_5 = CalculationUtil.GetAvg(baseClass, 5)
        print(f"五日均价是：{baseClass.avg_5}")

        baseClass.avg_10 = CalculationUtil.GetAvg(baseClass, 10)
        print(f"十日均价是：{baseClass.avg_10}")


        baseClass.avg_20 = CalculationUtil.GetAvg(baseClass, 20)
        print(f"二十日均价是：{baseClass.avg_20}")

        baseClass.avg_40 = CalculationUtil.GetAvg(baseClass, 40)
        print(f"四十日均价是：{baseClass.avg_40}")

        baseClass.avg_60 = CalculationUtil.GetAvg(baseClass, 60)
        print(f"六十日均价是：{baseClass.avg_60}")

        baseClass.avg_120 = CalculationUtil.GetAvg(baseClass, 120)
        print(f"一百二十日均价是：{baseClass.avg_120}")


        baseClass.avg_240 = CalculationUtil.GetAvg(baseClass, 240)
        print(f"两百四十日均价是：{baseClass.avg_240}")


        baseClass.avg_ratio_5 = baseClass.avg / baseClass.avg_5
        print(f"当日均价与五日均价的比是：{baseClass.avg_ratio_5}")

        baseClass.avg_ratio_10 = baseClass.avg / baseClass.avg_10
        print(f"当日均价与十日均价的比是：{baseClass.avg_ratio_10}")


        baseClass.avg_ratio_20 = baseClass.avg / baseClass.avg_20
        print(f"当日均价与二十日均价的比是：{baseClass.avg_ratio_20}")

        baseClass.avg_ratio_40 = baseClass.avg / baseClass.avg_40
        print(f"当日均价与四十日均价的比是：{baseClass.avg_ratio_40}")

        baseClass.avg_ratio_60 = baseClass.avg / baseClass.avg_60
        print(f"当日均价与六十日均价的比是：{baseClass.avg_ratio_60}")

        baseClass.avg_ratio_120 = baseClass.avg / baseClass.avg_120
        print(f"当日均价与一百二十日均价的比是：{baseClass.avg_ratio_120}")
        #avg_ratio_240:float           #240日均价
        baseClass.avg_ratio_240 = baseClass.avg / baseClass.avg_240
        print(f"当日均价与两百四十日均价的比是：{baseClass.avg_ratio_240}")
        
        
        ##这下面还有行业相关的排名数据没有写
        baseClass.volume_industry_rank = CalculationUtil.GetIndustry_Rank_Volume(baseClass, self)
        print(f"成交量排名是：{baseClass.volume_industry_rank}")

        baseClass.total_price_industry_rank = CalculationUtil.GetIndustry_Rank_Volume_Price(baseClass, self)
        print(f"成交额排名是：{baseClass.total_price_industry_rank}")

        baseClass.total_price_ratio_industry_rank = CalculationUtil.GetIndustry_Rank_Price_Ratio(baseClass, self)
        print(f"成交额涨跌幅排名是：{baseClass.total_price_ratio_industry_rank}")

        #:float #成交量涨跌幅排名(前%)
        baseClass.volume_ratio_industry_rank = CalculationUtil.GetIndustry_Rank_Volume_Ratio(baseClass, self)
        print(f"成交量涨跌幅排名是：{baseClass.volume_ratio_industry_rank}")


        #ratio_industry_rank:float#涨跌幅排名(前%)
        baseClass.ratio_industry_rank = CalculationUtil.GetIndustry_Rank_Ratio(baseClass, self)
        print(f"涨跌幅排名是：{baseClass.ratio_industry_rank}")


        #amplitude_industry_rank:float#振幅排名(前%)
        baseClass.amplitude_industry_rank = CalculationUtil.GetIndustry_Rank_Amplitude(baseClass, self)
        print(f"振幅排名是：{baseClass.amplitude_industry_rank}")

        baseClass.turn_industry_rank = CalculationUtil.GetIndustry_Rank_Turn(baseClass, self)
        print(f"换手率涨排名是：{baseClass.turn_industry_rank}")
        

        #turn_ratio_industry_rank:float#换手率涨跌幅排名(前%)
        baseClass.turn_ratio_industry_rank = CalculationUtil.GetIndustry_Rank_Turn_Ratio(baseClass, self)
        print(f"换手率涨跌幅排名是：{baseClass.turn_ratio_industry_rank}")


        #avg_industry_rank:float#均价涨跌幅排名(前%)
        baseClass.avg_industry_rank = CalculationUtil.GetIndustry_Rank_Avg_Ratio(baseClass, self)
        print(f"均价涨跌幅排名是：{baseClass.avg_industry_rank}")

        volumeState_1 = CalculationUtil.GetVolumeState(baseClass, 1)
        volumeState_3 = CalculationUtil.GetVolumeState(baseClass, 3)
        volumeState_5 = CalculationUtil.GetVolumeState(baseClass, 5)
        volumeState_10 = CalculationUtil.GetVolumeState(baseClass, 10)

        priceState_1 = CalculationUtil.GetRatioState(baseClass, 1)
        priceState_3 = CalculationUtil.GetRatioState(baseClass, 3)
        priceState_5 = CalculationUtil.GetRatioState(baseClass, 5)
        priceState_10 = CalculationUtil.GetRatioState(baseClass, 10)

        amplitudeState_1 = CalculationUtil.GetAmplitudeState(baseClass, 1)
        amplitudeState_3 = CalculationUtil.GetAmplitudeState(baseClass, 3)
        amplitudeState_5 = CalculationUtil.GetAmplitudeState(baseClass, 5)
        amplitudeState_10 = CalculationUtil.GetAmplitudeState(baseClass, 10)
        ##快捷指标

        #is_up_up:float#是否放量增长(>或小于1)
        baseClass.is_up_up = 1 if volumeState_1 == 1 and priceState_1 == 1 else 0
        print(f"放量增长状态：{baseClass.is_up_up}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_low_up:float#是否缩量增长
        baseClass.is_low_up = 1 if volumeState_1 == -1 and priceState_1 == 1 else 0
        print(f"缩量增长状态：{baseClass.is_low_up}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_up_low:float#是否放量降低
        baseClass.is_up_low = 1 if volumeState_1 == 1 and priceState_1 == -1 else 0
        print(f"放量降低状态：{baseClass.is_up_low}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_low_low:float#是否缩量降低
        baseClass.is_low_low = 1 if volumeState_1 == -1 and priceState_1 == -1 else 0
        print(f"缩量降低状态：{baseClass.is_low_low}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_up_mid:float#是否放量横盘
        baseClass.is_up_mid = 1 if volumeState_1 == 1 and priceState_1 == 0 else 0
        print(f"放量横盘状态：{baseClass.is_up_mid}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_low_mid:float#是否缩量横盘
        baseClass.is_low_mid = 1 if volumeState_1 == -1 and priceState_1 == 0 else 0
        print(f"缩量横盘状态：{baseClass.is_low_mid}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_mid_up:float#是否平量增长
        baseClass.is_mid_up = 1 if volumeState_1 == 0 and priceState_1 == 1 else 0
        print(f"平量增长状态：{baseClass.is_mid_up}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")
        #is_mid_low:float#是否平量降低
        baseClass.is_mid_low = 1 if volumeState_1 == 0 and priceState_1 == -1 else 0
        print(f"平量降低状态：{baseClass.is_mid_low}， volumeState_1：{volumeState_1}， priceState_1：{priceState_1}")


        #is_up_up_3:float#是否3日放量增长
        baseClass.is_up_up_3 = 1 if volumeState_3 == 1 and priceState_3 == 1 else 0
        print(f"3日放量增长状态：{baseClass.is_up_up_3}")

        #is_low_up_3:float#是否3日缩量增长
        baseClass.is_low_up_3 = 1 if volumeState_3 == -1 and priceState_3 == 1 else 0
        print(f"3日缩量增长状态：{baseClass.is_low_up_3}")

        #is_up_low_3:float#是否3日放量降低
        baseClass.is_up_low_3 = 1 if volumeState_3 == 1 and priceState_3 == -1 else 0
        print(f"3日放量降低状态：{baseClass.is_up_low_3}, volumeState_3：{volumeState_3}， priceState_3：{priceState_3}")

        #is_low_low_3:float#是否3日缩量降低
        baseClass.is_low_low_3 = 1 if volumeState_3 == -1 and priceState_3 == -1 else 0
        print(f"3日缩量降低状态：{baseClass.is_low_low_3}")

        #is_up_mid_3:float#是否3日放量横盘
        baseClass.is_up_mid_3 = 1 if volumeState_3 == 1 and priceState_3 == 0 else 0
        print(f"3日放量横盘状态：{baseClass.is_up_mid_3}, volumeState_3：{volumeState_3}， priceState_3：{priceState_3}")

        #is_low_mid_3:float#是否3日缩量横盘
        baseClass.is_low_mid_3 = 1 if volumeState_3 == -1 and priceState_3 == 0 else 0
        print(f"3日缩量横盘状态：{baseClass.is_low_mid_3}, volumeState_3：{volumeState_3}， priceState_3：{priceState_3}")

        #is_mid_up_3:float#是否3日平量增长
        baseClass.is_mid_up_3 = 1 if volumeState_3 == 0 and priceState_3 == 1 else 0
        print(f"3日平量增长状态：{baseClass.is_mid_up_3}, volumeState_3：{volumeState_3}， priceState_3：{priceState_3}")

        #is_mid_low_3:float#是否3日平量降低
        baseClass.is_mid_low_3 = 1 if volumeState_3 == 0 and priceState_3 == -1 else 0
        print(f"3日平量降低状态：{baseClass.is_mid_low_3}, volumeState_3：{volumeState_3}， priceState_3：{priceState_3}")




        #is_up_up_5:float#是否5日放量增长
        baseClass.is_up_up_5 = 1 if volumeState_5 == 1 and priceState_5 == 1 else 0
        print(f"5日放量增长状态：{baseClass.is_up_up_5}")

        #is_low_up_5:float#是否5日缩量增长
        baseClass.is_low_up_5 = 1 if volumeState_5 == -1 and priceState_5 == 1 else 0
        print(f"5日缩量增长状态：{baseClass.is_low_up_5}")

        #is_up_low_5:float#是否5日放量降低
        baseClass.is_up_low_5 = 1 if volumeState_5 == 1 and priceState_5 == -1 else 0
        print(f"5日放量降低状态：{baseClass.is_up_low_5}, volumeState_5：{volumeState_5}， priceState_5：{priceState_5}")

        #is_low_low_5:float#是否5日缩量降低
        baseClass.is_low_low_5 = 1 if volumeState_5 == -1 and priceState_5 == -1 else 0
        print(f"5日缩量降低状态：{baseClass.is_low_low_5}")

        #is_up_mid_5:float#是否5日放量横盘
        baseClass.is_up_mid_5 = 1 if volumeState_5 == 1 and priceState_5 == 0 else 0
        print(f"5日放量横盘状态：{baseClass.is_up_mid_5}, volumeState_5：{volumeState_5}， priceState_5：{priceState_5}")

        #is_low_mid_5:float#是否5日缩量横盘
        baseClass.is_low_mid_5 = 1 if volumeState_5 == -1 and priceState_5 == 0 else 0
        print(f"5日缩量横盘状态：{baseClass.is_low_mid_5}, volumeState_5：{volumeState_5}， priceState_5：{priceState_5}")

        #is_mid_up_5:float#是否5日平量增长
        baseClass.is_mid_up_5 = 1 if volumeState_5 == 0 and priceState_5 == 1 else 0
        print(f"5日平量增长状态：{baseClass.is_mid_up_5}, volumeState_5：{volumeState_5}， priceState_5：{priceState_5}")

        #is_mid_low_5:float#是否5日平量降低
        baseClass.is_mid_low_5 = 1 if volumeState_5 == 0 and priceState_5 == -1 else 0
        print(f"5日平量降低状态：{baseClass.is_mid_low_5}, volumeState_5：{volumeState_5}， priceState_5：{priceState_5}")


        #is_up_up_10:float#是否10日放量增长
        baseClass.is_up_up_10 = 1 if volumeState_10 == 1 and priceState_10 == 1 else 0
        print(f"10日放量增长状态：{baseClass.is_up_up_10}")

        #is_low_up_10:float#是否10日缩量增长
        baseClass.is_low_up_10 = 1 if volumeState_10 == -1 and priceState_10 == 1 else 0
        print(f"10日缩量增长状态：{baseClass.is_low_up_10}")

        #is_up_low_10:float#是否10日放量降低
        baseClass.is_up_low_10 = 1 if volumeState_10 == 1 and priceState_10 == -1 else 0
        print(f"10日放量降低状态：{baseClass.is_up_low_10}, volumeState_10：{volumeState_10}， priceState_10：{priceState_10}")

        #is_low_low_10:float#是否10日缩量降低
        baseClass.is_low_low_10 = 1 if volumeState_10 == -1 and priceState_10 == -1 else 0
        print(f"10日缩量降低状态：{baseClass.is_low_low_10}")

        #is_up_mid_10:float#是否10日放量横盘
        baseClass.is_up_mid_10 = 1 if volumeState_10 == 1 and priceState_10 == 0 else 0
        print(f"10日放量横盘状态：{baseClass.is_up_mid_10}, volumeState_10：{volumeState_10}， priceState_10：{priceState_10}")

        #is_low_mid_10:float#是否10日缩量横盘
        baseClass.is_low_mid_10 = 1 if volumeState_10 == -1 and priceState_10 == 0 else 0
        print(f"10日缩量横盘状态：{baseClass.is_low_mid_10}, volumeState_10：{volumeState_10}， priceState_10：{priceState_10}")

        #is_mid_up_10:float#是否10日平量增长
        baseClass.is_mid_up_10 = 1 if volumeState_10 == 0 and priceState_10 == 1 else 0
        print(f"10日平量增长状态：{baseClass.is_mid_up_10}, volumeState_10：{volumeState_10}， priceState_10：{priceState_10}")

        #is_mid_low_10:float#是否10日平量降低
        baseClass.is_mid_low_10 = 1 if volumeState_10 == 0 and priceState_10 == -1 else 0
        print(f"10日平量降低状态：{baseClass.is_mid_low_10}, volumeState_10：{volumeState_10}， priceState_10：{priceState_10}")


#   is_pop_up:float#是否震荡上行
        baseClass.is_pop_up = 1 if amplitudeState_1 == 1 and priceState_1 == 1 else 0
        print(f"当日震荡上行状态：{baseClass.is_pop_up}， amplitudeState_1：{amplitudeState_1}， priceState_1：{priceState_1}")
#    is_pop_down:float#是否震荡下行
        baseClass.is_pop_down = 1 if amplitudeState_1 == 1 and priceState_1 == -1 else 0
        print(f"当日震荡下行状态：{baseClass.is_pop_down}， amplitudeState_1：{amplitudeState_1}， priceState_1：{priceState_1}")

#    is_pop_up_3:float#是否震荡上行
        baseClass.is_pop_up_3 = 1 if amplitudeState_3 == 1 and priceState_3 == 1 else 0
        print(f"3日震荡上行状态：{baseClass.is_pop_up_3}, amplitudeState_3：{amplitudeState_3}， priceState_3：{priceState_3}")
#    is_pop_down_3:float#是否震荡下行
        baseClass.is_pop_down_3 = 1 if amplitudeState_3 == 1 and priceState_3 == -1 else 0
        print(f"3日震荡下行状态：{baseClass.is_pop_down_3}, amplitudeState_3：{amplitudeState_3}， priceState_3：{priceState_3}")

#    is_pop_up_5:float#是否震荡上行
        baseClass.is_pop_up_5 = 1 if amplitudeState_5 == 1 and priceState_5 == 1 else 0
        print(f"5日震荡上行状态：{baseClass.is_pop_up_5}, amplitudeState_5：{amplitudeState_5}， priceState_5：{priceState_5}")
#    is_pop_down_5:float#是否震荡下行
        baseClass.is_pop_down_5 = 1 if amplitudeState_5 == 1 and priceState_5 == -1 else 0
        print(f"5日震荡下行状态：{baseClass.is_pop_down_5}, amplitudeState_5：{amplitudeState_5}， priceState_5：{priceState_5}")

#    is_pop_up_10:float#是否震荡上行
        baseClass.is_pop_up_10 = 1 if amplitudeState_10 == 1 and priceState_10 == 1 else 0
        print(f"10日震荡上行状态：{baseClass.is_pop_up_10}, amplitudeState_10：{amplitudeState_10}， priceState_10：{priceState_10}")
#    is_pop_down_10:float#是否震荡下行
        baseClass.is_pop_down_10 = 1 if amplitudeState_10 == 1 and priceState_10 == -1 else 0
        print(f"10日震荡下行状态：{baseClass.is_pop_down_10}, amplitudeState_10：{amplitudeState_10}， priceState_10：{priceState_10}")


    def GetWindowDataClass(self, stockCode, startDate, toDate):
    #code:str
    #trade_date_from:date    #交易日期
    #trade_date_to:date      #交易日期
    #up_stopCount:int        #涨停次数
    #down_stopCount:int      #跌停次数
    #industry:str            #行业
    #isST:int                #1是  .0否

    
    #volume:float   #整体成交量
    #volume_price:float   #整体成交额
    #volume_ratio:float   #整体成交量涨跌幅
    #volume_price_ratio:float   #整体成交额涨跌幅
    #turn_ratio:float          #整体换手率涨跌幅
    #change_Ratio:float      #整体涨跌幅
    #avg_Ratio:float      #均价涨跌幅
    #volume_price_energy:float    #整体资金成交动量，正数越大向上推动越大，负数越小向下抛压越大


    #avg_open: float         #平均开盘价
    #avg_close: float            #平均收盘价
    #avg_last_close: float       #平均昨收价
    #avg_high: float         #平均最高价
    #avg_low: float          #平均最低价
    #avg_volume: float        #平均成交量
    #avg_volume_price: Optional[float] = None        #平均成交额
    #avg_volume_rito:float       #平均量比 
    #avg_turn: float             #平均换手率
    #avg_change_Ratio:float      #平均涨跌幅
    #avg_amplitude:float         #平均振幅
    #avg_avg:float         #平均均价

    #min_open: float         #最低开盘价
    #min_close: float            #最低收盘价
    #min_last_close: float       #最低昨收价
    #min_high: float         #最低最高价
    #min_low: float          #最低最低价
    #min_volume: float        #最低成交量
    #min_volume_price: Optional[float] = None        #最低成交额
    #min_volume_rito:float       #最低量比 
    #min_turn: float             #最低换手率
    #min_change_Ratio:float      #最低涨跌幅
    #min_amplitude:float         #最低振幅
    #min_avg:float         #最低均价

    #max_open: float         #最高开盘价
    #max_close: float            #最高收盘价
    #max_last_close: float       #最高昨收价
    #max_high: float         #最高最高价
    #max_low: float          #最高最低价
    #max_volume: float        #最高成交量
    #max_volume_price: Optional[float] = None        #最高成交额
    #max_volume_rito:float       #最高量比 
    #max_turn: float             #最高换手率
    #max_change_Ratio:float      #最高涨跌幅
    #max_amplitude:float         #最高振幅
    #max_avg:float         #最高均价

    #decrease_price:float  #这段时间的跌价总和
    #increase_price:float  #这段时间的涨价总和
    
    
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


    #is_pop_up:float#是否震荡上行
    #is_pop_down:float#是否震荡下行



        pass

    def GetIndustryBaseData(self, industryStr):
        pass

    def GetIndustryWindowData(self, industryStr, startDate, toDate):
        pass










    #获取前X天的股票的交易日期
    def GetLastTradeDateList(self, code, dateStr, num):
        dayList = []
        dt = datetime.strptime(dateStr, "%Y%m%d")
        end_dt = datetime.strptime(Const.first_Data, "%Y%m%d")
        while len(dayList) < num and dt > end_dt:
            dt -= timedelta(days=1)  # 往前一天
            date_str = dt.strftime("%Y%m%d")
            dailyData:CalculationDataStruct.StructBaseClass = self.GetBaseDataClass(code, date_str)
            if(dailyData != None and dailyData.trade_state == 1):
                dayList.append(date_str)
        return dayList


    #获取前X天的交易数据
    def GetLastDateDataByNum(self, code ,startDate, dayNum):
        dateList = self.GetLastTradeDateList(code, startDate, dayNum)
        dataList = []
        count = 0
        for val in dateList:
            dailyData = self.GetBaseDataClass(code, dateList[count])
            dataList.append(dailyData)
            count = count + 1
            if(count > dayNum):
                break
        return dataList