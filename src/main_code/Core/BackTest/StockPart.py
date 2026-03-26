import src.main_code.Core.BackTest.StockSingle as StockSingle
import src.main_code.Core.BackTest.Operate  as Operate
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from typing import List, Optional, Callable, Dict, Any, Union
import src.main_code.Core.Select.Models as Models

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.StockTotal as StockTotal

class BaseClass:
    id : int
    name : str                  #仓位名
    share : float               #占主仓比例
    startValue : float          #开仓价
    curValue : float            #当前价

    buyCondition : List[Models.FactorConfig]       #买入策略
    sellCondition : List[Models.FactorConfig]      #卖出策略

    buyThreshold : float         #买入阈值
    sellThreshold : float         #卖出阈值


    minContainDay : int         #最短持仓天数
    maxContainDay : int         #最长持仓天数

    stopEarn : float            #止盈位
    stopLose : float            #止损位
    
    curChangeRatio : float      #涨跌幅

    operate_recorder : List[Operate.BaseClass]      #操作记录
    stockList : List[StockSingle.BaseClass]         #持仓列表
    
    def __init__(self, single : BackTestMsgDataStruct.Msg_PartStock, totalStock : "StockTotal.BaseClass"):
        self.totalStock = totalStock
        self.id = single.id
        self.name = single.name
        self.share = single.weight
        self.buyCondition = single.buyConfigTree
        self.sellCondition = single.sellConfigTree
        self.minContainDay = single.holdingTimeMin
        self.maxContainDay = single.holdingTimeMax
        self.stopEarn = single.takeProfitPercent
        self.stopLose = single.stopLossPercent
        self.buyThreshold = single.thresholdBuy
        self.sellThreshold = single.thresholdSell
        print("=====================================================")
        print(f"名字：{self.name}")
        print(f"占比：{self.share}")
        print(f"止损：{self.stopLose}")
        print(f"止盈：{self.stopEarn}")
        print(f"最长天：{self.maxContainDay}")
        print(f"最短天：{self.minContainDay}")
        print(f"买因子：{self.buyThreshold}")
        print(f"卖因子：{self.sellThreshold}")



    def GetBuyCondition(self):
        return self.buyCondition, self.buyThreshold
    
    def GetSellCondition(self):
        return self.buyCondition, self.sellThreshold




    async def ExecuteSelect(self):
        main = self.totalStock.handler.main
        buyCodeList = self.totalStock.handler.backTestCalculationHandle.totalStockList
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle

        backTestHandle = self.totalStock.handler
        isOutKC = backTestHandle.isOutKC
        isOutCY = backTestHandle.isOutCY
        isOutST = backTestHandle.isOutST
        main.analysisHandle.RunGetStockListByConditionForBackTest(backTestCalculationHandle, buyCodeList, self.buyThreshold, isOutKC, isOutCY, isOutST, self.buyCondition)



    async def ExecuteBuySell(self):
        pass