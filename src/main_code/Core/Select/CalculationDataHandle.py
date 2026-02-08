from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
class BaseClass :
    def __init__(self):
        pass
    def Init(self, main):
        self.main = main
        self.totalComponyData = {}
        self.totalBaseDailyData = {}
        #self.ReadDBDataInMemory()
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


    def GetBaseData(self, stockCode, dataStr):

        pass


    def GetWindowData(self, stockCode, dataStr1, dataStr2):
        pass