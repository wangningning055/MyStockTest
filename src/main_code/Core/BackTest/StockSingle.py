import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.StockPart as StockPart
    import src.main_code.Core.BackTest.StockPart as StockPart

class BaseClass:
    id : int
    stockCode : str             #票子代码
    stockPart : "StockPart.BaseClass"           #所处的分仓仓位
    holdDay : int               #持仓天数
    startDate : str             #开仓日期
    endDate : str               #清仓日期
    isEnd : bool                #是否清仓
    volume : int                #持有股数
    curChangeRatio : float               #涨跌

    #开仓价
    start_price : float
    start_oriPrice_avg : float
    start_oriPrice_open : float
    start_oriPrice_close : float
    start_oriPrice_high : float
    start_oriPrice_low : float

    start_adjPrice_avg : float
    start_adjPrice_open : float
    start_adjPrice_close : float
    start_adjPrice_high : float
    start_adjPrice_low : float

    #清仓价
    end_price : float
    end_oriPrice_avg : float
    end_oriPrice_open : float
    end_oriPrice_close : float
    end_oriPrice_high : float
    end_oriPrice_low : float

    end_adjPrice_avg : float
    end_adjPrice_open : float
    end_adjPrice_close : float
    end_adjPrice_high : float
    end_adjPrice_low : float



    def __init__(self):
        self.curChangeRatio = 0
        pass


    #0 不可卖出，  1处于卖出判断区间，  2达到止损或止盈， 3 超过最大持仓天数
    def GetState(self):
        #第一步：达到止损或者止盈，需要立即卖出  2
        if self.stockPart.stopLose != 0:
            if self.curChangeRatio <= self.stockPart.stopLose:
                return 2
            
        if self.stockPart.stopEarn != 0:
            if self.curChangeRatio >= self.stockPart.stopEarn:
                return 2


        #第二部：达到最大持仓天数，需要立即卖出  3
        if self.stockPart.maxContainDay > 0:
            if self.holdDay >= self.stockPart.maxContainDay:
                return 3

        #第三部：没有到最短持仓天数，不可卖出    0
        if self.stockPart.minContainDay > 0:
            if self.holdDay <= self.stockPart.minContainDay:
                return 0

        #最后： 未达止损止盈，达到最短天但没到最长天， 在卖出判断区间：     1
        return 1

    def Update(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = self.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)
        nowPrice = cls.close_ori

        self.curChangeRatio = ((nowPrice - self.start_price) / self.start_price) * 100
        self.holdDay += 1

    #获取当前仓位总价值
    def GetValue(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = self.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)
        nowPrice = cls.close_ori
        return nowPrice * self.volume

