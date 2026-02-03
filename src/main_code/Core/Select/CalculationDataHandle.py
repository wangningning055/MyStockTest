from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass

class BaseClass :
    def __init__(self):
        pass
    def Init(self, main):
        self.main = main
        self.totalComponyData = {}
        self.totalBaseDailyData = {}
        self.ReadDBDataInMemory()
    def ReadDBDataInMemory(self):
        print("开始载入数据库数据，这需要花上一段时间......")
        self.main.BoardCast("开始载入数据库数据，这需要花上一段时间.....")
        basicData = self.main.dbHandler.GetAllBasicData()
        #self.main.dbHandler.GetAllDailyData()
        #self.main.dbHandler.GetAllAdjustData()


        self.main.BoardCast("数据库数据载入完成")
        print("数据库数据载入完成")


    def GetBaseData(self, stockCode, dataStr):

        pass


    def GetWindowData(self, stockCode, dataStr1, dataStr2):
        pass