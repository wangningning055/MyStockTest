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
    curValue : float              #当前仓位总价值
    maxHistoryValue : float          #历史上达到的最高价

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


    isInBack : bool            #是否处在回测判断时间


    def __init__(self):
        self.curChangeRatio = 0
        self.isInBack = False
        self.maxHistoryValue = 0
        self.curValue = 0
        self.holdDay = 0
        self.startDate = ""
        self.endDate = ""
        pass


    #0 不可卖出，  1处于卖出判断区间，  2达到止损或止盈， 3 超过最大持仓天数， 4达到最大回撤
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
            
        #第四步：达到最大回撤
        if self.isInBack:
            if self.GetBack() <= self.stockPart.backEnd:
                return 4

        #最后： 未达止损止盈，达到最短天但没到最长天， 在卖出判断区间：     1
        return 1

    def Update(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = self.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)
        if cls != None:
            if cls.trade_state != 0:
                nowPrice = cls.close_ori


                if nowPrice * self.volume > self.maxHistoryValue:
                    self.maxHistoryValue = nowPrice * self.volume


                self.curChangeRatio = ((nowPrice - self.start_price) / self.start_price) * 100
                self.curValue = nowPrice * self.volume


                if self.isInBack == False and self.stockPart.backEnd != 0:
                    if self.curChangeRatio >= partStock.backStart:
                        self.isInBack = True


        self.holdDay += 1

    #获取当前仓位总价值
    def GetValue(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = self.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)
        if cls == None:
            return self.curValue
        nowPrice = cls.close_ori
        return nowPrice * self.volume
    

    #获取回撤
    def GetBack(self):
        ratio = ((self.GetValue() - self.maxHistoryValue) / self.maxHistoryValue) * 100
        return ratio

