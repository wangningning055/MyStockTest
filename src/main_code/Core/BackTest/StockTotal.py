import src.main_code.Core.BackTest.StockPart as StockPart
from typing import List, Optional, Callable, Dict, Any, Union
class BaseClass:
    partList : Dict[str, StockPart.BaseClass]        #分仓列表
    startValue : int                                #开仓价
    curValue : int                                  #当前价
    changeRatio : float                             #涨跌幅
    def __init__(self, handler):
        self.total_part_share = 1
        self.handler = self.handler
        self.partList = {}
        pass
    def InitByJson(self, json):
        #这里解析json,解析出partList
        self.startValue = 100000
        self.curValue = 100000
        self.changeRatio = 0
        partList = []

        for single in partList:
            self.total_part_share -= single.share
            if(self.total_part_share < 0):
                print("分仓比例大于1，不正确，仓位初始化失败")
                self.handler.main.BoardCast("分仓比例大于1，不正确，仓位初始化失败")
                return False
            cls = self.CreatePart(single)
            self.partList[single.name] = cls
        return True
    def CreatePart(single):
        part = StockPart.BaseClass(single)
        return part
    
    def CheckBySell(self):
        pass