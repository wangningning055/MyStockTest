from datetime import date, datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from src.main_code.Core import Const
from src.main_code.Core.Calculate import CalculationSpecial
from src.main_code.Core.Calculate import CalculationDataHandle
import time
import numpy as np
import psutil
import os
import bisect
import random
import asyncio
def Stop():
      CalculationSpecial.isNeed_CalculateIndustryInfoTotal_Stop = True
async def TestCalculate(handler : CalculationDataHandle.BaseClass):
        main = handler.main
        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)
        todayStr = handler.GetToday()
        if todayStr == None:
            print("没有拉取数据记录，无法进行数据预热")
            handler.main.BoardCast("没有拉取数据记录，无法进行测试")
            return
        
        t0 = time.perf_counter()
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小
        print(f"开始计算测试数据：{todayStr} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")

        #基本数据
        #baseCls =  handler.GetBaseDataClass("603259.SH", "20260323")
        #baseCls =  handler.GetBaseDataClass("603258.SH", "20260323")
        #if baseCls is not None:
        #    handler.CalculateBaseClass(baseCls)

        ##窗口数据
        #windowCls =  handler.GetWindowDataClass("603259.SH","20260323", 0, 20)
        #if windowCls is not None:
        #      handler.CalculateBaseWindowClass(windowCls, windowCls.code, 0, 20)

        #高低压力位
        #def tempLog(code, start, to):
        #    cls1 = handler.totalBaseDailyData[(code, todayStr)]
        #    print("")
        #    print("")
        #    print("#####################################################################################################################################")
        #    down = CalculationSpecial.CalculateDownPressure(cls1, start, to, handler)
        #    print("                    &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        #    up = CalculationSpecial.CalculateUpPressure(cls1, start, to, handler)
        #    name = handler.totalComponyIns.GetComponyInfo(code).Name
        #    print(f"****************************股票{code}，    {name}   压力位计算完毕， 下压力值为  {down}，  上压力值为  {up}")
        #    print("#####################################################################################################################################")
        #    print("")
        #    print("")
        #my_list = [10, 20, 30, 40, 50]
        ## 随机取2个不重复的值
        #tempLog("603259.SH", 0, 60)

        #random_items = random.sample(handler.totalStockList, k=5)
        #for code in random_items:
        #    tempLog(code, 0, 40)

        
        #价值股成长股评分
        #scoreLimit = 80
        #def tempLog(code):
        #    cls1 = handler.totalBaseDailyData[(code, todayStr)]
        #    #value_value = CalculationSpecial.CalculateValueScore(cls1, self)
        #    grow_value = CalculationSpecial.CalculateGrowScore(cls1, handler)
        #    name = handler.totalComponyIns.GetComponyInfo(code).Name
        #    industry = handler.totalComponyIns.GetComponyInfo(code).Industry
        #    print(f"****************************股票{code}，    {name}, 行业：{industry}   价值计算完毕， 为  {grow_value}, {value_value}")
        #        #print(f"股票{code}，    {name}, 行业：{industry}")
        #    return value_value
        ## 随机取2个不重复的值
        #count = 0
        #for code in handler.totalStockList:
        #    val = tempLog(code)
        #    if val > scoreLimit:
        #        count += 1
        #print(f"***************************价值计算完毕， 总数为  {count}")



                
            


        #print(f"#######行业总数量位：{len(indList)}")
        #for ind in indList:
        #    print(f"####行业：|{ind}|")

        #handler.MoveDateToNextDay()
        #backTestHandle = CalculationDataHandle.BaseClass()
        #backTestHandle.Init(handler.main, "20210104")
        #await backTestHandle.DataPreheating()

        main.SetIsInHandle(True)

        #def tempLog(code):
        #    windowCls = handler.GetWindowDataClass(code, handler.todayStr, 0, 40)
        #    if windowCls is None:
        #         return
        #    downValue = windowCls.lower_tend_ratio
        #    name = handler.totalComponyIns.GetComponyInfo(code).Name
        #    industry = handler.totalComponyIns.GetComponyInfo(code).Industry

        ##随机取五个值
        #random_items = random.sample(handler.totalStockList, k=10)
        #for code in random_items:
        #    tempLog(code)

        aaa = []
        aaa.append(1)
        aaa.append(-1)
        aaa.append(1)
        aaa.append(-1.5)
        x = np.arange(len(aaa))
        y = np.array(aaa)
        slope, intercept = np.polyfit(x, y, 1)
        print(f"斜率是：{slope}")

        main.SetIsInHandle(False)

        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = handler.main.requestor.format_seconds(totalCostTime)
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小

        print(f"测试数据计算完毕{todayStr}, 花费的时间是：{totalCostTimeStr1} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")