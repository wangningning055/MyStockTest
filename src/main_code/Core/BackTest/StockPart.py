import src.main_code.Core.BackTest.StockSingle as StockSingle
import src.main_code.Core.BackTest.Operate  as Operate
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from typing import List, Optional, Callable, Dict, Any, Union
import src.main_code.Core.Select.Models as Models
import numpy as np
from dataclasses import dataclass, field, asdict
from datetime import datetime

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.StockTotal as StockTotal

class BaseClass:
    id : int
    name : str                  #仓位名
    maxCount:int                #最大持仓数
    share : float               #占主仓比例

    startValue : float          #开仓资金
    curValue : float            #当前可用资金
    totalValue : float          #当前仓位总价值
    lastVal : int                                   #昨日价


    buyCondition : List[Models.FactorConfig]       #买入策略
    sellCondition : List[Models.FactorConfig]      #卖出策略

    buyThreshold : float         #买入阈值
    sellThreshold : float         #卖出阈值


    minContainDay : int         #最短持仓天数
    maxContainDay : int         #最长持仓天数

    stopEarn : float            #止盈位
    stopLose : float            #止损位
    
    curChangeRatio : float      #涨跌幅

    
    buyCodeList : Dict[float ,str]  #买入列表
    sellCodeList : Dict[float ,str] #卖出列表

    operate_recorder_List : List[Operate.BaseClass]      #操作记录
    newOperate_recorder_List : List[Operate.BaseClass]      #新的操作记录

    
    stockList : List[StockSingle.BaseClass]         #持仓列表

    stockList_history : List[StockSingle.BaseClass]         #历史持仓列表

    backStart : float           #最大回撤开始位
    backEnd : float           #最大回撤位


    changeRatioList : List[float]                   #涨跌列表记录，用于计算波动率
    lastUpVal : float                               #上次涨的时候的价格，用于计算最大回撤
    maxReturn : float                               #最大回撤记录
    changeRatioCurve : BackTestMsgDataStruct.EquityCurve      #用于前端显示的曲线列表记录



    
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

        self.backStart = single.drawdownStartPercent
        self.backEnd = single.maxDrawdownPercent

        self.buyCodeList = {}
        self.sellCodeList = {}

        self.operate_recorder_List = []
        self.newOperate_recorder_List = []
        self.stockList = []
        self.stockList_history = []


        self.startValue = totalStock.startValue * self.share
        self.curValue = self.startValue
        self.totalValue = self.startValue
        self.maxCount = self.curValue // 30000
        if self.curValue % 30000 >= 10000:
            self.maxCount += 1
        self.curChangeRatio = 0

        self.changeRatioList = []
        self.maxReturn = 0
        self.lastUpVal = self.curValue
        self.lastVal = self.curValue

        self.changeRatioCurve = BackTestMsgDataStruct.EquityCurve()

        #print("=====================================================")
        #print(f"名字：{self.name}")
        #print(f"占比：{self.share}")
        #print(f"止损：{self.stopLose}")
        #print(f"止盈：{self.stopEarn}")
        #print(f"最长天：{self.maxContainDay}")
        #print(f"最短天：{self.minContainDay}")
        #print(f"买因子：{self.buyThreshold}")
        #print(f"卖因子：{self.sellThreshold}")



    def GetBuyCondition(self):
        return self.buyCondition, self.buyThreshold
    
    def GetSellCondition(self):
        return self.buyCondition, self.sellThreshold



    async def ExecuteBuySelect(self):
        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle
        backTestHandle = self.totalStock.handler
        isOutKC = backTestHandle.isOutKC
        isOutCY = backTestHandle.isOutCY
        isOutST = backTestHandle.isOutST

        buyCodeList = []

        buyCodeDic_selectRes = {}

        #当前处在满仓状态，不需要选股
        if(len(self.stockList) >= self.maxCount):
            return
        

        #移出已经持仓的股票和已经在卖出列表里的股票
        buySelectCodeList = self.totalStock.handler.backTestCalculationHandle.totalStockList.copy()
        for singleStock in self.stockList:
            if singleStock.stockCode in buySelectCodeList:
                buySelectCodeList.remove(singleStock.stockCode)
        
        for stockCode in self.sellCodeList:
            if stockCode in buySelectCodeList:
                buySelectCodeList.remove(stockCode)


        buyCodeDic_selectRes = main.analysisHandle.RunGetStockListByConditionForBackTest(backTestCalculationHandle, buySelectCodeList, self.buyThreshold, isOutKC, isOutCY, isOutST, self.buyCondition)


        #买入因子结果排序
        sorted_items = sorted(buyCodeDic_selectRes.items(), key=lambda x: x[0], reverse=True)[:2]

        for buy_key, buy_val in sorted_items:
            buyCodeList.append(buy_val)

        self.buyCodeList = buyCodeList


    async def ExecuteBuy(self):
        if len(self.stockList) >= self.maxCount:
                return
        #再执行买入
        for buyCode in self.buyCodeList:
            if len(self.stockList) >= self.maxCount:
                return
            success = self.Buy(buyCode)
            if success == True:
                break



    async def ExecuteSellSelect(self):
        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle
        backTestHandle = self.totalStock.handler
        isOutKC = backTestHandle.isOutKC
        isOutCY = backTestHandle.isOutCY
        isOutST = backTestHandle.isOutST

        sellCodeList = []

        sellCodeDic_selectRes = {}

        sellSelectCodeList = []
        for stockSingle in self.stockList:
            state = stockSingle.GetState()
            if(state == 2 or state == 3 or state == 4):
                sellCodeList.append(stockSingle.stockCode)
            if(state == 1):
                sellSelectCodeList.append(stockSingle.stockCode)


        if len(sellSelectCodeList) > 0:
            sellCodeDic_selectRes = main.analysisHandle.RunGetStockListByConditionForBackTest(backTestCalculationHandle, sellSelectCodeList, self.sellThreshold, isOutKC, isOutCY, isOutST, self.sellCondition)
        
        #卖出需要全加进去
        for sell_key, sell_val in sellCodeDic_selectRes.items():
            sellCodeList.append(sell_val)

        self.sellCodeList = sellCodeList


    async def ExecuteSell(self):
        await self.ExecuteSellSelect()

        for sellCode in self.sellCodeList:
            for singleStock in self.stockList:
                if sellCode == singleStock.stockCode:
                    self.Sell(singleStock)


    def Sell(self, singleStock:StockSingle.BaseClass, isForce = False):
        operate = Operate.BaseClass()
        self.operate_recorder_List.append(operate)
        self.newOperate_recorder_List.append(operate)

        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = singleStock.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(stockCode, todayStr)
        componyCls = backTestCalculationHandle.totalComponyIns.GetComponyInfo(stockCode)
        state = singleStock.GetState()

        operate.date = todayStr
        operate.partStock = self
        operate.stockCode = stockCode
        operate.operate = "sell"
        operate.stockName = componyCls.Name
        if cls == None:
            print(f"卖出错误，尝试卖出：{componyCls.Name}， 日期是：{todayStr}， 日期列表是：{backTestCalculationHandle.totalDateList}")
        if cls.trade_state == 0 and isForce == False:
            operate.isSuccess = False
            operate.failReason = "停牌无法卖出"
            return
        
        if cls.is_up_stop and cls.is_one_ban and isForce == False:
            operate.isSuccess = False
            operate.failReason = "跌停一字板，无法卖出"
            return
        
        if state == 0 and isForce == False:
            operate.isSuccess = False
            operate.failReason = "未达到最短持仓天数，无法卖出"
            return
        

        operate.isSuccess = True
        state = singleStock.GetState()
        if isForce:
            operate.successReason = "回测结束强制卖出"
        else:
            if state == 1:
                operate.successReason = "达成卖出条件判断"
            if state == 2:
                operate.successReason = "达成止损位或止盈位"
            if state == 3:
                operate.successReason = "达成最大持仓天数"
            if state == 4:
                operate.successReason = "达到最大回撤"

        end_price = cls.close_ori
        singleStock.isEnd = True
        singleStock.endDate = todayStr
        singleStock.end_price = cls.close_ori


        singleStock.end_oriPrice_avg   = cls.avg_ori
        singleStock.end_oriPrice_open  = cls.open_ori
        singleStock.end_oriPrice_close = cls.close_ori
        singleStock.end_oriPrice_high  = cls.high_ori
        singleStock.end_oriPrice_low   = cls.low_ori

        singleStock.end_adjPrice_avg   = cls.avg
        singleStock.end_adjPrice_open  = cls.open
        singleStock.end_adjPrice_close = cls.close
        singleStock.end_adjPrice_high  = cls.high
        singleStock.end_adjPrice_low   = cls.low


        operate.sell_price_start = singleStock.start_price
        operate.buy_date = singleStock.startDate
        operate.sell_date = todayStr
        operate.sell_price_end = singleStock.end_price
        operate.buy_volume = singleStock.volume
        operate.kline_data = singleStock.kline_data

        singleStock.End()
        self.stockList_history.append(singleStock)
        self.stockList.remove(singleStock)

        sellVal = singleStock.end_price * singleStock.volume

        #印花税默认按五块钱算
        self.curValue += (sellVal - 5)


        operate.Log()


    def Buy(self, stockCode):
        operate = Operate.BaseClass()
        self.operate_recorder_List.append(operate)
        self.newOperate_recorder_List.append(operate)

        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr

        singleStock = StockSingle.BaseClass()
        cls = backTestCalculationHandle.GetBaseDataClass_WithTradeState(stockCode, todayStr)
        componyCls = backTestCalculationHandle.totalComponyIns.GetComponyInfo(stockCode)

        operate.date = todayStr
        operate.partStock = self
        operate.stockCode = stockCode
        operate.stockName = componyCls.Name

        operate.operate = "buy"
        if cls.trade_state == 0:
            operate.isSuccess = False
            operate.failReason = "停牌无法买入"
            return False
        
        if cls.is_up_stop and cls.is_one_ban:
            operate.isSuccess = False
            operate.failReason = "涨停一字板，无法买入"
            return False

        #最低买入一手的价格
        oneHandMoney = cls.close_ori * 100
        curVal = self.GetBuyVal()
        if curVal < oneHandMoney:
            operate.isSuccess = False
            operate.failReason = f"当前分仓剩余钱数不足以购买一手目标：分仓剩余：{curVal}， 目标一手价格：{oneHandMoney}"
            return False
        
        handNum = curVal // oneHandMoney
        operate.isSuccess = True

        start_price = cls.close_ori
        singleStock.stockCode = stockCode
        singleStock.stockName = componyCls.Name
        singleStock.start_price = cls.close_ori
        singleStock.volume = handNum * 100
        singleStock.holdDay = 0
        singleStock.stockPart = self
        singleStock.startDate = todayStr
        singleStock.isEnd = False


        singleStock.start_oriPrice_avg   = cls.avg_ori
        singleStock.start_oriPrice_open  = cls.open_ori
        singleStock.start_oriPrice_close = cls.close_ori
        singleStock.start_oriPrice_high  = cls.high_ori
        singleStock.start_oriPrice_low   = cls.low_ori

        singleStock.start_adjPrice_avg   = cls.avg
        singleStock.start_adjPrice_open  = cls.open
        singleStock.start_adjPrice_close = cls.close
        singleStock.start_adjPrice_high  = cls.high
        singleStock.start_adjPrice_low   = cls.low


        operate.buy_price = start_price
        operate.buy_date = todayStr
        operate.buy_volume = handNum * 100

        singleStock.StartRecorderKLine()

        self.stockList.append(singleStock)

        buyVal = handNum * 100 * start_price

        self.curValue -= buyVal


        operate.Log()
        return True


    def Update(self, date):
        for singleStock in self.stockList:
            singleStock.Update()

        startValue = self.startValue
        nowValue = self.curValue
        for singleStock in self.stockList:
            nowValue += singleStock.GetValue()
        self.totalValue = nowValue



        self.curChangeRatio = ((self.totalValue - self.startValue) / self.startValue) * 100


        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle


        #计算回撤
        lastChange = (self.totalValue - self.lastVal) / self.lastVal
        self.changeRatioList.append(lastChange)
        if lastChange > 0:
            self.lastUpVal = self.totalValue
        else:
            ratio = (self.totalValue - self.lastUpVal) / self.lastUpVal
            self.changeRatioCurve.drawdown.append(ratio)
            if abs(ratio) > abs(self.maxReturn):
                self.maxReturn = ratio * 100
        self.lastVal = self.totalValue
                
        #构造曲线数据
        dt = datetime.strptime(date, "%Y%m%d")
        self.changeRatioCurve.dates.append(dt.strftime("%Y-%m-%d"))
        self.changeRatioCurve.returns.append(self.curChangeRatio)
        self.changeRatioCurve.equity.append(self.totalValue)

        dailyList = []
        for singleStock in self.stockList:
            position = BackTestMsgDataStruct.Position()
            position.code = singleStock.stockCode
            position.name = singleStock.stockName
            position.shares = singleStock.volume
            dailyList.append(position)

        self.changeRatioCurve.positions.append(dailyList)
        self.changeRatioCurve.equity.append


        todayStr = backTestCalculationHandle.todayStr
        for historyStock  in self.stockList_history:
            historyStock.UpdateRecorderKLine()



    #清空仓位，立即卖出，用以计算结果
    def CleanStock(self):
        print(f"执行彻底清仓，仓位数：{len(self.stockList)}")
        while(len(self.stockList) > 0):
            self.Sell(self.stockList[0], True)

        self.totalValue = self.curValue
        self.curChangeRatio = ((self.totalValue - self.startValue) / self.startValue) * 100
        self.changeRatioList.append(self.curChangeRatio / 100)

    #获取当前可使用的分仓价
    def GetBuyVal(self):
        ratio = 1 / (self.maxCount - len(self.stockList))
        return self.curValue * ratio
    

    #获取当前分仓胜率, 只考虑已完成的交易
    def GetSuccessRatio(self):
        totalCount = 0
        successCount = 0
        for singleStock in self.stockList_history:
            totalCount += 1
            if singleStock.curChangeRatio > 0:
                successCount += 1
        return successCount / totalCount
    
    #获得成交笔数
    def GetTotalDealCount(self):
        return len(self.stockList_history)
        

    def GetResult(self):
        #平均日收益率
        avgRatio = 0
        avgRatio = self.curChangeRatio / self.totalStock.holdDay
        
        #平均日波动率
        daily_volatility = np.std(self.changeRatioList)

         #名称
        name = self.name

        #初始仓价
        startVal = self.startValue

        #当前仓价
        curVal = self.curValue

        #总收益率
        changeRatio = self.curChangeRatio

        #胜率
        totalCount = 0
        successCount = 0
        for singleStock in self.stockList_history:
            totalCount += 1
            if singleStock.curChangeRatio > 0:
                successCount += 1

        successRatio = (successCount / totalCount) * 100


        #平均年化收益率
        yearAvgRatio = avgRatio * 252
      

        #年化波动率
        year_volatility = daily_volatility * np.sqrt(252)

        #平均月化收益率
        monthAvgRatio = avgRatio * 22


        #月化波动率
        month_volatility = daily_volatility * np.sqrt(22)

        #最大回撤
        maxReturn = self.maxReturn

        #夏普比率
        sharpe = yearAvgRatio / (year_volatility * 100) if year_volatility != 0 else 0

        #成交笔数
        totalDealCount = totalCount

        divisionStock = BackTestMsgDataStruct.DivisionResult()

        #构造基本数据
        divisionStock.division_name = self.name
        totalSummary = BackTestMsgDataStruct.TradeSummary()

        totalSummary.initial_fund = startVal
        totalSummary.final_fund = curVal
        totalSummary.total_return = changeRatio
        totalSummary.win_rate = successRatio
        totalSummary.annual_return = yearAvgRatio
        totalSummary.annual_volatility = year_volatility * 100
        totalSummary.monthly_return = monthAvgRatio
        totalSummary.monthly_volatility = month_volatility * 100
        totalSummary.max_drawdown = maxReturn
        totalSummary.sharpe_ratio = sharpe

        divisionStock.summary = asdict(totalSummary)

        tradeRecorderList = []
        count = 0
        #构造收益率曲线
        for operate in self.operate_recorder_List:
            if operate.operate == "buy" and operate.isSuccess == True:
                
                dt = datetime.strptime(operate.buy_date, "%Y%m%d")
                operate_date = dt.strftime("%Y-%m-%d")
                marker = BackTestMsgDataStruct.TradeMarker()
                marker.date = operate_date
                marker.code = operate.stockCode
                marker.name = operate.stockName
                marker.price = operate.buy_price
                marker.equity = operate.curPartStockValue
        
                self.changeRatioCurve.buy_markers.append(marker)


            elif operate.operate == "sell" and operate.isSuccess == True:
                count +=1
                dt = datetime.strptime(operate.sell_date, "%Y%m%d")
                operate_date = dt.strftime("%Y-%m-%d")
                marker = BackTestMsgDataStruct.TradeMarker()
                marker.date = operate_date
                marker.code = operate.stockCode
                marker.name = operate.stockName
                marker.price = operate.sell_price_end
                marker.equity = operate.curPartStockValue 
                self.changeRatioCurve.sell_markers.append(marker)

                dt_buy = datetime.strptime(operate.buy_date, "%Y%m%d")
                buy_date = dt_buy.strftime("%Y-%m-%d")

                dt_sell = datetime.strptime(operate.sell_date, "%Y%m%d")
                sell_date = dt_sell.strftime("%Y-%m-%d")


                tradeRecorder = BackTestMsgDataStruct.TradeRecord()
                tradeRecorder.trade_id = count
                tradeRecorder.buy_date = buy_date
                tradeRecorder.sell_date = sell_date
                tradeRecorder.hold_days = (dt_sell - dt_buy).days
                tradeRecorder.code = operate.stockCode
                tradeRecorder.name = operate.stockName
                tradeRecorder.buy_price = operate.sell_price_start
                tradeRecorder.sell_price = operate.sell_price_end
                tradeRecorder.sellReason = operate.successReason

                profitMoney = (operate.sell_price_end - operate.sell_price_start) * operate.buy_volume
                profit = (operate.sell_price_end - operate.sell_price_start) / operate.sell_price_start
                tradeRecorder.profit_pct = profit * 100
                tradeRecorder.profit_money = profitMoney
                tradeRecorder.kline_data = asdict(operate.kline_data)
                tradeRecorderList.append(asdict(tradeRecorder))
                
        divisionStock.equity_curve = asdict(self.changeRatioCurve)
        divisionStock.trades = tradeRecorderList
        return asdict(divisionStock)





    def LogOpera(self):
        for opera in self.operate_recorder_List:
            opera.Log()

    def Log(self):
        print(f"----更新分仓：日期：{self.totalStock.handler.backTestCalculationHandle.todayStr}， 分仓名：{self.name}， 开仓价：{self.startValue}， 当前价：{self.totalValue}， 涨跌幅：{self.curChangeRatio}")