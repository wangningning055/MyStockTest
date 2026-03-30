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
    maxCount:int                #最大持仓数
    share : float               #占主仓比例

    startValue : float          #开仓资金
    curValue : float            #当前可用资金
    totalValue : float          #当前仓位总价值


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
    stockList : List[StockSingle.BaseClass]         #持仓列表

    stockList_history : List[StockSingle.BaseClass]         #历史持仓列表

    backStart : float           #最大回撤开始位
    backEnd : float           #最大回撤位




    
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
        self.stockList = []
        self.stockList_history = []

        self.startValue = totalStock.startValue * self.share
        self.curValue = self.startValue
        self.totalValue = self.startValue
        self.maxCount = 2
        self.curChangeRatio = 0


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




    async def ExecuteSelect(self):
        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle
        backTestHandle = self.totalStock.handler
        isOutKC = backTestHandle.isOutKC
        isOutCY = backTestHandle.isOutCY
        isOutST = backTestHandle.isOutST

        sellCodeList = []
        buyCodeList = []

        buyCodeDic_selectRes = {}
        sellCodeDic_selectRes = {}

        buySelectCodeList = self.totalStock.handler.backTestCalculationHandle.totalStockList
        sellSelectCodeList = []
        for stockSingle in self.stockList:
            state = stockSingle.GetState()
            if(state == 2 or state == 3 or state == 4):
                sellCodeList.append(stockSingle.stockCode)
            if(state == 1):
                sellSelectCodeList.append(stockSingle.stockCode)

        buyCodeDic_selectRes = main.analysisHandle.RunGetStockListByConditionForBackTest(backTestCalculationHandle, buySelectCodeList, self.buyThreshold, isOutKC, isOutCY, isOutST, self.buyCondition)



        if len(sellSelectCodeList) > 0:
            sellCodeDic_selectRes = main.analysisHandle.RunGetStockListByConditionForBackTest(backTestCalculationHandle, sellSelectCodeList, self.sellThreshold, isOutKC, isOutCY, isOutST, self.sellCondition)
        

        #买入因子结果排序
        sorted_items = sorted(buyCodeDic_selectRes.items(), key=lambda x: x[0], reverse=True)[:2]



        for buy_key, buy_val in sorted_items:
            buyCodeList.append(buy_val)


        #卖出需要全加进去
        for sell_key, sell_val in sellCodeDic_selectRes.items():
            sellCodeList.append(sell_val)

        self.buyCodeList = buyCodeList
        self.sellCodeList = sellCodeList


    async def ExecuteBuySell(self):
        #先执行卖出
        for sellCode in self.sellCodeList:
            for singleStock in self.stockList:
                if sellCode == singleStock.stockCode:
                    self.Sell(singleStock)


        #再执行买入
        for buyCode in self.buyCodeList:
            if len(self.stockList) >= self.maxCount:
                return
            self.Buy(buyCode)


    def Sell(self, singleStock:StockSingle.BaseClass):
        operate = Operate.BaseClass()
        self.operate_recorder_List.append(operate)

        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr
        stockCode = singleStock.stockCode
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)
        state = singleStock.GetState()

        operate.date = todayStr
        operate.partStock = self
        operate.stockCode = stockCode
        operate.operate = "sell"
        if cls.trade_state == 0:
            operate.isSuccess = False
            operate.failReason = "停牌无法卖出"
            return
        
        if cls.is_up_stop and cls.is_one_ban:
            operate.isSuccess = False
            operate.failReason = "跌停一字板，无法卖出"
            return
        if state == 0:
            operate.isSuccess = False
            operate.failReason = "未达到最短持仓天数，无法卖出"
            return
        

        operate.isSuccess = True
        state = singleStock.GetState()
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
        singleStock.isEnd = True


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

        self.stockList_history.append(singleStock)
        self.stockList.remove(singleStock)

        sellVal = singleStock.end_price * singleStock.volume

        self.curValue += sellVal
        operate.Log()


    def Buy(self, stockCode):
        if len(self.stockList) >= self.maxCount:
            return
        
        operate = Operate.BaseClass()
        self.operate_recorder_List.append(operate)

        main = self.totalStock.handler.main
        backTestCalculationHandle = self.totalStock.handler.backTestCalculationHandle

        todayStr = backTestCalculationHandle.todayStr

        singleStock = StockSingle.BaseClass()
        cls = backTestCalculationHandle.GetBaseDataClass(stockCode, todayStr)

        operate.date = todayStr
        operate.partStock = self
        operate.stockCode = stockCode
        operate.operate = "buy"
        if cls.trade_state == 0:
            operate.isSuccess = False
            operate.failReason = "停牌无法买入"
            return
        
        if cls.is_up_stop and cls.is_one_ban:
            operate.isSuccess = False
            operate.failReason = "涨停一字板，无法买入"
            return

        #最低买入一手的价格
        oneHandMoney = cls.close_ori * 100
        curVal = self.GetBuyVal()
        if curVal < oneHandMoney:
            operate.isSuccess = False
            operate.failReason = f"当前分仓剩余钱数不足以购买一手目标：分仓剩余：{curVal}， 目标一手价格：{oneHandMoney}"
            return
        
        handNum = curVal // oneHandMoney
        operate.isSuccess = True

        start_price = cls.close_ori
        singleStock.stockCode = stockCode
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

        self.stockList.append(singleStock)

        buyVal = handNum * 100 * start_price

        self.curValue -= buyVal
        operate.Log()


    def Update(self):
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



        todayStr = backTestCalculationHandle.todayStr




    def GetBuyVal(self):
        ratio = 1 / (self.maxCount - len(self.stockList))
        return self.curValue * ratio
    

    def LogOpera(self):
        for opera in self.operate_recorder_List:
            opera.Log()

    def Log(self):
        print(f"----更新分仓：日期：{self.totalStock.handler.backTestCalculationHandle.todayStr}， 分仓名：{self.name}， 开仓价：{self.startValue}， 当前价：{self.curValue}， 涨跌幅：{self.curChangeRatio}")