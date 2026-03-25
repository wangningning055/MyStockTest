import src.main_code.Core.BackTest.StockSingle as StockSingle
import src.main_code.Core.BackTest.Operate  as Operate
from typing import List, Optional, Callable, Dict, Any, Union
class BaseClass:
    id : int
    name : str                  #仓位名
    share : float               #占主仓比例
    startValue : float          #开仓价
    curValue : float            #当前价

    buyConditionJson : int       #买入策略
    sellConditionJson : int      #卖出策略

    buyThreshold : float         #买入阈值
    sellThreshold : float         #卖出阈值


    minContainDay : int         #最短持仓天数
    maxContainDay : int         #最长持仓天数

    stopEarn : float            #止盈位
    stopLose : float            #止损位
    
    curChangeRatio : float      #涨跌幅

    operate_recorder : List[Operate.BaseClass]      #操作记录
    stockList : List[StockSingle.BaseClass]         #持仓列表
    
    def __init__(self, single):
        self.name = single.name
        self.share = single.share
        self.buyConditionJson = single.buyConditionJson
        self.sellConditionJson = single.sellConditionJson
        self.minContainDay = single.minContainDay
        self.maxContainDay = single.maxContainDay
        self.stopEarn = single.stopEarn
        self.stopLose = single.stopLose
        self.buyThreshold = single.buyThreshold
        self.sellThreshold = single.sellThreshold


    #进行买入判断
    def CheckBuy():
        pass

    
    #进行卖出判断
    def CheckSell():
        pass

    def Buy(self):
        pass


    def Sell(self):
        pass