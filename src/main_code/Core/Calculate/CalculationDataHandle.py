from datetime import date, datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core.DataStruct.WebResult import WebResultDataStruct
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
import asyncio
import gc
import sys
import json

class BaseClass :
    isOutCY : bool
    isOutKC : bool
    isOutST : bool

    def __init__(self):
        self.isOutCY = False
        self.isOutKC = False
        self.isOutST = False
        self.isNeedStop = False
        pass
    
    
    def Init(self, main, todayStr = "000000"):
        self.main :Main.processor = main
        self.task = None
        self.totalStockList = []
        self.totalComponyIns : CalculationDataStruct.StructIndustryTotalInfoClass = CalculationDataStruct.StructIndustryTotalInfoClass()

        #临时存储
        self.totalBaseDailyData : Dict[str, Dict[str, CalculationDataStruct.StructBaseClass]] = {}
        self.totalBaseWindowData : Dict[str, CalculationDataStruct.StructBaseWindowClass]  = {}
        self.totalAdjustData = {}
        self.CalculateIndustryBaseClassDic = {}
        self.CalculateIndustryWindowClassDic = {}

        #方法存储
        self.CalculateBaseAttrDic = {}
        self.CalculateBaseWindowAttrDic = {}
        self.CalculateIndustryBaseClassAttrDic = {}
        self.CalculateIndustryWindowClassAttrDic = {}
        self.isInStop = False

        self.InitIndustry()
        CalculationFuncRegister.RegisterCalculateFunc(self)
        self.isPreheating = False
        if todayStr == "000000":
            self.todayStr = self.GetToday()
            self.main.recordDataCls.industry_list = []
            for key, industryCls in self.totalComponyIns.industryList.items():
                if key is not None:
                    self.main.recordDataCls.industry_list.append(key)
            self.main.recordHandler.WriteRecordData()

        else:
            self.todayStr = todayStr

    async def DataPreheating(self, isNeedLog = True, isJumpReadDb = False):
        self.main.SetIsInHandle(True)
        await asyncio.sleep(0)
        today = self.todayStr
        if today == None:
            print("没有拉取数据记录，无法进行数据预热")
            self.main.BoardCast("没有拉取数据记录，无法进行数据预热")
            self.main.SetIsInHandle(False)
            return
        
        if isNeedLog:
            print("开始数据预热")
            self.main.BoardCast("开始数据预热")
            
        ##################################################################
        if isJumpReadDb == False:
            self.totalDateList = self.InitDateList(today, Const.dateListLength)
            
        if isNeedLog:
            print(self.totalDateList)
        await asyncio.sleep(0)

        
        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)

        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小
        t0 = time.perf_counter()

        if isNeedLog:
            print(f"开始读取数据库 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            self.main.BoardCast(f"开始读取数据库 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
        await asyncio.sleep(0)
        if self.isInStop:
            return
        

        ##################################################################
        if isJumpReadDb == False:
            self.totalDbList = self.main.dbHandler.GetDailyRowByCodeListAndDateList(self.totalStockList, self.totalDateList)

            

        if isJumpReadDb == False:
            self.totalValueDbDic = self.main.dbHandler.LoadAllValueDataToDict()
        
        
        if self.isInStop:
            return

        t_db = time.perf_counter()
        totalCostTime = (t_db - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)

        if isNeedLog:
            print(f"数据库读取完毕 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 花费时间{totalCostTimeStr1}")
            self.main.BoardCast(f"开始读取数据库 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 花费时间{totalCostTimeStr1}")

        await asyncio.sleep(0)



        if isNeedLog:
            print("      开始整理复权数据：")

        ##################################################################
        if isJumpReadDb == False:
            self.totalAdjustData = self.main.dbHandler.LoadAllAdjustDataToDict()

        if self.isInStop:
            return

        if isNeedLog:
            print(f"    复权数据整理完毕")

        await asyncio.sleep(0)

        #这里整理价值数据
        if isNeedLog:
            print("     开始整理价值数据：")
        await asyncio.sleep(0)



        ##################################################################
        self.InitValueData()

        if isNeedLog:
            print(f"    价值数据整理完毕")

        if self.isInStop:
            return
        await asyncio.sleep(0)

        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小


        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        #print(f"整个数据获取完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 花费时间：{totalCostTimeStr1}")
        #print(f"整个数据获取完毕 ")

        await asyncio.sleep(0)


        if isNeedLog:
            print(f"开计算数据 数据日期长度{Const.dateListLength}  物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            self.main.BoardCast(f"开计算数据 数据日期长度{Const.dateListLength}  物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
        t0 = time.perf_counter()

        await asyncio.sleep(0)


        ##################################################################


        isLog = isJumpReadDb == False
        if isJumpReadDb == False:
            await self.InitAllBaseDataClsList(self.totalDateList, self.totalDbList, isLog)
        #print("")
        #dateList = []
        #for key ,val in self.totalBaseDailyData.items():
        #    #print(f"{key[0]},    {key[1]}")
        #    if key[0] == "000001.SZ":
        #        dateList.append(key[1])

        #print(f"长度是 {len(self.totalBaseDailyData)},  日期列表是是：{dateList}")
        #print("")


        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)


        if isNeedLog:
            print(f"数据预热完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 这个阶段花费时间：{totalCostTimeStr1}, 数据日期长度：{Const.dateListLength}")
            self.main.BoardCast(f"数据预热完毕   物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}, 数据预热花费时间：{totalCostTimeStr1}, 数据日期长度：{Const.dateListLength}")

        self.main.SetIsInHandle(False)

        self.isPreheating = True
        if isJumpReadDb == False:
            growValueList = self.GetValueGrowStockListForWeb()
            self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.LAST_UPDATE_GROW_VALUE, growValueList)


    #向前移动1天
    async def MoveDateToNextDay(self):
        if self.isPreheating == False:
            print("请先预热数据")
            return ""

        #t0 = time.perf_counter()

        #t_end = time.perf_counter()
        #totalCostTime = (t_end - t_select)
        #totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        
        
        #-------------------------------------------
        #获取下一天的日期
        nextDayStr = self.GetNextDay()
        oldDayStr = self.todayStr

        
        if nextDayStr == "":
            print("这是最后一天了，没有下一天了")
            return ""
        self.todayStr = nextDayStr
        
        #老的日期列表
        oldDataList = self.totalDateList

        #初始化新的日期列表
        newDataList = self.InitDateList(nextDayStr, Const.dateListLength)
        self.totalDateList = newDataList

        #找到两个列表的差别
        diff_list =  [item for item in oldDataList if item not in newDataList]
        

        delCount = 0
        addCount = 0

        #-------------------------------------------
        #执行删除
        for day in diff_list:

            #基本日线数据删除
            #第一种删除方法
            keys_to_delete_base = [
                key for key in self.totalBaseDailyData
                if key == day
            ]

            for key in keys_to_delete_base:
                #delCount += 1
                for key2, val2 in self.totalBaseDailyData[key].items():
                    val2.Clear()
                    
                self.totalBaseDailyData[key].clear()
                del self.totalBaseDailyData[key]


            #窗口数据删除
            keys_to_delete_window = [
                key for key in self.totalBaseWindowData
                if key[1] == day
            ]
            for key in keys_to_delete_window:
                self.totalBaseWindowData[key].Clear()
                del self.totalBaseWindowData[key]


            #行业数据删除
            keys_to_delete_industry = [
                key for key in self.CalculateIndustryBaseClassDic
                if key[1] == day
            ]
            for key in keys_to_delete_industry:
                self.CalculateIndustryBaseClassDic[key].Clear()
                del self.CalculateIndustryBaseClassDic[key]

            #行业窗口数据删除
            keys_to_delete_industry_window = [
                key for key in self.CalculateIndustryWindowClassDic
                if key[1] == day
            ]
            for key in keys_to_delete_industry_window:
                self.CalculateIndustryWindowClassDic[key].Clear()
                del self.CalculateIndustryWindowClassDic[key]


            #数据库数据删除
            keys_to_delete_industry_db = [
                key for key in self.totalDbList
                if key[1] == day
            ]


            for key in keys_to_delete_industry_db:
                delCount += 1
                del self.totalDbList[key]
                

        #-------------------------------------------
        #重读数据库
        #print("     开始重读数据库")
        #t4 = time.perf_counter()

        for code in self.totalStockList:
            catchKey = (code, nextDayStr)
            res = self.main.dbHandler.GetDailyRowByCodeAndDate(code, nextDayStr)
            if res != None:
                addCount += 1
                self.totalDbList[catchKey] = res

                dateItem = self.totalBaseDailyData.get(nextDayStr)
                if dateItem is None:
                    dateItem = {}
                    self.totalBaseDailyData[nextDayStr] = dateItem

                if (code) in dateItem:
                    continue
                else:
                    isKC = Const.GetIsKC(code)
                    isCY = Const.GetIsCy(code)
                    isBJ = Const.GetIsBJ(code)
                    if isBJ :
                        continue
                    if isKC and self.isOutKC:
                        continue
                    if isCY and self.isOutCY:
                        continue

                    baseClass = CalculationDataStruct.StructBaseClass()
                    baseClass.Init(self, code, nextDayStr, res)


                    isST = baseClass.isST == 1
                    if isST and self.isOutST:
                        continue
    
                    dateItem[code] = baseClass



        #all_codes = set()
        #all_days = set()
        #for  (code, day_str) in self.totalDbList.keys():
        #    all_codes.add(code)
        #    all_days.add(day_str)

        ## 最后转成列表（如果你需要列表）
        #all_codes = list(all_codes)
        #all_days = list(all_days)

        #print(f"     执行数据库结束，删除的数量是：{delCount}，增加的数量是：{addCount} 数据库长度：{len(self.totalDbList)} 股长度：{len(all_codes)}，日期长度：{len(all_days)}    基本日线长度：{len(self.totalBaseDailyData)}")



        #-------------------------------------------
        #重新预热
        #selfSize = asizeof.asizeof(self)
        await self.DataPreheating(False,True)
        #t5 = time.perf_counter()
        #totalCostTime = (t5 - t4)
        #totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)

        #print(f"     重新读取数据库和预热结束 花费时间：{totalCostTimeStr1}")

        #gc.collect()
        return nextDayStr




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
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return
        #print(f"开始计算, code:{stockCode}, 名字：{componenyInfo.Name}, 行业：{componenyInfo.Industry} 日期：{date}， 计算：{isCalculate} ")
        dateItem = self.totalBaseDailyData.get(date)
        if dateItem is None:
            return None
        cls = dateItem.get(stockCode)
        if cls is None:
            return None
        if cls.trade_state == 1:
            return cls
        else:
            return None
        
    def GetBaseDataClass_WithTradeState(self, stockCode, date, isCalculate = False) -> CalculationDataStruct.StructBaseClass:
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return
        dateItem = self.totalBaseDailyData.get(date)
        if dateItem is None:
            return None
        cls = dateItem.get(stockCode)
        if cls is None:
            return None
        return cls


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
        

        print(f"价值股评分：{baseClass.ValueScore}")
        print(f"成长股评分：{baseClass.GrowScore}")
        print(f"是否处在行业上涨周期:{baseClass.isInIndustryUp}")

        print(f"20日上压力位:{baseClass.up_pressure_20}")
        print(f"20日下压力位:{baseClass.down_pressure_20}")
        print(f"40日上压力位:{baseClass.up_pressure_40}")
        print(f"40日下压力位:{baseClass.down_pressure_40}")
        print(f"60日上压力位:{baseClass.up_pressure_60}")
        print(f"60日下压力位:{baseClass.down_pressure_60}")
        print(f"120日上压力位:{baseClass.up_pressure_120}")
        print(f"120日下压力位:{baseClass.down_pressure_120}")
        print(f"240日上压力位:{baseClass.up_pressure_240}")
        print(f"240日下压力位:{baseClass.down_pressure_240}")

        # 单一日突破/跌破打印
        print(f"是否突破20日上压力位:{baseClass.is_break_upper_20}")
        print(f"是否跌破20日下压力位:{baseClass.is_break_lower_20}")
        print(f"是否突破40日上压力位:{baseClass.is_break_upper_40}")
        print(f"是否跌破40日下压力位:{baseClass.is_break_lower_40}")
        print(f"是否突破60日上压力位:{baseClass.is_break_upper_60}")
        print(f"是否跌破60日下压力位:{baseClass.is_break_lower_60}")
        print(f"是否突破120日上压力位:{baseClass.is_break_upper_120}")
        print(f"是否跌破120日下压力位:{baseClass.is_break_lower_120}")
        print(f"是否突破240日上压力位:{baseClass.is_break_upper_240}")
        print(f"是否跌破240日下压力位:{baseClass.is_break_lower_240}")

        # 连续2日突破/跌破打印
        print(f"是否连续2日突破20日上压力位:{baseClass.is_break_upper_20_2}")
        print(f"是否连续2日跌破20日下压力位:{baseClass.is_break_lower_20_2}")
        print(f"是否连续2日突破40日上压力位:{baseClass.is_break_upper_40_2}")
        print(f"是否连续2日跌破40日下压力位:{baseClass.is_break_lower_40_2}")
        print(f"是否连续2日突破60日上压力位:{baseClass.is_break_upper_60_2}")
        print(f"是否连续2日跌破60日下压力位:{baseClass.is_break_lower_60_2}")
        print(f"是否连续2日突破120日上压力位:{baseClass.is_break_upper_120_2}")
        print(f"是否连续2日跌破120日下压力位:{baseClass.is_break_lower_120_2}")
        print(f"是否连续2日突破240日上压力位:{baseClass.is_break_upper_240_2}")
        print(f"是否连续2日跌破240日下压力位:{baseClass.is_break_lower_240_2}")

        # 连续3日突破/跌破打印
        print(f"是否连续3日突破20日上压力位:{baseClass.is_break_upper_20_3}")
        print(f"是否连续3日跌破20日下压力位:{baseClass.is_break_lower_20_3}")
        print(f"是否连续3日突破40日上压力位:{baseClass.is_break_upper_40_3}")
        print(f"是否连续3日跌破40日下压力位:{baseClass.is_break_lower_40_3}")
        print(f"是否连续3日突破60日上压力位:{baseClass.is_break_upper_60_3}")
        print(f"是否连续3日跌破60日下压力位:{baseClass.is_break_lower_60_3}")
        print(f"是否连续3日突破120日上压力位:{baseClass.is_break_upper_120_3}")
        print(f"是否连续3日跌破120日下压力位:{baseClass.is_break_lower_120_3}")
        print(f"是否连续3日突破240日上压力位:{baseClass.is_break_upper_240_3}")
        print(f"是否连续3日跌破240日下压力位:{baseClass.is_break_lower_240_3}")

        # 连续5日突破/跌破打印
        print(f"是否连续5日突破20日上压力位:{baseClass.is_break_upper_20_5}")
        print(f"是否连续5日跌破20日下压力位:{baseClass.is_break_lower_20_5}")
        print(f"是否连续5日突破40日上压力位:{baseClass.is_break_upper_40_5}")
        print(f"是否连续5日跌破40日下压力位:{baseClass.is_break_lower_40_5}")
        print(f"是否连续5日突破60日上压力位:{baseClass.is_break_upper_60_5}")
        print(f"是否连续5日跌破60日下压力位:{baseClass.is_break_lower_60_5}")
        print(f"是否连续5日突破120日上压力位:{baseClass.is_break_upper_120_5}")
        print(f"是否连续5日跌破120日下压力位:{baseClass.is_break_lower_120_5}")
        print(f"是否连续5日突破240日上压力位:{baseClass.is_break_upper_240_5}")
        print(f"是否连续5日跌破240日下压力位:{baseClass.is_break_lower_240_5}")

        # 当日价格与压力位比值打印
        print(f"当日收盘价与20日上压力位的比:{baseClass.ratio_close_upper_20}")
        print(f"当日收盘价与20日下压力位的比:{baseClass.ratio_close_lower_20}")
        print(f"当日收盘价与40日上压力位的比:{baseClass.ratio_close_upper_40}")
        print(f"当日收盘价与40日下压力位的比:{baseClass.ratio_close_lower_40}")
        print(f"当日收盘价与60日上压力位的比:{baseClass.ratio_close_upper_60}")
        print(f"当日收盘价与60日下压力位的比:{baseClass.ratio_close_lower_60}")
        print(f"当日收盘价与120日上压力位的比:{baseClass.ratio_close_upper_120}")
        print(f"当日收盘价与120日下压力位的比:{baseClass.ratio_close_lower_120}")
        print(f"当日收盘价与240日上压力位的比:{baseClass.ratio_close_upper_240}")
        print(f"当日收盘价与240日下压力位的比:{baseClass.ratio_close_lower_240}")

        # 2日平均价格与压力位比值打印
        print(f"2日平均收盘价与20日上压力位的比:{baseClass.ratio_close_upper_2_20}")
        print(f"2日平均收盘价与20日下压力位的比:{baseClass.ratio_close_lower_2_20}")
        print(f"2日平均收盘价与40日上压力位的比:{baseClass.ratio_close_upper_2_40}")
        print(f"2日平均收盘价与40日下压力位的比:{baseClass.ratio_close_lower_2_40}")
        print(f"2日平均收盘价与60日上压力位的比:{baseClass.ratio_close_upper_2_60}")
        print(f"2日平均收盘价与60日下压力位的比:{baseClass.ratio_close_lower_2_60}")
        print(f"2日平均收盘价与120日上压力位的比:{baseClass.ratio_close_upper_2_120}")
        print(f"2日平均收盘价与120日下压力位的比:{baseClass.ratio_close_lower_2_120}")
        print(f"2日平均收盘价与240日上压力位的比:{baseClass.ratio_close_upper_2_240}")
        print(f"2日平均收盘价与240日下压力位的比:{baseClass.ratio_close_lower_2_240}")

        # 3日平均价格与压力位比值打印
        print(f"3日平均收盘价与20日上压力位的比:{baseClass.ratio_close_upper_3_20}")
        print(f"3日平均收盘价与20日下压力位的比:{baseClass.ratio_close_lower_3_20}")
        print(f"3日平均收盘价与40日上压力位的比:{baseClass.ratio_close_upper_3_40}")
        print(f"3日平均收盘价与40日下压力位的比:{baseClass.ratio_close_lower_3_40}")
        print(f"3日平均收盘价与60日上压力位的比:{baseClass.ratio_close_upper_3_60}")
        print(f"3日平均收盘价与60日下压力位的比:{baseClass.ratio_close_lower_3_60}")
        print(f"3日平均收盘价与120日上压力位的比:{baseClass.ratio_close_upper_3_120}")
        print(f"3日平均收盘价与120日下压力位的比:{baseClass.ratio_close_lower_3_120}")
        print(f"3日平均收盘价与240日上压力位的比:{baseClass.ratio_close_upper_3_240}")
        print(f"3日平均收盘价与240日下压力位的比:{baseClass.ratio_close_lower_3_240}")

        # 5日平均价格与压力位比值打印
        print(f"5日平均收盘价与20日上压力位的比:{baseClass.ratio_close_upper_5_20}")
        print(f"5日平均收盘价与20日下压力位的比:{baseClass.ratio_close_lower_5_20}")
        print(f"5日平均收盘价与40日上压力位的比:{baseClass.ratio_close_upper_5_40}")
        print(f"5日平均收盘价与40日下压力位的比:{baseClass.ratio_close_lower_5_40}")
        print(f"5日平均收盘价与60日上压力位的比:{baseClass.ratio_close_upper_5_60}")
        print(f"5日平均收盘价与60日下压力位的比:{baseClass.ratio_close_lower_5_60}")
        print(f"5日平均收盘价与120日上压力位的比:{baseClass.ratio_close_upper_5_120}")
        print(f"5日平均收盘价与120日下压力位的比:{baseClass.ratio_close_lower_5_120}")
        print(f"5日平均收盘价与240日上压力位的比:{baseClass.ratio_close_upper_5_240}")
        print(f"5日平均收盘价与240日下压力位的比:{baseClass.ratio_close_lower_5_240}")

        pass

    def GetWindowDataClass(self, stockCode, tradeDate, startDateCount, toDateCount, isJustSetRank = False):
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return
        #print(f"尝试获取股票：{stockCode}")
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
        #print(f"股票未缓存：{stockCode}， {startDateCount}，   {toDateCount}")
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

            print(f"成交量行业排名是 {windowsClass.volume_industry_rank}%")
            print(f"成交额行业排名是 {windowsClass.total_price_industry_rank}%")
            print(f"成交额涨跌幅行业排名是 {windowsClass.total_price_ratio_industry_rank}%")
            print(f"成交量涨跌幅行业排名是 {windowsClass.volume_ratio_industry_rank}%")
            print(f"涨跌幅行业排名是 {windowsClass.ratio_industry_rank}%")
            print(f"振幅行业排名是 {windowsClass.amplitude_industry_rank}%")
            print(f"换手率涨跌幅行业排名是 {windowsClass.turn_ratio_industry_rank}%")
            print(f"均价行业排名是 {windowsClass.avg_industry_rank}%")
            # 区间压力位突破/跌破次数打印
            print(f"区间突破20日上压力位次数:{windowsClass.break_upper_count_20}")
            print(f"区间跌破20日下压力位次数:{windowsClass.break_lower_count_20}")
            print(f"区间突破40日上压力位次数:{windowsClass.break_upper_count_40}")
            print(f"区间跌破40日下压力位次数:{windowsClass.break_lower_count_40}")
            print(f"区间突破60日上压力位次数:{windowsClass.break_upper_count_60}")
            print(f"区间跌破60日下压力位次数:{windowsClass.break_lower_count_60}")
            print(f"区间突破120日上压力位次数:{windowsClass.break_upper_count_120}")
            print(f"区间跌破120日下压力位次数:{windowsClass.break_lower_count_120}")
            print(f"区间突破240日上压力位次数:{windowsClass.break_upper_count_240}")
            print(f"区间跌破240日下压力位次数:{windowsClass.break_lower_count_240}")

            # 区间平均价格与压力位比值打印
            print(f"区间平均收盘价与20日上压力位的比:{windowsClass.ratio_avg_close_upper_20}")
            print(f"区间平均收盘价与20日下压力位的比:{windowsClass.ratio_avg_close_lower_20}")
            print(f"区间平均收盘价与40日上压力位的比:{windowsClass.ratio_avg_close_upper_40}")
            print(f"区间平均收盘价与40日下压力位的比:{windowsClass.ratio_avg_close_lower_40}")
            print(f"区间平均收盘价与60日上压力位的比:{windowsClass.ratio_avg_close_upper_60}")
            print(f"区间平均收盘价与60日下压力位的比:{windowsClass.ratio_avg_close_lower_60}")
            print(f"区间平均收盘价与120日上压力位的比:{windowsClass.ratio_avg_close_upper_120}")
            print(f"区间平均收盘价与120日下压力位的比:{windowsClass.ratio_avg_close_lower_120}")
            print(f"区间平均收盘价与240日上压力位的比:{windowsClass.ratio_avg_close_upper_240}")
            print(f"区间平均收盘价与240日下压力位的比:{windowsClass.ratio_avg_close_lower_240}")

                
    def GetIndustryBaseDataByCls(self,trade_date, industryInfoCls:CalculationDataStruct.StructIndustryInfoClass):
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return

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
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return

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
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return

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

    def GetIndustryWindowDataByCls(self, tradeDate, startDateCount, toDateCount, industryInfoCls:CalculationDataStruct.StructIndustryInfoClass):
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return

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


    def AnalyzeIndustry(self):
        asyncio.get_running_loop().create_task(CalculationSpecial.CalculateIndustryInfoTotal(self.main))

    def GetValueGrowStockList(self):
        if self.isPreheating == False:
            print("没有预热数据，请先预热数据")
            self.main.BoardCast("没有预热数据，请先预热数据")
            return
        valueList:List[CalculationDataStruct.StructBaseClass] = []
        growList:List[CalculationDataStruct.StructBaseClass] = []
        for stockCode in self.totalStockList:
            cls = self.GetBaseDataClass(stockCode, self.todayStr)
            if cls is not None and cls.trade_state == 1:
                if cls.ValueScore > 0:
                    valueList.append(cls)
                if cls.GrowScore > 0:
                    growList.append(cls)
        return valueList, growList


    def GetValueGrowStockListForWeb(self):
        valueList:List[CalculationDataStruct.StructBaseClass]
        growList:List[CalculationDataStruct.StructBaseClass]
        valueList, growList= self.GetValueGrowStockList()
        count = 0
        resultList = []
        if valueList is not None and growList is not None:
            for cls in valueList:
                data = WebResultDataStruct.GrowValueStockListDataStruct()
                data.code = cls.code
                data.name = cls.componyInfo.Name
                data.industry = cls.industry
                data.type = "value"   #'value' 或 'growth'
                data.score = cls.ValueScore

                # 涨跌幅
                data.change_3d = cls.change_Ratio_single_3
                data.change_5d = cls.change_Ratio_single_5
                data.change_20d = cls.change_Ratio_single_20
                data.change_120d = cls.change_Ratio_single_120
                data.change_240d = cls.change_Ratio_single_240

                # 市值
                data.value = cls.total_value / 100000000  # 转换为亿

                # 财务估值指标
                data.Roe = cls.componyInfo.Roe  # ROE
                data.earn = cls.earn   # 市盈率
                data.clean = cls.clean  # 市净率
                data.sale = cls.sale   # 市销率
                data.cash = cls.cash   # 市现率

                # 增长与负债
                data.YOYNi = cls.componyInfo.YOYNi          # 净利润同比增长率
                data.LiabilityTo = cls.componyInfo.LiabilityTo    # 资产负债率
                data.YOYEquity = cls.componyInfo.YOYEquity      # 净资产同比增长率
                data.YOYLiability = cls.componyInfo.YOYLiability   # 负债同比增长率
                resultList.append(data)

            for cls in growList:
                data = WebResultDataStruct.GrowValueStockListDataStruct()
                data.code = cls.code
                data.name = cls.componyInfo.Name
                data.industry = cls.industry
                data.type = "growth"   #'value' 或 'growth'
                data.score = cls.GrowScore 

                # 涨跌幅
                data.change_3d = cls.change_Ratio_single_3
                data.change_5d = cls.change_Ratio_single_5
                data.change_20d = cls.change_Ratio_single_20
                data.change_120d = cls.change_Ratio_single_120
                data.change_240d = cls.change_Ratio_single_240

                # 市值
                data.value = cls.total_value/ 100000000

                # 财务估值指标
                data.Roe = cls.componyInfo.Roe  # ROE
                data.earn = cls.earn   # 市盈率
                data.clean = cls.clean  # 市净率
                data.sale = cls.sale   # 市销率
                data.cash = cls.cash   # 市现率

                # 增长与负债
                data.YOYNi = cls.componyInfo.YOYNi          # 净利润同比增长率
                data.LiabilityTo = cls.componyInfo.LiabilityTo    # 资产负债率
                data.YOYEquity = cls.componyInfo.YOYEquity      # 净资产同比增长率
                data.YOYLiability = cls.componyInfo.YOYLiability   # 负债同比增长率
                resultList.append(data)

        json_str = json.dumps(
            [item.model_dump() for item in resultList],
            ensure_ascii=False
        )
        return json_str

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
        if last == Const.first_Data:
            return None
        
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
                
    #获取下一天
    def GetNextDay(self):
        nowStr = self.todayStr
        date_format = "%Y%m%d"
        curDate = datetime.strptime(nowStr, date_format)
        count = 1
        while count < 50:
            days_next = curDate + timedelta(days=count)
            days_next_str = days_next.strftime(date_format)
            random_items = random.sample(self.totalStockList, k=200)
            for code in random_items:
                res = self.main.dbHandler.GetDailyRowByCodeAndDate(code, days_next_str)
                if res is not None:
                    return days_next_str
            count +=1
        return ""




    #初始化日期列表
    def InitDateList(self, today, length):
        dayList = []
        dt = datetime.strptime(today, "%Y%m%d")
        end_dt = datetime.strptime(Const.first_Data, "%Y%m%d")

        if dt.weekday() < 5:  # 0-4 代表周一到周五，5=周六，6=周日
            dayList.append(today)
        while len(dayList) < length and dt > end_dt:
            if self.isInStop:
                break
            dt -= timedelta(days=1)  # 往前一天

            if dt.weekday() >= 5:
                continue  # 跳过周末，不加入列表
            date_str = dt.strftime("%Y%m%d")
            dayList.append(date_str)
        return dayList
    

    #构建整个基础类列表
    async def InitAllBaseDataClsList(self, totalDateList, totalDbList, isLog = False):
        count = 0
        progressInterval = 0
        for date in totalDateList:
            if self.isInStop:
                break
            count = count + 1
            dateItem = self.totalBaseDailyData.get(date)
            if dateItem is None:
                dateItem = {}
                self.totalBaseDailyData[date] = dateItem
            if isLog:
                print("正在预热基础数据，日期是：", date, f"进度{count}/{len(totalDateList)}")

                progressInterval = progressInterval + 1
                if progressInterval >= Const.progress_interval_preheat:
                    self.main.SendProgress(count / len(totalDateList))
                    progressInterval = 0
                    await asyncio.sleep(0)

            for code in self.totalStockList:
                if self.isInStop:
                    break
                db = totalDbList.get((code, date))

                if db is None:
                    continue
                else:
                    if (code) in dateItem:
                        continue
                    else:
                        isKC = Const.GetIsKC(code)
                        isCY = Const.GetIsCy(code)
                        isBJ = Const.GetIsBJ(code)
                        if isBJ :
                            continue
                        if isKC and self.isOutKC:
                            continue
                        if isCY and self.isOutCY:
                            continue

                        baseClass = CalculationDataStruct.StructBaseClass()
                        baseClass.Init(self, code, date, db)


                        isST = baseClass.isST == 1
                        if isST and self.isOutST:
                            continue
                        
                        dateItem[code] = baseClass

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
        todayStr = self.todayStr
        if todayStr == None:
            print("没有拉取数据记录，无法进行数据预热")
            self.main.BoardCast("没有拉取数据记录，无法进行价值分析")
            return

        todayDate = datetime.strptime(todayStr, "%Y%m%d")
        year = todayDate.year
        month = todayDate.month
        #print(f"获取价值数据字符串是{todayStr},  年份是：{year}，    月份是{month}")
        allCodeList = self.totalStockList
        dbStruct =  ValueDBStruct.DBStructClass()
        haveNum_quarter = 0
        haveNum_year = 0
        noneNum_quarter = 0
        noneNum_year = 0
        wrongNum_quarter = 0
        wrongNum_year = 0

        q_target_year = 0
        q_target_q = 0
        if month >= 5 and month <= 8:
            q_target_year = year
            q_target_q = 1
        if month >= 9 and month <= 10:
            q_target_year = year
            q_target_q = 2
        if month >= 11 and month <= 12:
            q_target_year = year
            q_target_q = 3
        if month >= 1 and month <= 4:
            q_target_year = year - 1
            q_target_q = 3


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

        for code in allCodeList:
            componyInfo = self.totalComponyIns.GetComponyInfo(code)


            catchKey = (code, q_target_year, q_target_q)
            #print(f"获取价值季度数据字符串是{todayStr},  目标年份是：{q_target_year}，    目标季度是{q_target_q}")
            val = self.totalValueDbDic.get(catchKey)
            if val is not None: 
                roe = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.Roe)] * 100
                yoyni = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYNi)] * 100
                liabilityTo = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.LiabilityTo)] * 100 
                yoyEquity = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYEquity)] * 100
                yoyLiability = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYLiability)] * 100

                componyInfo.Roe = roe
                componyInfo.YOYNi = yoyni
                componyInfo.LiabilityTo = liabilityTo
                componyInfo.YOYEquity = yoyEquity
                componyInfo.YOYLiability = yoyLiability

                if roe == 0 and yoyni == 0 and liabilityTo == 0 and yoyEquity == 0 and yoyLiability == 0:
                    noneNum_quarter += 1
                if not (roe == 0 and yoyni == 0 and liabilityTo == 0 and yoyEquity == 0 and yoyLiability == 0):
                    haveNum_quarter += 1
                if roe == 0 or yoyni == 0 or liabilityTo == 0 or yoyEquity == 0 or yoyLiability == 0:
                    wrongNum_quarter += 1

            else:
                noneNum_quarter += 1




            #print(f"获取价值年度数据字符串是{todayStr},  目标年份是：{y_target_year}，    目标季度是{y_target_q}")
            catchKey = (code, y_target_year, y_target_q)
            val = self.totalValueDbDic.get(catchKey)
            if val is not None: 
                roe = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.Roe)] * 100
                yoyni = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYNi)] * 100
                liabilityTo = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.LiabilityTo)] * 100
                yoyEquity = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYEquity)] * 100
                yoyLiability = val[dbStruct.GetNameByEnum(ValueDBStruct.ColumnEnum.YOYLiability)] * 100

                componyInfo.Roe_Year = roe
                componyInfo.YOYNi_Year = yoyni
                componyInfo.LiabilityTo_Year = liabilityTo
                componyInfo.YOYEquity_Year = yoyEquity
                componyInfo.YOYLiability_Year = yoyLiability
                if roe == 0 and yoyni == 0 and liabilityTo == 0 and yoyEquity == 0 and yoyLiability == 0:
                    noneNum_year += 1
                if not (roe == 0 and yoyni == 0 and liabilityTo == 0 and yoyEquity == 0 and yoyLiability == 0):
                    haveNum_year += 1
                if roe == 0 or yoyni == 0 or liabilityTo == 0 or yoyEquity == 0 or yoyLiability == 0:
                    wrongNum_year += 1

            else:
                noneNum_year += 1
        #print("##################################################")
        
        
        #print(f"价值数据获取完毕，年报年月：{y_target_year}  {y_target_q}   季报年月{y_target_year}  {q_target_q}总股票数：{len(allCodeList)}，  年报数：{haveNum_year}  空年报数：{noneNum_year}  瑕疵年报数：{wrongNum_year}  季报数{haveNum_quarter}      空季报数：{noneNum_quarter}   瑕疵季报数：{wrongNum_quarter}")



    def ClearDic(self):
        self.totalBaseDailyData.clear()
        self.totalBaseWindowData.clear()
        self.CalculateIndustryBaseClassDic.clear()
        self.CalculateIndustryWindowClassDic.clear()
    
    def DelDicByDate(dateStr):
        pass




