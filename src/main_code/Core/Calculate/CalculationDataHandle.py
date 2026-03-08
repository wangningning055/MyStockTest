from datetime import date, datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core import Main
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core import Const
import time
from functools import partial
import psutil
import os
import bisect
class BaseClass :
    def __init__(self):
        pass
    def Init(self, main):
        self.main :Main.processor = main
        self.totalStockList = []
        self.totalComponyIns : CalculationDataStruct.StructIndustryTotalInfoClass = CalculationDataStruct.StructIndustryTotalInfoClass()
        self.totalBaseDailyData : Dict[(str, str), CalculationDataStruct.StructBaseClass] = {}
        self.totalBaseWindowData : Dict[str, CalculationDataStruct.StructBaseWindowClass]  = {}
        self.totalAdjustData = {}
        self.InitIndustry()
        self.InitCalculateBaseAttrByDic()
        self.InitCalculateBaseWindowAttrByDic()
        self.totalDateList = self.InitDateList()
        print(self.totalDateList)

        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)

        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小
        t0 = time.perf_counter()

        print(f"开始获取整个数据 ")
        print(f"开始获取整个数据 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")


        self.totalDbList = self.main.dbHandler.GetDailyRowByCodeListAndDateList(self.totalStockList, self.totalDateList)



        print("开始整理复权数据：")



        self.totalAdjustData = self.main.dbHandler.LoadAllAdjustDataToDict()




        print(f"复权数据整理完毕")

        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小


        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"整个数据获取完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 花费时间：{totalCostTimeStr1}")
        print(f"整个数据获取完毕 ")




        print(f"开计算数据 ")
        print(f"开计算数据 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
        t0 = time.perf_counter()



        todayStr = self.GetToday()
        self.InitAllBaseDataClsList(240, todayStr)



        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"数据计算完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 这个阶段花费时间：{totalCostTimeStr1}")



        todayStr = self.GetToday()
        t0 = time.perf_counter()
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小
        print(f"开始计算测试数据：{todayStr} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")



        #cls = self.totalBaseDailyData[("300846.SZ", todayStr)]
        #self.CalculateBaseClass(cls)
        windowCls = self.GetWindowDataClass("300846.SZ", todayStr, 0, 5)
        self.CalculateBaseWindowClass(windowCls, windowCls.code, 0, 5)

        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小

        print(f"测试数据计算完毕{todayStr}, 花费的时间是：{totalCostTimeStr1} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")


    def InitIndustry(self):
        df = self.main.dbHandler.GetAllBasicData()
        temBasic = BasicDBStruct.DBStructClass()
        sameList = set()
        for key, val in df.items():
            code = key
            self.totalStockList.append(code)
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

    def InitIndustryCls(self):

        print(f"行业总数量为：{len(self.totalComponyIns.industryList)}")
        for key, val in self.totalComponyIns.industryList.items():
            if key == "焦炭加工":
                #self.GetIndustryBaseData("20260211", val)
                self.GetIndustryWindowData(val, "20260213", 0, 10 )


    def GetBaseDataClass(self, stockCode, date, isCalculate = False) -> CalculationDataStruct.StructBaseClass:
        #print(f"开始计算, code:{stockCode}, 名字：{componenyInfo.Name}, 行业：{componenyInfo.Industry} 日期：{date}， 计算：{isCalculate} ")
        if (stockCode, date) in self.totalBaseDailyData:
            baseClass = self.totalBaseDailyData[(stockCode, date)]
            #print(f"直接返回：{stockCode}  {date}")
            return baseClass
        else:
            #print(f"股票{stockCode},  {date}数据不存在")
            return None

    def CalculateBaseClass(self, baseClass : CalculationDataStruct.StructBaseClass):
        print(f"当日涨跌幅是{baseClass.change_Ratio}")
        print(f"当日震幅是{baseClass.amplitude}")
        print(f"5日涨跌幅是{baseClass.change_Ratio_5}")
        print(f"10日涨跌幅是{baseClass.change_Ratio_10}")
        print(f"20日涨跌幅是{baseClass.change_Ratio_20}")
        print(f"40日涨跌幅是{baseClass.change_Ratio_40}")
        print(f"60日涨跌幅是{baseClass.change_Ratio_60}")
        print(f"120日涨跌幅是{baseClass.change_Ratio_120}")
        print(f"240日涨跌幅是{baseClass.change_Ratio_240}")
        print(f"成交量涨跌幅是{baseClass.volume_ratio}")
        print(f"3日成交量涨跌幅是{baseClass.volume_ratio_3}")
        print(f"5日成交量涨跌幅是{baseClass.volume_ratio_5_percent}")
        print(f"10成交量涨跌幅是{baseClass.volume_ratio_10}")
        print(f"20成交量涨跌幅是{baseClass.volume_ratio_20}")
        print(f"40成交量涨跌幅是{baseClass.volume_ratio_40}")
        print(f"当成交额涨跌幅是{baseClass.volume_price_ratio}")
        print(f"3日平均成交额涨跌幅是{baseClass.volume_price_ratio_3}")
        print(f"5日平均成交额涨跌幅是{baseClass.volume_price_ratio_5}")
        print(f"10日平均成交额涨跌幅是{baseClass.volume_price_ratio_10}")
        print(f"20日平均成交额涨跌幅是{baseClass.volume_price_ratio_20}")
        print(f"40日平均成交额涨跌幅是{baseClass.volume_price_ratio_40}")
        print(f"量比是{baseClass.volume_ratio_5}")
        print(f"当日均价涨跌幅是：{baseClass.avg_ratio}")
        print(f"当日换手率涨跌幅是{baseClass.turn_ratio}")
        print(f"五日均价是：{baseClass.avg_5}")
        print(f"十日均价是：{baseClass.avg_10}")
        print(f"二十日均价是：{baseClass.avg_20}")
        print(f"四十日均价是：{baseClass.avg_40}")
        print(f"六十日均价是：{baseClass.avg_60}")
        print(f"一百二十日均价是：{baseClass.avg_120}")
        print(f"两百四十日均价是：{baseClass.avg_240}")
        print(f"当日均价与五日均价的比是：{baseClass.avg_ratio_5}")
        print(f"当日均价与十日均价的比是：{baseClass.avg_ratio_10}")
        print(f"当日均价与二十日均价的比是：{baseClass.avg_ratio_20}")
        print(f"当日均价与四十日均价的比是：{baseClass.avg_ratio_40}")
        print(f"当日均价与六十日均价的比是：{baseClass.avg_ratio_60}")
        print(f"当日均价与一百二十日均价的比是：{baseClass.avg_ratio_120}")
        print(f"当日均价与两百四十日均价的比是：{baseClass.avg_ratio_240}")

        print(f"流通市值排名是：{baseClass.total_value_ratio}%")
        print(f"市盈率排名是：{baseClass.earn_ratio}%")
        print(f"市净率排名是：{baseClass.clean_ratio}%")
        print(f"市现率排名是：{baseClass.cash_ratio}%")
        print(f"市销率排名是：{baseClass.sale_ratio}%")
        print(f"成交量排名是：{baseClass.volume_industry_rank}")
        print(f"成交额排名是：{baseClass.total_price_industry_rank}")
        print(f"成交额涨跌幅排名是：{baseClass.total_price_ratio_industry_rank}")
        print(f"成交量涨跌幅排名是：{baseClass.volume_ratio_industry_rank}")
        print(f"涨跌幅排名是：{baseClass.ratio_industry_rank}")
        print(f"振幅排名是：{baseClass.amplitude_industry_rank}")
        print(f"换手率涨排名是：{baseClass.turn_industry_rank}")
        print(f"换手率涨跌幅排名是：{baseClass.turn_ratio_industry_rank}")
        print(f"均价涨跌幅排名是：{baseClass.avg_industry_rank}")
        print(f"当日量状态：{baseClass.volumeState_1}")
        print(f"3日量状态：{baseClass.volumeState_3}")
        print(f"5日量状态：{baseClass.volumeState_5}")
        print(f"10日量状态：{baseClass.volumeState_10}")
        print(f"当日价状态：{baseClass.priceState_1}")
        print(f"3日价状态：{baseClass.priceState_3}")
        print(f"5日价状态：{baseClass.priceState_5}")
        print(f"10日价状态：{baseClass.priceState_10}")
        print(f"当日振幅状态：{baseClass.amplitudeState_1}")
        print(f"3日振幅状态：{baseClass.amplitudeState_3}")
        print(f"5日振幅状态：{baseClass.amplitudeState_5}")
        print(f"10日振幅状态：{baseClass.amplitudeState_10}")
        print(f"放量增长状态：{baseClass.is_up_up}")
        print(f"缩量增长状态：{baseClass.is_low_up}")
        print(f"放量降低状态：{baseClass.is_up_low}")
        print(f"缩量降低状态：{baseClass.is_low_low}")
        print(f"放量横盘状态：{baseClass.is_up_mid}")
        print(f"缩量横盘状态：{baseClass.is_low_mid}")
        print(f"平量增长状态：{baseClass.is_mid_up}")
        print(f"平量降低状态：{baseClass.is_mid_low}")
        print(f"3日放量增长状态：{baseClass.is_up_up_3}")
        print(f"3日缩量增长状态：{baseClass.is_low_up_3}")
        print(f"3日放量降低状态：{baseClass.is_up_low_3}")
        print(f"3日缩量降低状态：{baseClass.is_low_low_3}")
        print(f"3日放量横盘状态：{baseClass.is_up_mid_3}")
        print(f"3日缩量横盘状态：{baseClass.is_low_mid_3}")
        print(f"3日平量增长状态：{baseClass.is_mid_up_3}")
        print(f"3日平量降低状态：{baseClass.is_mid_low_3}")
        print(f"5日放量增长状态：{baseClass.is_up_up_5}")
        print(f"5日缩量增长状态：{baseClass.is_low_up_5}")
        print(f"5日放量降低状态：{baseClass.is_up_low_5}")
        print(f"5日缩量降低状态：{baseClass.is_low_low_5}")
        print(f"5日放量横盘状态：{baseClass.is_up_mid_5}")
        print(f"5日缩量横盘状态：{baseClass.is_low_mid_5}")
        print(f"5日平量增长状态：{baseClass.is_mid_up_5}")
        print(f"5日平量降低状态：{baseClass.is_mid_low_5}")

        print(f"10日放量增长状态：{baseClass.is_up_up_10}")
        print(f"10日缩量增长状态：{baseClass.is_low_up_10}")
        print(f"10日放量降低状态：{baseClass.is_up_low_10}")
        print(f"10日缩降低状态：{baseClass.is_low_low_10}")
        print(f"10日放量横盘状态：{baseClass.is_up_mid_10}")
        print(f"10日缩量横盘状态：{baseClass.is_low_mid_10}")
        print(f"10日平量增长状态：{baseClass.is_mid_up_10}")
        print(f"10日平量降低状态：{baseClass.is_mid_low_10}")
        print(f"当日震荡上行状态：{baseClass.is_pop_up}")
        print(f"当日震荡下行状态：{baseClass.is_pop_down}")
        print(f"3日震荡上行状态：{baseClass.is_pop_up_3}")
        print(f"3日震荡下行状态：{baseClass.is_pop_down_3}")
        print(f"5日震荡上行状态：{baseClass.is_pop_up_5}")
        print(f"5日震荡下行状态：{baseClass.is_pop_down_5}")
        print(f"10日震荡上行状态：{baseClass.is_pop_up_10}")
        print(f"10日震荡下行状态：{baseClass.is_pop_down_10}")
        pass

    def GetWindowDataClass(self, stockCode, tradeDate, startDateCount, toDateCount, isJustSetRank = False):
        from src.main_code.Core.Calculate import CalculationUtil
        #print(f"尝试获取股票：{stockCode}")
        cache_key = (stockCode, tradeDate, startDateCount, toDateCount)
        res = None
        if cache_key in self.totalBaseWindowData:
            res = self.totalBaseWindowData[cache_key]
            return res


        windowsClass = CalculationDataStruct.StructBaseWindowClass()
        startDataClass = self.GetBaseDataClass(stockCode, tradeDate)
        windowsClass.Init(startDataClass, startDateCount, toDateCount, self)
        self.totalBaseWindowData[cache_key] = windowsClass
        return windowsClass

    def CalculateBaseWindowClass(self, windowsClass, stockCode, startDateCount, toDateCount):
            print(f"行业是 {windowsClass.industry}")
            print(f"{self.totalComponyIns.GetComponyInfo(stockCode).Name} 前{startDateCount}天到前{toDateCount}天 涨停次数：{windowsClass.up_stopCount}")
            print(f"{self.totalComponyIns.GetComponyInfo(stockCode).Name} 前{startDateCount}天到前{toDateCount}天 跌停次数：{windowsClass.down_stopCount}")

            print(f"整体成交量是 {windowsClass.volume}")
            print(f"整体成交额是 {windowsClass.volume_price}")
            print(f"整体成交量涨跌幅是 {windowsClass.volume_ratio}")
            print(f"整体成交额涨跌幅是 {windowsClass.volume_price_ratio}")
            print(f"整体换手率涨跌幅是 {windowsClass.turn_ratio}")
            print(f"涨跌幅是 {windowsClass.change_Ratio}")
            print(f"整体涨跌幅是 {windowsClass.change_Ratio_Total}")
            print(f"均价涨跌幅是 {windowsClass.avg_Ratio}")
            print(f"整体均价涨跌幅是 {windowsClass.avg_Ratio_Total}")
            print(f"平均开盘价是 {windowsClass.avg_open}")
            print(f"平均收盘价是 {windowsClass.avg_close}")
            print(f"平均最高价是 {windowsClass.avg_high}")
            print(f"平均最低价是 {windowsClass.avg_low}")
            print(f"平均成交量是 {windowsClass.avg_volume}")
            print(f"平均成交额是 {windowsClass.avg_volume_price}")
            print(f"平均量比是 {windowsClass.avg_volume_rito}")
            print(f"平均换手率是 {windowsClass.avg_turn}")
            print(f"平均涨跌幅是 {windowsClass.avg_change_Ratio}")
            print(f"平均振幅是 {windowsClass.avg_amplitude}")
            print(f"平均均价是 {windowsClass.avg_avg}")
            print(f"最低开盘价是 {windowsClass.min_open}")
            print(f"最低收盘价是 {windowsClass.min_close}")
            print(f"最低昨收价是 {windowsClass.min_last_close}")
            print(f"最低最高价是 {windowsClass.min_high}")
            print(f"最低最低价是 {windowsClass.min_low}")
            print(f"最低成交量是 {windowsClass.min_volume}")
            print(f"最低成交额是 {windowsClass.min_volume_price}")
            print(f"最低量比是 {windowsClass.min_volume_rito}")
            print(f"最低换手率是 {windowsClass.min_turn}")
            print(f"最低涨跌幅是 {windowsClass.min_change_Ratio}")
            print(f"最低振幅是 {windowsClass.min_amplitude}")
            print(f"最低均价是 {windowsClass.min_avg}")
            print(f"最高开盘价是 {windowsClass.max_open}")
            print(f"最高收盘价是 {windowsClass.max_close}")
            print(f"最高昨收价是 {windowsClass.max_last_close}")
            print(f"最高最高价是 {windowsClass.max_high}")
            print(f"最高最低价是 {windowsClass.max_low}")
            print(f"最高成交量是 {windowsClass.max_volume}")
            print(f"最高成交额是 {windowsClass.max_volume_price}")
            print(f"最高量比是 {windowsClass.max_volume_rito}")
            print(f"最高换手率是 {windowsClass.max_turn}")
            print(f"最高涨跌幅是 {windowsClass.max_change_Ratio}")
            print(f"最高振幅是 {windowsClass.max_amplitude}")
            print(f"最高均价是 {windowsClass.max_avg}")

            print(f"量状态：{windowsClass.volumeState}")
            print(f"价状态：{windowsClass.priceState}")
            print(f"震荡状态：{windowsClass.amplitudeState}")
            print(f"放量增长状态：{windowsClass.is_up_up}")
            print(f"缩量增长状态：{windowsClass.is_low_up}")
            print(f"放量降低状态：{windowsClass.is_up_low}")
            print(f"缩量降低状态：{windowsClass.is_low_low}")
            print(f"放量横盘状态：{windowsClass.is_up_mid}")
            print(f"缩量横盘状态：{windowsClass.is_low_mid}")
            print(f"平量增长状态：{windowsClass.is_mid_up}")
            print(f"平量降低状态：{windowsClass.is_mid_low}")
            print(f"当日震荡上行状态：{windowsClass.is_pop_up}")
            print(f"当日震荡下行状态：{windowsClass.is_pop_down}")

            if windowsClass.isCalculateRank:
                print(f"成交量行业排名是 {windowsClass.volume_industry_rank}%")
                print(f"成交额行业排名是 {windowsClass.total_price_industry_rank}%")
                print(f"成交额涨跌幅行业排名是 {windowsClass.total_price_ratio_industry_rank}%")
                print(f"成交量涨跌幅行业排名是 {windowsClass.volume_ratio_industry_rank}%")
                print(f"涨跌幅行业排名是 {windowsClass.ratio_industry_rank}%")
                print(f"振幅行业排名是 {windowsClass.amplitude_industry_rank}%")
                print(f"换手率涨跌幅行业排名是 {windowsClass.turn_ratio_industry_rank}%")
                print(f"均价行业排名是 {windowsClass.avg_industry_rank}%")

    def GetWindowDataClassTest(self, stockCode, tradeDate, startDateCount, toDateCount, isJustSetRank = False):
        from src.main_code.Core.Calculate import CalculationUtil
        #print(f"尝试获取股票：{stockCode},  isJust {isJustSetRank}")
        cache_key = (stockCode, tradeDate, startDateCount, toDateCount)
        res = None
        if cache_key in self.totalBaseWindowData:
            res = self.totalBaseWindowData[cache_key]
            if res.isCalculateRank and res.isCalculateOther:
                return res
        startDataClass = self.GetBaseDataClass(stockCode, tradeDate, True)

        windowsClass = None
        if res is not None:
            #print(f"已有缓存")
            windowsClass = res
        else:
            #print("建一个新的")
            windowsClass = CalculationDataStruct.StructBaseWindowClass()
            self.totalBaseWindowData[cache_key] = windowsClass




        #code:str
        windowsClass.code = stockCode
        windowsClass.startCount = startDateCount
        windowsClass.toCount = toDateCount
        windowsClass.trade_date_from = tradeDate
        #industry:str            #行业
        windowsClass.industry = self.totalComponyIns.GetComponyInfo(stockCode).Industry

        if isJustSetRank:
            #print("只计算行业，直接返回")
            return windowsClass

        if not windowsClass.isCalculateOther:
            #print("计算他的基本数据")
            t0 = time.perf_counter()


            #up_stopCount:int        #涨停次数
            windowsClass.up_stopCount = CalculationUtil.GetUpStopCount(startDataClass, startDateCount, toDateCount)


            #down_stopCount:int      #跌停次数
            windowsClass.down_stopCount = CalculationUtil.GetDownStopCount(startDataClass, startDateCount, toDateCount)
            


            #isST:int                #1是  .0否
            windowsClass.isST = startDataClass.isST
            
            #volume:float   #整体成交量
            windowsClass.volume = CalculationUtil.GetVolume_Window(startDataClass, startDateCount, toDateCount)

            #volume_price:float   #整体成交额
            windowsClass.volume_price = CalculationUtil.GetVolume_Price_Window(startDataClass, startDateCount, toDateCount)


            #volume_ratio:float   #整体成交量涨跌幅
            windowsClass.volume_ratio = CalculationUtil.GetVolume_Ratio_Window(startDataClass, startDateCount, toDateCount)

            #volume_price_ratio:float   #整体成交额涨跌幅
            windowsClass.volume_price_ratio = CalculationUtil.GetVolume_Price_Ratio_Window(startDataClass, startDateCount, toDateCount)

            #turn_ratio:float          #整体换手率涨跌幅
            windowsClass.turn_ratio = CalculationUtil.GetTurn_Ratio_Window(startDataClass, startDateCount, toDateCount)

            #change_Ratio:float      #整体涨跌幅
            windowsClass.change_Ratio = CalculationUtil.GetChange_Ratio_Window(startDataClass, startDateCount, toDateCount)

            #change_Ratio_Total:float      #整体涨跌幅
            windowsClass.change_Ratio_Total = CalculationUtil.GetChange_Ratio_Total_Window(startDataClass, startDateCount, toDateCount)

            #avg_Ratio:float      #均价涨跌幅
            windowsClass.avg_Ratio = CalculationUtil.GetAvg_Ratio_Window(startDataClass, startDateCount, toDateCount)

            #avg_Ratio_Total:float      #整体均价涨跌幅
            windowsClass.avg_Ratio_Total = CalculationUtil.GetAvg_Ratio_Total_Window(startDataClass, startDateCount, toDateCount)


            #avg_open: float         #平均开盘价
            windowsClass.avg_open = CalculationUtil.GetOpen_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_close: float            #平均收盘价
            windowsClass.avg_close = CalculationUtil.GetClose_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_high: float         #平均最高价
            windowsClass.avg_high = CalculationUtil.GetHigh_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_low: float          #平均最低价
            windowsClass.avg_low = CalculationUtil.GetLow_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_volume: float        #平均成交量
            windowsClass.avg_volume = CalculationUtil.GetVolume_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_volume_price: Optional[float] = None        #平均成交额
            windowsClass.avg_volume_price = CalculationUtil.GetVolume_Price_Window_Avg(startDataClass, startDateCount, toDateCount)


            #avg_volume_rito:float       #平均量比 
            windowsClass.avg_volume_rito = CalculationUtil.Get_VolumeRatio_5_Window_Avg(startDataClass, startDateCount, toDateCount, self)
            

            #avg_turn: float             #平均换手率
            windowsClass.avg_turn = CalculationUtil.GetTurn_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_change_Ratio:float      #平均涨跌幅
            windowsClass.avg_change_Ratio = CalculationUtil.GetChangeRatio_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_amplitude:float         #平均振幅
            windowsClass.avg_amplitude = CalculationUtil.GetAmplitude_Window_Avg(startDataClass, startDateCount, toDateCount)

            #avg_avg:float         #平均均价
            windowsClass.avg_avg = CalculationUtil.GetAvg_Price_Window_Avg(startDataClass, startDateCount, toDateCount)



            #min_open: float         #最低开盘价
            windowsClass.min_open = CalculationUtil.GetOpen_Window_Low(startDataClass, startDateCount, toDateCount)
            
            #min_close: float            #最低收盘价
            windowsClass.min_close = CalculationUtil.GetClose_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_last_close: float       #最低昨收价
            windowsClass.min_last_close = CalculationUtil.GetLastClose_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_high: float         #最低最高价
            windowsClass.min_high = CalculationUtil.GetHigh_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_low: float          #最低最低价
            windowsClass.min_low = CalculationUtil.GetLow_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_volume: float        #最低成交量
            windowsClass.min_volume = CalculationUtil.GetVolume_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_volume_price: Optional[float] = None        #最低成交额
            windowsClass.min_volume_price = CalculationUtil.GetVolume_Price_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_volume_rito:float       #最低量比 
            windowsClass.min_volume_rito = CalculationUtil.GetVolume_Ratio_5_Window_Low(startDataClass, startDateCount, toDateCount, self)


            #min_turn: float             #最低换手率
            windowsClass.min_turn = CalculationUtil.GetTurn_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_change_Ratio:float      #最低涨跌幅
            windowsClass.min_change_Ratio = CalculationUtil.GetChange_Ratio_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_amplitude:float         #最低振幅
            windowsClass.min_amplitude = CalculationUtil.GetAmplitude_Window_Low(startDataClass, startDateCount, toDateCount)

            #min_avg:float         #最低均价
            windowsClass.min_avg = CalculationUtil.GetAvg_Window_Low(startDataClass, startDateCount, toDateCount)
            

            #max_open: float         #最高开盘价
            windowsClass.max_open = CalculationUtil.GetOpen_Window_High(startDataClass, startDateCount, toDateCount)

            #max_close: float            #最高收盘价
            windowsClass.max_close = CalculationUtil.GetClose_Window_High(startDataClass, startDateCount, toDateCount)

            #max_last_close: float       #最高昨收价
            windowsClass.max_last_close = CalculationUtil.GetLastClose_Window_High(startDataClass, startDateCount, toDateCount)


            #max_high: float         #最高最高价
            windowsClass.max_high = CalculationUtil.GetHigh_Window_High(startDataClass, startDateCount, toDateCount)


            
            #max_low: float          #最高最低价
            windowsClass.max_low = CalculationUtil.GetLow_Window_High(startDataClass, startDateCount, toDateCount)


            #max_volume: float        #最高成交量
            windowsClass.max_volume = CalculationUtil.GetVolume_Window_High(startDataClass, startDateCount, toDateCount)


            #max_volume_price: Optional[float] = None        #最高成交额
            windowsClass.max_volume_price = CalculationUtil.GetVolume_Price_Window_High(startDataClass, startDateCount, toDateCount)


            #max_volume_rito:float       #最高量比 
            windowsClass.max_volume_rito = CalculationUtil.GetVolume_Ratio_5_Window_High(startDataClass, startDateCount, toDateCount, self)

            #max_turn: float             #最高换手率
            windowsClass.max_turn = CalculationUtil.GetTurn_Window_High(startDataClass, startDateCount, toDateCount)


            #max_change_Ratio:float      #最高涨跌幅
            windowsClass.max_change_Ratio = CalculationUtil.GetChange_Ratio_Window_High(startDataClass, startDateCount, toDateCount)


            #max_amplitude:float         #最高振幅
            windowsClass.max_amplitude = CalculationUtil.GetAmplitude_Window_High(startDataClass, startDateCount, toDateCount)


            #max_avg:float         #最高均价
            windowsClass.max_avg = CalculationUtil.GetAvg_Window_High(startDataClass, startDateCount, toDateCount)



            volumeState_1 = CalculationUtil.GetVolume_State_Windows(windowsClass)
            priceState_1 = CalculationUtil.GetChange_Ratio_State_Windows(windowsClass)
            amplitudeState_1 = CalculationUtil.GetAmplitude_State_Windows(windowsClass)

            #is_up_up:float#是否放量增长(>或小于1)
            windowsClass.is_up_up = 1 if volumeState_1 == 1 and priceState_1 == 1 else 0
            #is_low_up:float#是否缩量增长
            windowsClass.is_low_up = 1 if volumeState_1 == -1 and priceState_1 == 1 else 0
            #is_up_low:float#是否放量降低
            windowsClass.is_up_low = 1 if volumeState_1 == 1 and priceState_1 == -1 else 0
            #is_low_low:float#是否缩量降低
            windowsClass.is_low_low = 1 if volumeState_1 == -1 and priceState_1 == -1 else 0
            #is_up_mid:float#是否放量横盘
            windowsClass.is_up_mid = 1 if volumeState_1 == 1 and priceState_1 == 0 else 0
            #is_low_mid:float#是否缩量横盘
            windowsClass.is_low_mid = 1 if volumeState_1 == -1 and priceState_1 == 0 else 0
            #is_mid_up:float#是否平量增长
            windowsClass.is_mid_up = 1 if volumeState_1 == 0 and priceState_1 == 1 else 0
            #is_mid_low:float#是否平量降低
            windowsClass.is_mid_low = 1 if volumeState_1 == 0 and priceState_1 == -1 else 0
            windowsClass.is_pop_up = 1 if amplitudeState_1 == 1 and priceState_1 == 1 else 0
            windowsClass.is_pop_down = 1 if amplitudeState_1 == 1 and priceState_1 == -1 else 0
            windowsClass.isCalculateOther = True
            #print("他的基本数据算完了")
            t1 = time.perf_counter()
            totalCostTime = (t1 - t0)
            totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        if not windowsClass.isCalculateRank:
            #print("计算他的排名数据")
            t0 = time.perf_counter()


            #volume_industry_rank:float #成交量排名(前%)
            windowsClass.volume_industry_rank = CalculationUtil.GetVolume_Window_Rank(startDataClass, startDateCount, toDateCount, self)


            #total_price_industry_rank:float #成交额排名(前%)
            windowsClass.total_price_industry_rank = CalculationUtil.GetVolume_Price_Window_Rank(startDataClass, startDateCount, toDateCount, self)


            #total_price_ratio_industry_rank:float#成交额涨跌幅排名(前%)
            windowsClass.total_price_ratio_industry_rank = CalculationUtil.GetVolume_Price_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)

            #volume_ratio_industry_rank:float #成交量涨跌幅排名(前%)
            windowsClass.volume_ratio_industry_rank = CalculationUtil.GetVolume_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)

            #ratio_industry_rank:float#涨跌幅排名(前%)
            windowsClass.ratio_industry_rank = CalculationUtil.GetChange_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)


            #amplitude_industry_rank:float#振幅排名(前%)
            windowsClass.amplitude_industry_rank = CalculationUtil.GetAmplitude_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)

            #turn_ratio_industry_rank:float#换手率涨跌幅排名(前%)
            windowsClass.turn_ratio_industry_rank = CalculationUtil.GetTurn_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)

            #avg_industry_rank:float#均价涨跌幅排名(前%)
            windowsClass.avg_industry_rank = CalculationUtil.GetAvg_Ratio_Window_Rank(startDataClass, startDateCount, toDateCount, self)
            industryCls = self.totalComponyIns.GetIndustryClsByCode(windowsClass.code)

            industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
            for key, val in industryCls.stockList.items():
                dailyCls = self.GetBaseDataClass(val.Code, tradeDate, False)
                industryDailyList.append(dailyCls)

            for val in industryDailyList:
                temp = self.GetWindowDataClass(val.code, tradeDate, startDateCount, toDateCount, True)
                temp.isCalculateRank = True

            t1 = time.perf_counter()
            totalCostTime = (t1 - t0)
            totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
            #print("他的排名数据算完了")



        #if windowsClass.isCalculateOther:


        #print(f"{stockCode}   计算完毕")
        return windowsClass



    def GetIndustryBaseData(self, trade_date:str, industryInfoCls:CalculationDataStruct.StructIndustryInfoClass):
        from src.main_code.Core.Calculate import CalculationUtil
        industryBaseClass = CalculationDataStruct.StructIndustryClass()

        #name:str        #行业名
        industryBaseClass.name = industryInfoCls.industryName
        print(f"行业名称是 {industryBaseClass.name}, 行业股数量是 {len(industryInfoCls.stockList)}")
        for key, val in industryInfoCls.stockList.items():
            print(f"行业名称是 {industryBaseClass.name}, key:{key}, val :{val.Name}")
            

        #trade_date:date #交易日期
        industryBaseClass.trade_date = trade_date
        print(f"交易日期是 {industryBaseClass.trade_date}")

        #volume: float   #成交量
        industryBaseClass.volume = CalculationUtil.GetIndustry_Volume(industryInfoCls, trade_date, self)
        print(f"行业整体成交量是 {industryBaseClass.volume}")

        #volume_ratio:float        #成交量涨跌幅
        industryBaseClass.volume_ratio = CalculationUtil.GetIndustry_Volume_Ratio(industryInfoCls, trade_date, 1, self)
        print(f"行业整体成交量涨跌幅是 {industryBaseClass.volume_ratio}")

        #volume_ratio_3:float        #当日成交量与3日平均成交量的比
        industryBaseClass.volume_ratio_3 = CalculationUtil.GetIndustry_Volume_Ratio(industryInfoCls, trade_date, 3, self)
        print(f"行业整体成交量3日平均比是 {industryBaseClass.volume_ratio_3}")

        #volume_ratio_5:float        #当日成交量与5日平均成交量的比
        industryBaseClass.volume_ratio_5 = CalculationUtil.GetIndustry_Volume_Ratio(industryInfoCls, trade_date, 5, self)
        print(f"行业整体成交量5日平均比是 {industryBaseClass.volume_ratio_5}")

        #volume_ratio_10:float        #当日成交量与10日平均成交量的比
        industryBaseClass.volume_ratio_10 = CalculationUtil.GetIndustry_Volume_Ratio(industryInfoCls, trade_date, 10, self)
        print(f"行业整体成交量10日平均比是 {industryBaseClass.volume_ratio_10}")

        #volume_ratio_20:float        #当日成交量与20日平均成交量的比
        industryBaseClass.volume_ratio_20 = CalculationUtil.GetIndustry_Volume_Ratio(industryInfoCls, trade_date, 20, self)
        print(f"行业整体成交量20日平均比是 {industryBaseClass.volume_ratio_20}")

        #volume_price: Optional[float] = None        #成交额
        industryBaseClass.volume_price = CalculationUtil.GetIndustry_Volume_Price(industryInfoCls, trade_date, self)
        print(f"行业整体成交额是 {industryBaseClass.volume_price}")

        #volume_price_ratio: Optional[float] = None        #成交额涨跌幅
        industryBaseClass.volume_price_ratio = CalculationUtil.GetIndustry_Volume_Price_Ratio(industryInfoCls, trade_date, 1, self)
        print(f"行业整体成交额涨跌幅是 {industryBaseClass.volume_price_ratio}")

        #volume_price_ratio_3: Optional[float] = None        #当日成交额与3日平均成交额的比
        industryBaseClass.volume_price_ratio_3 = CalculationUtil.GetIndustry_Volume_Price_Ratio(industryInfoCls, trade_date, 3, self)
        print(f"行业整体成交额3日平均比是 {industryBaseClass.volume_price_ratio_3}")

        #volume_price_ratio_5: Optional[float] = None        #当日成交额与5日平均成交额的比
        industryBaseClass.volume_price_ratio_5 = CalculationUtil.GetIndustry_Volume_Price_Ratio(industryInfoCls, trade_date, 5, self)
        print(f"行业整体成交额5日平均比是 {industryBaseClass.volume_price_ratio_5}")

        #volume_price_ratio_10: Optional[float] = None        #当日成交额与10日平均成交额的比
        industryBaseClass.volume_price_ratio_10 = CalculationUtil.GetIndustry_Volume_Price_Ratio(industryInfoCls, trade_date, 10, self)
        print(f"行业整体成交额10日平均比是 {industryBaseClass.volume_price_ratio_10}")

        #volume_price_ratio_20: Optional[float] = None        #当日成交额与20日平均成交额的比
        industryBaseClass.volume_price_ratio_20 = CalculationUtil.GetIndustry_Volume_Price_Ratio(industryInfoCls, trade_date, 20, self)
        print(f"行业整体成交额20日平均比是 {industryBaseClass.volume_price_ratio_20}")

        #change_Ratio:float      #行业整体涨跌幅
        industryBaseClass.change_Ratio = CalculationUtil.GetIndustry_Change_Ratio(industryInfoCls, trade_date, self)
        print(f"行业涨跌幅是 {industryBaseClass.change_Ratio}")

        #stockNum:int            #行业股数量
        industryBaseClass.stockNum = len(industryInfoCls.stockList)

        #stockNum_up:int         #行业上涨股数量
        industryBaseClass.stockNum_up = CalculationUtil.GetIndustry_Up_Count(industryInfoCls, trade_date, self)
        print(f"行业上涨股数量是 {industryBaseClass.stockNum_up}")

        #stockNum_up_Ratio:int         #行业上涨股比例
        industryBaseClass.stockNum_up_Ratio = (industryBaseClass.stockNum_up / industryBaseClass.stockNum) * 100 if industryBaseClass.stockNum > 0 else 0
        print(f"行业上涨股比例是 {industryBaseClass.stockNum_up_Ratio}")

        #stockNum_down:int       #行业下跌股数量
        industryBaseClass.stockNum_down = CalculationUtil.GetIndustry_Down_Count(industryInfoCls, trade_date, self)
        print(f"行业下跌股数量是 {industryBaseClass.stockNum_down}")

        #stockNum_down_Ratio:int         #行业下跌股比例
        industryBaseClass.stockNum_down_Ratio = (industryBaseClass.stockNum_down / industryBaseClass.stockNum) * 100 if industryBaseClass.stockNum > 0 else 0
        print(f"行业下跌股比例是 {industryBaseClass.stockNum_down_Ratio}")


    def GetIndustryWindowData(self, industryInfoCls:CalculationDataStruct.StructIndustryInfoClass, tradeDate, startDateCount, toDateCount):
        from src.main_code.Core.Calculate import CalculationUtil

        industryWindowClass = CalculationDataStruct.StructIndustryWindowClass()

        #name:str        #行业名
        industryWindowClass.name = industryInfoCls.industryName
        print(f"行业名称是 {industryWindowClass.name}, 行业股数量是 {len(industryInfoCls.stockList)}")
        for key, val in industryInfoCls.stockList.items():
            print(f"行业名称是 {industryWindowClass.name}, key:{key}, val :{val.Name}")

        
        #stockNum:int            #行业股数量
        industryWindowClass.stockNum = len(industryInfoCls.stockList)

        #volume: float   #整体成交量
        industryWindowClass.volume = CalculationUtil.GetIndustry_Volume_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业整体成交量是 {industryWindowClass.volume}")
        #volume_price: Optional[float] = None        #整体成交额
        industryWindowClass.volume_price = CalculationUtil.GetIndustry_Volume_Price_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业整体成交额是 {industryWindowClass.volume_price}")

        #avg_volume: float   #平均成交量
        industryWindowClass.avg_volume = CalculationUtil.GetIndustry_Volume_Avg_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业平均成交量是 {industryWindowClass.avg_volume}")

        #avg_volume_price: Optional[float] = None        #平均成交额
        industryWindowClass.avg_volume_price = CalculationUtil.GetIndustry_Volume_Price_Avg_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业平均成交额是 {industryWindowClass.avg_volume_price}")

        #volume_ratio:float        #整体成交量涨跌幅
        industryWindowClass.volume_ratio = CalculationUtil.GetIndustry_Volume_Ratio_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业整体成交量涨跌幅 {industryWindowClass.volume_ratio}")

        #volume_price_ratio: Optional[float] = None        #整体成交额涨跌幅
        industryWindowClass.volume_price_ratio = CalculationUtil.GetIndustry_Volume_Price_Ratio_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业整体成交额涨跌幅 {industryWindowClass.volume_price_ratio}")


        #change_Ratio:float      #行业涨跌幅
        industryWindowClass.change_Ratio = CalculationUtil.GetIndustry_Change_Ratio_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业涨跌幅 {industryWindowClass.change_Ratio}")

        #change_Ratio_Total:float      #整体行业涨跌幅
        industryWindowClass.change_Ratio_Total = CalculationUtil.GetIndustry_Change_Ratio_Total_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业整体涨跌幅 {industryWindowClass.change_Ratio_Total}")

        #avg_stockNum_up:int         #平均行业上涨股数量
        industryWindowClass.avg_stockNum_up = CalculationUtil.GetIndustry_Up_Stock_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业平均上涨股数量 {industryWindowClass.avg_stockNum_up}")

        #avg_stockNum_down:int       #平均行业下跌股数量
        industryWindowClass.avg_stockNum_down = CalculationUtil.GetIndustry_Down_Stock_Window(industryInfoCls, tradeDate, startDateCount, toDateCount, self)
        print(f"行业平均下跌股数量 {industryWindowClass.avg_stockNum_down}")
        
        #stockNum_up_Ratio:int         #平均行业上涨股比例
        industryWindowClass.stockNum_up_Ratio = (industryWindowClass.avg_stockNum_up / industryWindowClass.stockNum) * 100 if industryWindowClass.stockNum > 0 else 0
        print(f"行业平均上涨股比例 {industryWindowClass.stockNum_up_Ratio}")

        #stockNum_down_Ratio:int         #平均行业下跌股比例
        industryWindowClass.stockNum_down_Ratio = (industryWindowClass.avg_stockNum_down / industryWindowClass.stockNum) * 100 if industryWindowClass.stockNum > 0 else 0
        print(f"行业平均下跌股比例 {industryWindowClass.stockNum_down_Ratio}")




    #获取前X天的交易数据
    def GetLastDateDataByNum(self, cls, dayNum):
        clsList = []
        count = 0
        stopCount = 0
        targetCode = ""
        if isinstance(cls, str):
            targetCode = cls
        if isinstance(cls, CalculationDataStruct.StructBaseClass):
            targetCode = cls.code

        for day in self.totalDateList:
            cls_day = self.GetBaseDataClass(targetCode, day)
            if cls_day is None or cls_day.trade_state == 0:
                stopCount += 1
                if stopCount > 60:
                    break
                continue
            clsList.append(cls_day)
            count = count + 1
            stopCount = 0
            if count > dayNum:
                break
        return clsList
    #60 20251203   120 20250902   240 20250311

    def GetToday(self):
        last = self.main.lastDayStr
        count = 0
        for i in range(10000):
            date_format = "%Y%m%d"
            original_date = datetime.strptime(last, date_format)
            days_ago_str = last
            if(count > 0):
                # 2. 计算前1天的日期
                days_ago = original_date - timedelta(days=count)

                # 3. 转换回字符串格式（保持原格式）
                days_ago_str = days_ago.strftime(date_format)
            else:
                days_ago_str = last
            count = count + 1

            for singleStock in self.totalComponyIns.allStockList:
                res = self.main.dbHandler.GetDailyRowByCodeAndDate(singleStock, days_ago_str)
                if res is not None:
                    return days_ago_str
    def InitDateList(self):
        today = self.GetToday()
        dayList = []
        dt = datetime.strptime(today, "%Y%m%d")
        end_dt = datetime.strptime(Const.first_Data, "%Y%m%d")

        if dt.weekday() < 5:  # 0-4 代表周一到周五，5=周六，6=周日
            dayList.append(today)
        while len(dayList) < 34 and dt > end_dt:
            dt -= timedelta(days=1)  # 往前一天

            if dt.weekday() >= 5:
                continue  # 跳过周末，不加入列表
            date_str = dt.strftime("%Y%m%d")
            dayList.append(date_str)
            
        return dayList
    def InitAllBaseDataClsList(self, num, today):
        count = 0
        for date in self.totalDateList:
            for code in self.totalStockList:
                db = self.totalDbList.get((code, date))
                if db is None:
                    continue
                else:
                    if (code, date) in self.totalBaseDailyData:
                        continue
                    else:
                        baseClass = CalculationDataStruct.StructBaseClass()
                        baseClass.Init(self, code, date, db)
                        #if date == today and baseClass.trade_state == 0:
                        if code == "000001.SZ":
                            count += 1
                            #print(f"a啊啊啊啊啊啊啊啊啊啊啊啊啊载入的时间是 ：{date}, 数量：{count}")
                        self.totalBaseDailyData[(code, date)] = baseClass


    def GetLatestAdjustDataByCodeAndDate(self, code, target_date):
        """
        用二分查找快速获取指定日期或之前的最新复权数据
        时间复杂度 O(logN)，百万级数据也能瞬间查询
        """
        if code not in self.totalAdjustData:
            return {"Open_Price": 1}
        stock_data = self.totalAdjustData[code]
        dates = stock_data["dates"]
        data_dict = stock_data["data"]
        
        idx = bisect.bisect_right(dates, target_date) - 1
        
        # 没有找到≤目标日期的数据
        if idx < 0:
            return {"Open_Price": 1}
        # 获取最新的有效日期和对应数据
        latest_date = dates[idx]
        return data_dict[latest_date]

    def InitCalculateBaseAttrByDic(self):
        from src.main_code.Core.Calculate import CalculationUtil
        self.CalculateBaseAttrDic = {
            "dataList_240" :partial(self.GetLastDateDataByNum, dayNum = 240),
            # -------------------------- 振幅相关 --------------------------
            "amplitude_3": partial(CalculationUtil.GetAmplitude_Avg, num =3),
            "amplitude_5": partial(CalculationUtil.GetAmplitude_Avg, num =5),
            "amplitude_10": partial(CalculationUtil.GetAmplitude_Avg, num =10),

            # -------------------------- 涨跌幅相关 --------------------------
            "change_Ratio_3": partial(CalculationUtil.GetChange_Ratio, num =3),
            "change_Ratio_5": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 5),
            "change_Ratio_10": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 10),
            "change_Ratio_20": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 20),
            "change_Ratio_40": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 40),
            "change_Ratio_60": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 60),
            "change_Ratio_120": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 120),
            "change_Ratio_240": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 240),


            "change_Ratio_single_3": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 3),
            "change_Ratio_single_5": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 5),
            "change_Ratio_single_10": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 10),
            "change_Ratio_single_20": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 20),
            "change_Ratio_single_40": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 40),
            "change_Ratio_single_60": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 60),
            "change_Ratio_single_120": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 120),
            "change_Ratio_single_240": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 240),

            # -------------------------- 成交量相关 --------------------------
            "volume_ratio": partial(CalculationUtil.GetVolume_Ratio),
            "volume_ratio_3": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=3),
            "volume_ratio_5_percent": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=5),
            "volume_ratio_10": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=10),
            "volume_ratio_20": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=20),
            "volume_ratio_40": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=40),


            

            # -------------------------- 量价相关 --------------------------
            "volume_price_ratio": partial(CalculationUtil.GetVolume_Price, num=1),
            "volume_price_ratio_3": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=3),
            "volume_price_ratio_5": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=5),
            "volume_price_ratio_10": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=10),
            "volume_price_ratio_20": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=20),
            "volume_price_ratio_40": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=40),
            "volume_ratio_5": partial(CalculationUtil.GetVolume_5),

            
            # -------------------------- 均价/换手率相关 --------------------------
            "avg_ratio": partial(CalculationUtil.GetAvg_Ratio),
            "turn_ratio": partial(CalculationUtil.GetTurn_Ratio),

            # -------------------------- 资金成交动量 --------------------------
            "volume_price_energy": partial(CalculationUtil.GetVolume_Energy, num=1),
            "volume_price_energy_5": partial(CalculationUtil.GetVolume_Energy, num=5),
            "volume_price_energy_10": partial(CalculationUtil.GetVolume_Energy, num=10),
            "volume_price_energy_20": partial(CalculationUtil.GetVolume_Energy, num=20),
            "volume_price_energy_60": partial(CalculationUtil.GetVolume_Energy, num=60),
            "volume_price_energy_120": partial(CalculationUtil.GetVolume_Energy, num=120),
            "volume_price_energy_240": partial(CalculationUtil.GetVolume_Energy, num=240),

            # -------------------------- 均价相关 --------------------------
            "avg_5": partial(CalculationUtil.GetAvg, num=5),
            "avg_10": partial(CalculationUtil.GetAvg, num=10),
            "avg_20": partial(CalculationUtil.GetAvg, num=20),
            "avg_40": partial(CalculationUtil.GetAvg, num=40),
            "avg_60": partial(CalculationUtil.GetAvg, num=60),
            "avg_120": partial(CalculationUtil.GetAvg, num=120),
            "avg_240": partial(CalculationUtil.GetAvg, num=240),
 
            # -------------------------- 均价比率 --------------------------
            "avg_ratio_5": (lambda cls: cls.avg / cls.avg_5),
            "avg_ratio_10": (lambda cls: cls.avg / cls.avg_10),
            "avg_ratio_20": (lambda cls: cls.avg / cls.avg_20),
            "avg_ratio_40": (lambda cls: cls.avg / cls.avg_40),
            "avg_ratio_60": (lambda cls: cls.avg / cls.avg_60),
            "avg_ratio_120": (lambda cls: cls.avg / cls.avg_120),
            "avg_ratio_240": (lambda cls: cls.avg / cls.avg_240),

            # -------------------------- 行业排名相关 --------------------------
            "total_value_ratio": partial(CalculationUtil.GetIndustry_Rank_Value, handler = self),
            "earn_ratio": partial(CalculationUtil.GetIndustry_Rank_Earn, handler = self),
            "clean_ratio": partial(CalculationUtil.GetIndustry_Rank_Clean, handler = self),
            "cash_ratio": partial(CalculationUtil.GetIndustry_Rank_Cash, handler = self),
            "sale_ratio": partial(CalculationUtil.GetIndustry_Rank_Sale, handler = self),
            "volume_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume, handler = self),
            "total_price_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume_Price, handler = self),
            "total_price_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Price_Ratio, handler = self),
            "volume_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume_Ratio, handler = self),
            "ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Ratio, handler = self),
            "amplitude_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Amplitude, handler = self),
            "turn_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Turn, handler = self),
            "turn_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Turn_Ratio, handler = self),
            "avg_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Avg_Ratio, handler = self),



            # -------------------------- 基础状态 - 成交量 --------------------------
            "volumeState_1": partial(CalculationUtil.GetVolumeState, num=1),
            "volumeState_3": partial(CalculationUtil.GetVolumeState, num=3),
            "volumeState_5": partial(CalculationUtil.GetVolumeState, num=5),
            "volumeState_10": partial(CalculationUtil.GetVolumeState, num=10),
            "volumeState_20": partial(CalculationUtil.GetVolumeState, num=20),  # 新增20日
            "volumeState_40": partial(CalculationUtil.GetVolumeState, num=40),  # 新增40日
            "volumeState_60": partial(CalculationUtil.GetVolumeState, num=60),  # 新增60日
            "volumeState_120": partial(CalculationUtil.GetVolumeState, num=120),  # 新增120日
            
            # -------------------------- 基础状态 - 价格 --------------------------
            "priceState_1": partial(CalculationUtil.GetRatioState, num=1),
            "priceState_3": partial(CalculationUtil.GetRatioState, num=3),
            "priceState_5": partial(CalculationUtil.GetRatioState, num=5),
            "priceState_10": partial(CalculationUtil.GetRatioState, num=10),
            "priceState_20": partial(CalculationUtil.GetRatioState, num=20),  # 新增20日
            "priceState_40": partial(CalculationUtil.GetRatioState, num=40),  # 新增40日
            "priceState_60": partial(CalculationUtil.GetRatioState, num=60),  # 新增60日
            "priceState_120": partial(CalculationUtil.GetRatioState, num=120),  # 新增120日
            
            # -------------------------- 基础状态 - 振幅 --------------------------
            "amplitudeState_1": partial(CalculationUtil.GetAmplitudeState, num=1),
            "amplitudeState_3": partial(CalculationUtil.GetAmplitudeState, num=3),
            "amplitudeState_5": partial(CalculationUtil.GetAmplitudeState, num=5),
            "amplitudeState_10": partial(CalculationUtil.GetAmplitudeState, num=10),
            "amplitudeState_20": partial(CalculationUtil.GetAmplitudeState, num=20),  # 新增20日
            "amplitudeState_40": partial(CalculationUtil.GetAmplitudeState, num=40),  # 新增40日
            "amplitudeState_60": partial(CalculationUtil.GetAmplitudeState, num=60),  # 新增60日
            "amplitudeState_120": partial(CalculationUtil.GetAmplitudeState, num=120),  # 新增120日
            
            # -------------------------- 状态相关 - 1日 --------------------------
            "is_up_up": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == 1 else 0),
            "is_low_up": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == 1 else 0),
            "is_up_low": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == -1 else 0),
            "is_low_low": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == -1 else 0),
            "is_up_mid": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == 0 else 0),
            "is_low_mid": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == 0 else 0),
            "is_mid_up": (lambda cls: 1 if cls.volumeState_1 == 0 and cls.priceState_1 == 1 else 0),
            "is_mid_low": (lambda cls: 1 if cls.volumeState_1 == 0 and cls.priceState_1 == -1 else 0),

            # -------------------------- 状态相关 - 3日 --------------------------
            "is_up_up_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == 1 else 0),
            "is_low_up_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == 1 else 0),
            "is_up_low_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == -1 else 0),
            "is_low_low_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == -1 else 0),
            "is_up_mid_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == 0 else 0),
            "is_low_mid_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == 0 else 0),
            "is_mid_up_3": (lambda cls: 1 if cls.volumeState_3 == 0 and cls.priceState_3 == 1 else 0),
            "is_mid_low_3": (lambda cls: 1 if cls.volumeState_3 == 0 and cls.priceState_3 == -1 else 0),

            # -------------------------- 状态相关 - 5日 --------------------------
            "is_up_up_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == 1 else 0),
            "is_low_up_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == 1 else 0),
            "is_up_low_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == -1 else 0),
            "is_low_low_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == -1 else 0),
            "is_up_mid_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == 0 else 0),
            "is_low_mid_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == 0 else 0),
            "is_mid_up_5": (lambda cls: 1 if cls.volumeState_5 == 0 and cls.priceState_5 == 1 else 0),
            "is_mid_low_5": (lambda cls: 1 if cls.volumeState_5 == 0 and cls.priceState_5 == -1 else 0),

            # -------------------------- 状态相关 - 10日 --------------------------
            "is_up_up_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == 1 else 0),
            "is_low_up_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == 1 else 0),
            "is_up_low_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == -1 else 0),
            "is_low_low_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == -1 else 0),
            "is_up_mid_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == 0 else 0),
            "is_low_mid_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == 0 else 0),
            "is_mid_up_10": (lambda cls: 1 if cls.volumeState_10 == 0 and cls.priceState_10 == 1 else 0),
            "is_mid_low_10": (lambda cls: 1 if cls.volumeState_10 == 0 and cls.priceState_10 == -1 else 0),

            # -------------------------- 状态相关 - 20日 --------------------------  # 新增20日
            "is_up_up_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == 1 else 0),
            "is_low_up_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == 1 else 0),
            "is_up_low_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == -1 else 0),
            "is_low_low_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == -1 else 0),
            "is_up_mid_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == 0 else 0),
            "is_low_mid_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == 0 else 0),
            "is_mid_up_20": (lambda cls: 1 if cls.volumeState_20 == 0 and cls.priceState_20 == 1 else 0),
            "is_mid_low_20": (lambda cls: 1 if cls.volumeState_20 == 0 and cls.priceState_20 == -1 else 0),

            # -------------------------- 状态相关 - 40日 --------------------------  # 新增40日
            "is_up_up_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == 1 else 0),
            "is_low_up_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == 1 else 0),
            "is_up_low_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == -1 else 0),
            "is_low_low_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == -1 else 0),
            "is_up_mid_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == 0 else 0),
            "is_low_mid_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == 0 else 0),
            "is_mid_up_40": (lambda cls: 1 if cls.volumeState_40 == 0 and cls.priceState_40 == 1 else 0),
            "is_mid_low_40": (lambda cls: 1 if cls.volumeState_40 == 0 and cls.priceState_40 == -1 else 0),

            # -------------------------- 状态相关 - 60日 --------------------------  # 新增60日
            "is_up_up_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == 1 else 0),
            "is_low_up_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == 1 else 0),
            "is_up_low_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == -1 else 0),
            "is_low_low_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == -1 else 0),
            "is_up_mid_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == 0 else 0),
            "is_low_mid_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == 0 else 0),
            "is_mid_up_60": (lambda cls: 1 if cls.volumeState_60 == 0 and cls.priceState_60 == 1 else 0),
            "is_mid_low_60": (lambda cls: 1 if cls.volumeState_60 == 0 and cls.priceState_60 == -1 else 0),

            # -------------------------- 状态相关 - 120日 --------------------------  # 新增120日
            "is_up_up_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == 1 else 0),
            "is_low_up_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == 1 else 0),
            "is_up_low_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == -1 else 0),
            "is_low_low_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == -1 else 0),
            "is_up_mid_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == 0 else 0),
            "is_low_mid_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == 0 else 0),
            "is_mid_up_120": (lambda cls: 1 if cls.volumeState_120 == 0 and cls.priceState_120 == 1 else 0),
            "is_mid_low_120": (lambda cls: 1 if cls.volumeState_120 == 0 and cls.priceState_120 == -1 else 0),

            # -------------------------- 振幅+价格状态 --------------------------
            "is_pop_up": (lambda cls: 1 if cls.amplitudeState_1 == 1 and cls.priceState_1 == 1 else 0),
            "is_pop_down": (lambda cls: 1 if cls.amplitudeState_1 == 1 and cls.priceState_1 == -1 else 0),
            "is_pop_up_3": (lambda cls: 1 if cls.amplitudeState_3 == 1 and cls.priceState_3 == 1 else 0),
            "is_pop_down_3": (lambda cls: 1 if cls.amplitudeState_3 == 1 and cls.priceState_3 == -1 else 0),
            "is_pop_up_5": (lambda cls: 1 if cls.amplitudeState_5 == 1 and cls.priceState_5 == 1 else 0),
            "is_pop_down_5": (lambda cls: 1 if cls.amplitudeState_5 == 1 and cls.priceState_5 == -1 else 0),
            "is_pop_up_10": (lambda cls: 1 if cls.amplitudeState_10 == 1 and cls.priceState_10 == 1 else 0),
            "is_pop_down_10": (lambda cls: 1 if cls.amplitudeState_10 == 1 and cls.priceState_10 == -1 else 0),
            "is_pop_up_20": (lambda cls: 1 if cls.amplitudeState_20 == 1 and cls.priceState_20 == 1 else 0),  # 新增20日
            "is_pop_down_20": (lambda cls: 1 if cls.amplitudeState_20 == 1 and cls.priceState_20 == -1 else 0),  # 新增20日
            "is_pop_up_40": (lambda cls: 1 if cls.amplitudeState_40 == 1 and cls.priceState_40 == 1 else 0),  # 新增40日
            "is_pop_down_40": (lambda cls: 1 if cls.amplitudeState_40 == 1 and cls.priceState_40 == -1 else 0),  # 新增40日
            "is_pop_up_60": (lambda cls: 1 if cls.amplitudeState_60 == 1 and cls.priceState_60 == 1 else 0),  # 新增60日
            "is_pop_down_60": (lambda cls: 1 if cls.amplitudeState_60 == 1 and cls.priceState_60 == -1 else 0),  # 新增60日
            "is_pop_up_120": (lambda cls: 1 if cls.amplitudeState_120 == 1 and cls.priceState_120 == 1 else 0),  # 新增120日
            "is_pop_down_120": (lambda cls: 1 if cls.amplitudeState_120 == 1 and cls.priceState_120 == -1 else 0),  # 新增120日
  
        }

    def InitCalculateBaseWindowAttrByDic(self):
        from src.main_code.Core.Calculate import CalculationUtil
        self.CalculateBaseWindowAttrDic = {
            # -------------------------- 涨跌停相关 --------------------------
            "up_stopCount": (CalculationUtil.GetUpStopCount, ("startDataCls", "startCount", "toCount")),
            "down_stopCount": (CalculationUtil.GetDownStopCount, ("startDataCls", "startCount", "toCount")),
            
            # -------------------------- 基础量价相关 --------------------------
            "volume": (CalculationUtil.GetVolume_Window, ("startDataCls", "startCount", "toCount")),
            "volume_price": (CalculationUtil.GetVolume_Price_Window, ("startDataCls", "startCount", "toCount")),
            "volume_ratio": (CalculationUtil.GetVolume_Ratio_Window, ("startDataCls", "startCount", "toCount")),
            "volume_price_ratio": (CalculationUtil.GetVolume_Price_Ratio_Window, ("startDataCls", "startCount", "toCount")),

            "turn_ratio": (CalculationUtil.GetTurn_Ratio_Window, ("startDataCls", "startCount", "toCount")),
            "change_Ratio": (CalculationUtil.GetChange_Ratio_Window, ("startDataCls", "startCount", "toCount")),
            "change_Ratio_Total": (CalculationUtil.GetChange_Ratio_Total_Window, ("startDataCls", "startCount", "toCount")),
            "avg_Ratio": (CalculationUtil.GetAvg_Ratio_Window, ("startDataCls", "startCount", "toCount")),
            "avg_Ratio_Total": (CalculationUtil.GetAvg_Ratio_Total_Window, ("startDataCls", "startCount", "toCount")),
            
            # -------------------------- 平均值类字段 --------------------------
            "avg_open": (CalculationUtil.GetOpen_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_close": (CalculationUtil.GetClose_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_high": (CalculationUtil.GetHigh_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_low": (CalculationUtil.GetLow_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_volume": (CalculationUtil.GetVolume_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_volume_price": (CalculationUtil.GetVolume_Price_Window_Avg, ("startDataCls", "startCount", "toCount")),

            "avg_volume_rito": (CalculationUtil.Get_VolumeRatio_5_Window_Avg, ("startDataCls", "startCount", "toCount", "handler")),
            "avg_turn": (CalculationUtil.GetTurn_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_change_Ratio": (CalculationUtil.GetChangeRatio_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_amplitude": (CalculationUtil.GetAmplitude_Window_Avg, ("startDataCls", "startCount", "toCount")),
            "avg_avg": (CalculationUtil.GetAvg_Price_Window_Avg, ("startDataCls", "startCount", "toCount")),
            
            # -------------------------- 最小值类字段 --------------------------
            "min_open": (CalculationUtil.GetOpen_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_close": (CalculationUtil.GetClose_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_last_close": (CalculationUtil.GetLastClose_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_high": (CalculationUtil.GetHigh_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_low": (CalculationUtil.GetLow_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_volume": (CalculationUtil.GetVolume_Window_Low, ("startDataCls", "startCount", "toCount")),

            "min_volume_price": (CalculationUtil.GetVolume_Price_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_volume_rito": (CalculationUtil.GetVolume_Ratio_5_Window_Low, ("startDataCls", "startCount", "toCount", "handler")),
            "min_turn": (CalculationUtil.GetTurn_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_change_Ratio": (CalculationUtil.GetChange_Ratio_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_amplitude": (CalculationUtil.GetAmplitude_Window_Low, ("startDataCls", "startCount", "toCount")),
            "min_avg": (CalculationUtil.GetAvg_Window_Low, ("startDataCls", "startCount", "toCount")),
            
            # -------------------------- 最大值类字段 --------------------------
            "max_open": (CalculationUtil.GetOpen_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_close": (CalculationUtil.GetClose_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_last_close": (CalculationUtil.GetLastClose_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_high": (CalculationUtil.GetHigh_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_low": (CalculationUtil.GetLow_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_volume": (CalculationUtil.GetVolume_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_volume_price": (CalculationUtil.GetVolume_Price_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_volume_rito": (CalculationUtil.GetVolume_Ratio_5_Window_High, ("startDataCls", "startCount", "toCount", "handler")),
            "max_turn": (CalculationUtil.GetTurn_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_change_Ratio": (CalculationUtil.GetChange_Ratio_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_amplitude": (CalculationUtil.GetAmplitude_Window_High, ("startDataCls", "startCount", "toCount")),
            "max_avg": (CalculationUtil.GetAvg_Window_High, ("startDataCls", "startCount", "toCount")),
            
            # -------------------------- 状态类字段（依赖windowsClass） --------------------------
            "volumeState": (CalculationUtil.GetVolume_State_Windows, ("self",)),
            "priceState": (CalculationUtil.GetChange_Ratio_State_Windows, ("self",)),
            "amplitudeState": (CalculationUtil.GetAmplitude_State_Windows, ("self",)),
            
            # -------------------------- 行业排名类字段 --------------------------
            "volume_industry_rank": (CalculationUtil.GetVolume_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "total_price_industry_rank": (CalculationUtil.GetVolume_Price_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "total_price_ratio_industry_rank": (CalculationUtil.GetVolume_Price_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "volume_ratio_industry_rank": (CalculationUtil.GetVolume_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "ratio_industry_rank": (CalculationUtil.GetChange_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "amplitude_industry_rank": (CalculationUtil.GetAmplitude_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "turn_ratio_industry_rank": (CalculationUtil.GetTurn_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
            "avg_industry_rank": (CalculationUtil.GetAvg_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),


            "is_up_up": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == 1 else 0, ()),
            "is_low_up": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == 1 else 0, ()),
            "is_up_low": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == -1 else 0, ()),
            "is_low_low": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == -1 else 0, ()),
            "is_up_mid": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == 0 else 0, ()),
            "is_low_mid": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == 0 else 0, ()),
            "is_mid_up": (lambda cls: 1 if cls.volumeState == 0 and cls.priceState == 1 else 0, ()),
            "is_mid_low": (lambda cls: 1 if cls.volumeState == 0 and cls.priceState == -1 else 0, ()),
            
            # 振幅+价格组合属性
            "is_pop_up": (lambda cls: 1 if cls.amplitudeState == 1 and cls.priceState == 1 else 0, ()),
            "is_pop_down": (lambda cls: 1 if cls.amplitudeState == 1 and cls.priceState == -1 else 0, ())


        }
