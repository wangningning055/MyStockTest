from datetime import date, datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core import Main
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core.DataStruct.DB import ValueDBStruct
from src.main_code.Core import Const
from src.main_code.Core.Calculate import CalculationFuncRegister
from src.main_code.Core.Calculate import CalculationSpecial
import time
import psutil
import os
import bisect
import random
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
        self.CalculateBaseAttrDic = {}
        self.CalculateBaseWindowAttrDic = {}
        self.CalculateIndustryBaseClassDic = {}
        self.CalculateIndustryWindowClassDic = {}
        self.InitIndustry()
        CalculationFuncRegister.RegisterCalculateFunc(self)
        self.totalDateList = self.InitDateList()
        print(self.totalDateList)
        self.InitValueData()


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



        print("      开始整理复权数据：")
        self.totalAdjustData = self.main.dbHandler.LoadAllAdjustDataToDict()
        print(f"    复权数据整理完毕")


        #这里整理价值数据
        print("     开始整理价值数据：")
        print(f"    价值数据整理完毕")


        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小


        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"整个数据获取完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 花费时间：{totalCostTimeStr1}")
        print(f"整个数据获取完毕 ")




        print(f"开计算数据，数据日期长度{Const.dateListLength} ")
        print(f"开计算数据 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
        t0 = time.perf_counter()



        todayStr = self.GetToday()
        self.InitAllBaseDataClsList(240, todayStr)



        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"数据计算完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 这个阶段花费时间：{totalCostTimeStr1}, 数据日期长度：{Const.dateListLength}")



        todayStr = self.GetToday()
        t0 = time.perf_counter()
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小
        print(f"开始计算测试数据：{todayStr} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")



        #cls = self.totalBaseDailyData[("300846.SZ", todayStr)]
        #self.CalculateBaseClass(cls)


        #windowCls = self.GetWindowDataClass("603596.SH", todayStr, 0, 240)
        #windowCls = self.GetWindowDataClass("600759.SH", todayStr, 0, 10)
        #windowCls = self.GetWindowDataClass("603318.SH", todayStr, 0, 6)
        #windowCls = self.GetWindowDataClass("603716.SH", todayStr, 0, 5)
        #self.CalculateBaseWindowClass(windowCls, windowCls.code, 0, 240)


        #industryCls = self.GetIndustryBaseData("600740.SH", "20260310")
        #self.CalculateIndustryBaseData(industryCls)


        #industryCls = self.GetIndustryWindowData("600740.SH", todayStr, 0 , 30)
        #self.CalculateIndustryWindowData(industryCls)

        def tempLog(code, start, to):
            cls1 = self.totalBaseDailyData[(code, todayStr)]
            CalculationSpecial.CalculateDownPressure(cls1, start, to, self)
        
        my_list = [10, 20, 30, 40, 50]
        # 随机取2个不重复的值
        random_items = random.sample(self.totalStockList, k=200)
        for code in random_items:
            tempLog(code, 0, 40)
            
        #cls1 = self.totalBaseDailyData[("002413.SZ", todayStr)]
        #cls2 = self.totalBaseDailyData[("600026.SH", todayStr)]
        #cls3 = self.totalBaseDailyData[("603716.SH", todayStr)]
        #cls4 = self.totalBaseDailyData[("600703.SH", todayStr)]
        #cls5 = self.totalBaseDailyData[("601872.SH", todayStr)]
        #cls6 = self.totalBaseDailyData[("600325.SH", todayStr)]
        #cls7 = self.totalBaseDailyData[("300846.SZ", todayStr)]
        #cls8 = self.totalBaseDailyData[("600885.SH", todayStr)]

        #tempLog("002413.SZ", 0, 40)
        #tempLog("600026.SH", 0, 40)
        #tempLog("603716.SH", 0, 40)
        #tempLog("600703.SH", 0, 40)
        #tempLog("601872.SH", 0, 40)
        #tempLog("600325.SH", 0, 40)
        #tempLog("300846.SZ", 0, 40)
        #tempLog("600885.SH", 0, 40)

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


    def GetBaseDataClass(self, stockCode, date, isCalculate = False) -> CalculationDataStruct.StructBaseClass:
        #print(f"开始计算, code:{stockCode}, 名字：{componenyInfo.Name}, 行业：{componenyInfo.Industry} 日期：{date}， 计算：{isCalculate} ")
        if (stockCode, date) in self.totalBaseDailyData:
            baseClass = self.totalBaseDailyData[(stockCode, date)]
            #print(f"直接返回：{stockCode}  {date}")
            if baseClass.trade_state == 1:
                return baseClass
            else:
                return None
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
        print(f"尝试获取股票：{stockCode}")
        cache_key = (stockCode, tradeDate, startDateCount, toDateCount)
        res = None
        if cache_key in self.totalBaseWindowData:
            res = self.totalBaseWindowData[cache_key]
            if res.startDataCls.trade_state == 1:
                return res
            else:
                return None


        startDataClass = self.GetBaseDataClass(stockCode, tradeDate)
        if startDataClass == None:
            return None
        if startDataClass.trade_state == 0:
            return None
        print(f"股票未缓存：{stockCode}， {startDateCount}，   {toDateCount}")
        windowsClass = CalculationDataStruct.StructBaseWindowClass()
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

                
    def GetIndustryBaseDataByCls(self,trade_date, industryInfoCls:CalculationDataStruct.StructIndustryInfoClass):
        if (industryInfoCls, trade_date) in self.CalculateIndustryBaseClassDic:
            baseClass = self.CalculateIndustryBaseClassDic[(industryInfoCls, trade_date)]
            #print(f"直接返回：{stockCode}  {date}")
            return baseClass
        else:
            #print(f"股票{stockCode},  {date}数据不存在")
            baseClass = CalculationDataStruct.StructIndustryClass()
            baseClass.Init(industryInfoCls, trade_date, self)
            self.CalculateIndustryBaseClassDic[(industryInfoCls, trade_date)] = baseClass
            return baseClass

    def GetIndustryBaseData(self, stockCode, trade_date:str):
        #componenyInfo = self.totalComponyIns.GetComponyInfo(stockCode)
        #print(f"开始计算基本行业数据, code:{stockCode}, 名字：{componenyInfo.Name}, 行业：{componenyInfo.Industry} 日期：{date} ")
        industryInfoCls = self.totalComponyIns.GetIndustryClsByCode(stockCode)
        if (industryInfoCls, trade_date) in self.CalculateIndustryBaseClassDic:
            baseClass = self.CalculateIndustryBaseClassDic[(industryInfoCls, trade_date)]
            #print(f"直接返回：{stockCode}  {date}")
            return baseClass
        else:
            #print(f"股票{stockCode},  {date}数据不存在")
            baseClass = CalculationDataStruct.StructIndustryClass()
            baseClass.Init(industryInfoCls, trade_date, self)
            self.CalculateIndustryBaseClassDic[(industryInfoCls, trade_date)] = baseClass
            return baseClass
    def CalculateIndustryBaseData(self,industryBaseClass):
        print(f"行业名称是 {industryBaseClass.name}, 行业股数量是 {len(industryBaseClass.industryInfoCls.stockList)}")
        print(f"交易日期是 {industryBaseClass.trade_date}")
        print(f"行业整体成交量是 {industryBaseClass.volume}")
        print(f"行业整体成交量涨跌幅是 {industryBaseClass.volume_ratio}")
        print(f"行业整体成交量3日平均比是 {industryBaseClass.volume_ratio_3}")
        print(f"行业整体成交量5日平均比是 {industryBaseClass.volume_ratio_5}")
        print(f"行业整体成交量10日平均比是 {industryBaseClass.volume_ratio_10}")
        print(f"行业整体成交量20日平均比是 {industryBaseClass.volume_ratio_20}")
        print(f"行业整体成交额是 {industryBaseClass.volume_price}")
        print(f"行业整体成交额涨跌幅是 {industryBaseClass.volume_price_ratio}")
        print(f"行业整体成交额3日平均比是 {industryBaseClass.volume_price_ratio_3}")
        print(f"行业整体成交额5日平均比是 {industryBaseClass.volume_price_ratio_5}")
        print(f"行业整体成交额10日平均比是 {industryBaseClass.volume_price_ratio_10}")
        print(f"行业整体成交额20日平均比是 {industryBaseClass.volume_price_ratio_20}")
        print(f"行业涨跌幅是 {industryBaseClass.change_Ratio}")
        print(f"行业上涨股数量是 {industryBaseClass.stockNum_up}")
        print(f"行业上涨股比例是 {industryBaseClass.stockNum_up_Ratio}")
        print(f"行业下跌股数量是 {industryBaseClass.stockNum_down}")
        print(f"行业下跌股比例是 {industryBaseClass.stockNum_down_Ratio}")
        #for key, val in industryBaseClass.industryInfoCls.stockList.items():
        #    print(f"行业名称是 {industryBaseClass.name}, key:{key}, val :{val.Name}")
    def GetIndustryWindowData(self, stockCode, tradeDate, startDateCount, toDateCount):
        #print(f"开始计算, code:{stockCode}, 名字：{componenyInfo.Name}, 行业：{componenyInfo.Industry} 日期：{date}， 计算：{isCalculate} ")
        industryInfoCls = self.totalComponyIns.GetIndustryClsByCode(stockCode)
        if (industryInfoCls, tradeDate, startDateCount, toDateCount) in self.CalculateIndustryWindowClassDic:
            baseClass = self.CalculateIndustryWindowClassDic[(industryInfoCls, tradeDate, startDateCount, toDateCount)]
            return baseClass
        else:
            #print(f"股票{stockCode},  {date}数据不存在")
            baseClass = CalculationDataStruct.StructIndustryWindowClass()
            baseClass.Init(industryInfoCls, tradeDate, startDateCount,toDateCount, self)
            self.CalculateIndustryWindowClassDic[(industryInfoCls, tradeDate, startDateCount, toDateCount)] = baseClass
            return baseClass

    def CalculateIndustryWindowData(self, industryWindowClass):
        print(f"行业名称是 {industryWindowClass.name}, 行业股数量是 {len(industryWindowClass.industryInfoCls.stockList)}")
        print(f"行业整体成交量是 {industryWindowClass.volume}")
        print(f"行业整体成交额是 {industryWindowClass.volume_price}")
        print(f"行业平均成交量是 {industryWindowClass.avg_volume}")
        print(f"行业平均成交额是 {industryWindowClass.avg_volume_price}")
        print(f"行业整体成交量涨跌幅 {industryWindowClass.volume_ratio}")
        print(f"行业整体成交额涨跌幅 {industryWindowClass.volume_price_ratio}")
        print(f"行业涨跌幅 {industryWindowClass.change_Ratio}")
        print(f"行业整体涨跌幅 {industryWindowClass.change_Ratio_Total}")
        print(f"行业平均上涨股数量 {industryWindowClass.avg_stockNum_up}")
        print(f"行业平均下跌股数量 {industryWindowClass.avg_stockNum_down}")
        print(f"行业平均上涨股比例 {industryWindowClass.stockNum_up_Ratio}")
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

    #获取最近一次有效的交易日
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
                

    #初始化日期列表
    def InitDateList(self):
        today = self.GetToday()
        dayList = []
        dt = datetime.strptime(today, "%Y%m%d")
        end_dt = datetime.strptime(Const.first_Data, "%Y%m%d")

        if dt.weekday() < 5:  # 0-4 代表周一到周五，5=周六，6=周日
            dayList.append(today)
        while len(dayList) < Const.dateListLength and dt > end_dt:
            dt -= timedelta(days=1)  # 往前一天

            if dt.weekday() >= 5:
                continue  # 跳过周末，不加入列表
            date_str = dt.strftime("%Y%m%d")
            dayList.append(date_str)
            
        return dayList
    

    #构建整个基础类列表
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
                        #if code == "000001.SZ":
                        #    count += 1
                            #print(f"a啊啊啊啊啊啊啊啊啊啊啊啊啊载入的时间是 ：{date}, 数量：{count}")
                        self.totalBaseDailyData[(code, date)] = baseClass

    #获取最近的复权数据
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


    #4/31(一季报，上一年年报)
    #8/31(二季报)
    #10/31（三季报）
    #初始化价值数据
    def InitValueData(self):
        todayStr = self.GetToday()
        todayDate = datetime.strptime(todayStr, "%Y%m%d")
        year = todayDate.year
        month = todayDate.month
        dbDic = self.main.dbHandler.LoadAllValueDataToDict()
        #print(f"获取价值数据字符串是{todayStr},  年份是：{year}，    月份是{month}")
        allCodeList = self.totalStockList
        dbStruct =  ValueDBStruct.DBStructClass()
        #季报数据获取
        for code in allCodeList:
            componyInfo = self.totalComponyIns.GetComponyInfo(code)
            target_year = 0
            target_q = 0
            if month >= 5 and month <= 8:
                target_year = year
                target_q = 1
            if month >= 9 and month <= 10:
                target_year = year
                target_q = 2
            if month >= 11 and month <= 12:
                target_year = year
                target_q = 3
            if month >= 1 and month <= 4:
                target_year = year - 1
                target_q = 3

            catchKey = (code, target_year, target_q)
            #print(f"获取价值季度数据字符串是{todayStr},  目标年份是：{target_year}，    目标季度是{target_q}")
            val = dbDic.get(catchKey)
            if val is not None: 
                roe = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.Roe)]
                yoyni = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYNi)]
                liabilityTo = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.LiabilityTo)]
                yoyEquity = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYEquity)]
                yoyLiability = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYLiability)]

                componyInfo.Roe = roe
                componyInfo.YOYNi = yoyni
                componyInfo.LiabilityTo = liabilityTo
                componyInfo.YOYEquity = yoyEquity
                componyInfo.YOYLiability = yoyLiability



            #年报数据获取
            y_target_year = 0
            y_target_q = 0
            if month >= 1 and month <= 4:
                y_target_year = year - 1
                y_target_q = 2
            if month >= 5 and month <= 8:
                y_target_year = year - 1
                y_target_q = 4
            if month >= 9 and month <= 12:
                y_target_year = year
                y_target_q = 2

            #print(f"获取价值年度数据字符串是{todayStr},  目标年份是：{y_target_year}，    目标季度是{y_target_q}")
            catchKey = (code, y_target_year, y_target_q)
            val = dbDic.get(catchKey)
            if val is not None: 
                roe = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.Roe)]
                yoyni = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYNi)]
                liabilityTo = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.LiabilityTo)]
                yoyEquity = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYEquity)]
                yoyLiability = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYLiability)]

                componyInfo.Roe_Year = roe
                componyInfo.YOYNi_Year = yoyni
                componyInfo.LiabilityTo_Year = liabilityTo
                componyInfo.YOYEquity_Year = yoyEquity
                componyInfo.YOYLiability_Year = yoyLiability