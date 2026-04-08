import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from datetime import datetime

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.StockPart as StockPart
    import src.main_code.Core.BackTest.StockPart as StockPart

class BaseClass:
    id : int
    stockCode : str             #票子代码
    stockName : str
    stockPart : "StockPart.BaseClass"           #所处的分仓仓位
    holdDay : int               #持仓天数
    startDate : str             #开仓日期
    endDate : str               #清仓日期
    isEnd : bool                #是否清仓
    volume : int                #持有股数
    curChangeRatio : float               #涨跌
    curValue : float              #当前仓位总价值
    maxHistoryValue : float          #历史上达到的最高价
    kline_data : BackTestMsgDataStruct.KlineData    #K线图
    kline_data_stopRecorderCount : int    #K线图结尾记录
    isEndUpdateKLine : bool


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
        self.kline_data = BackTestMsgDataStruct.KlineData()
        self.isEnd = False
        self.kline_data_stopRecorderCount = 0
        self.isEndUpdateKLine = False
        pass

    def StartRecorderKLine(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle
        todayStr = backTestCalculationHandle.todayStr
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(self.stockCode, todayStr)
        count = 0
        for singleCls in cls.dataList_240:
            #if count > 120:
            #    break
            count += 1
            dt = datetime.strptime(singleCls.trade_date, "%Y%m%d")
            date = dt.strftime("%Y-%m-%d")
            priceList = []
            priceList.append(singleCls.open)
            priceList.append(singleCls.close)
            priceList.append(singleCls.low)
            priceList.append(singleCls.high)
            priceList.append(singleCls.change_Ratio)

            volume = singleCls.volume            #手


            self.kline_data.dates.insert(0, date)
            self.kline_data.ohlc.insert(0, priceList)
            self.kline_data.volumes.insert(0, volume)
    
    def UpdateRecorderKLine(self):
        if self.isEndUpdateKLine == True:
            return
        if self.isEnd == True:
            self.kline_data_stopRecorderCount += 1
            
        if self.kline_data_stopRecorderCount > 240:
            self.isEndUpdateKLine = True
            return

        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle
        todayStr = backTestCalculationHandle.todayStr
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(self.stockCode, todayStr)
        if cls == None:
            self.isEndUpdateKLine = True
            return
        if cls.trade_state == 0:
            return
        dt = datetime.strptime(cls.trade_date, "%Y%m%d")
        date = dt.strftime("%Y-%m-%d")
        if date in self.kline_data.dates:
            return
        priceList = []
        priceList.append(cls.open)
        priceList.append(cls.close)
        priceList.append(cls.low)
        priceList.append(cls.high)
        priceList.append(cls.change_Ratio)

        volume = cls.volume           #万手

        self.kline_data.dates.append(date)
        self.kline_data.ohlc.append(priceList)
        self.kline_data.volumes.append(volume)






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
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(stockCode, todayStr)
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

        self.UpdateRecorderKLine()
        self.holdDay += 1

    #清仓卖出
    def End(self):
        self.curChangeRatio = ((self.end_price - self.start_price) / self.start_price) * 100
        self.curValue = self.end_price * self.volume
        self.isEnd = True

    #获取当前仓位总价值
    def GetValue(self):
        partStock = self.stockPart
        main = partStock.totalStock.handler.main
        backTestCalculationHandle = partStock.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = self.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(stockCode, todayStr)
        if cls == None:
            return self.curValue
        nowPrice = cls.close_ori
        return nowPrice * self.volume
    

    #获取回撤
    def GetBack(self):
        ratio = ((self.GetValue() - self.maxHistoryValue) / self.maxHistoryValue) * 100
        return ratio

