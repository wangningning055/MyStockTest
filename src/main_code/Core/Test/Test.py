from datetime import date, datetime, timedelta
from typing import List, Optional, Callable, Dict, Any, Union
from src.main_code.Core import Const
from src.main_code.Core.Calculate import CalculationSpecial
import time
import psutil
import os
import bisect
import random
def Stop():
      CalculationSpecial.isNeed_CalculateIndustryInfoTotal_Stop = True
async def TestCalculate(handler):
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


        #高低压力位
        #def tempLog(code, start, to):
        #    cls1 = self.totalBaseDailyData[(code, todayStr)]
        #    print("")
        #    print("")
        #    print("#####################################################################################################################################")
        #    down = CalculationSpecial.CalculateDownPressure(cls1, start, to, self)
        #    print("                    &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        #    up = CalculationSpecial.CalculateUpPressure(cls1, start, to, self)
        #    name = self.totalComponyIns.GetComponyInfo(code).Name
        #    print(f"****************************股票{code}，    {name}   压力位计算完毕， 下压力值为  {down}，  上压力值为  {up}")
        #    print("#####################################################################################################################################")
        #    print("")
        #    print("")
        #my_list = [10, 20, 30, 40, 50]
        ## 随机取2个不重复的值
        #random_items = random.sample(self.totalStockList, k=5)
        #for code in random_items:
        #    tempLog(code, 0, 40)

        
        ##价值股成长股评分
        #scoreLimit = 80
        #def tempLog(code):
        #    cls1 = self.totalBaseDailyData[(code, todayStr)]
        #    #value = CalculationSpecial.CalculateValueScore(cls1, self)
        #    value = CalculationSpecial.CalculateGrowScore(cls1, self)
        #    name = self.totalComponyIns.GetComponyInfo(code).Name
        #    industry = self.totalComponyIns.GetComponyInfo(code).Industry
        #    if(value > scoreLimit):
        #        print(f"****************************股票{code}，    {name}, 行业：{industry}   价值计算完毕， 为  {value}")
        #        #print(f"股票{code}，    {name}, 行业：{industry}")
        #    return value
        ## 随机取2个不重复的值
        #count = 0
        #for code in self.totalStockList:
        #    val = tempLog(code)
        #    if val > scoreLimit:
        #        count += 1
        #print(f"***************************价值计算完毕， 总数为  {count}")



        await CalculationSpecial.CalculateIndustryInfoTotal(handler.main)

        #print(f"#######行业总数量位：{len(indList)}")
        #for ind in indList:
        #    print(f"####行业：|{ind}|")

        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = handler.main.requestor.format_seconds(totalCostTime)
        mem_info = process.memory_info()
        rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
        vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小

        print(f"测试数据计算完毕{todayStr}, 花费的时间是：{totalCostTimeStr1} 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")