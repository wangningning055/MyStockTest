import src.main_code.Core.BackTest.StockPart as StockPart
from typing import List, Optional, Callable, Dict, Any, Union
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field, asdict
# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.BackTestHandler as BackTestHandler

class BaseClass:
    name:str                                        #仓名
    partList : Dict[str, StockPart.BaseClass]        #分仓列表
    startValue : int                                #开仓价
    curValue : int                                  #当前价
    lastVal : int                                   #昨日价
    changeRatio : float                             #涨跌幅

    holdDay : int                                 #持仓天数（按交易日）


    changeRatioList : List[float]                   #涨跌列表记录，用于计算波动率
    lastUpVal : float                               #上次涨的时候的价格，用于计算最大回撤
    maxReturn : float                               #最大回撤记录

    changeRatioCurve : BackTestMsgDataStruct.EquityCurve      #用于前端显示的曲线列表记录

    def __init__(self, handler):
        self.total_part_share = 0
        self.handler : "BackTestHandler.BaseClass" = handler
        self.partList = {}
        pass
    def Init(self, config : BackTestMsgDataStruct.Msg_TotalStock):
        self.startValue = config.initialFund
        self.curValue = config.initialFund
        self.changeRatio = 0
        self.name = "总仓"
        self.holdDay = 0
        self.changeRatioList = []
        self.maxReturn = 0
        self.lastUpVal = self.curValue
        self.lastVal = self.curValue

        self.changeRatioCurve = BackTestMsgDataStruct.EquityCurve()

        for single in config.divisions:
            if(len(single.buyConfigTree) <= 0):
                print(f"分仓{single.name}的买入策略为空，跳过")
                self.handler.main.BoardCast(f"分仓{single.name}的买入策略为空，跳过")
                continue
            
            if(len(single.sellConfigTree) <= 0  and(single.holdingTimeMax == 0 and single.stopLossPercent == 0 and single.takeProfitPercent == 0)):
                print(f"分仓{single.name}的卖出策略为空，跳过")
                self.handler.main.BoardCast(f"分仓{single.name}的卖出策略为空，跳过")
                continue


            self.total_part_share += single.weight

            if(single.weight <= 0):
                print(f"分仓{single.name}的占比小于等于1，不正确，仓位初始化失败")
                self.handler.main.BoardCast(f"分仓{single.name}的占比小于等于1，不正确，仓位初始化失败")
                return False

            if(self.total_part_share > 1):
                print(f"分仓加起来的比例大于1，不正确，仓位初始化失败")
                self.handler.main.BoardCast(f"分仓加起来的比例大于1，不正确，仓位初始化失败")
                return False
            cls = self.CreatePart(single)
            self.partList[single.name] = cls
        if len(self.partList) <= 0:
            print("有效仓位数为0， 初始化失败")
            self.handler.main.BoardCast(f"有效仓位数为0， 初始化失败")
            return False
        return True
    


    def CreatePart(self, single):
        part = StockPart.BaseClass(single, self)
        return part
    


    async def ExecuteBuy(self):
        for key, part in self.partList.items():
            await part.ExecuteBuy()

    async def ExecuteSell(self):
        for key, part in self.partList.items():
            await part.ExecuteSell()

    #更新
    def UpdateStock(self, date):
        for key, part in self.partList.items():
            part.Update(date)
        cur = 0
        if self.total_part_share < 1:
            cur = self.startValue * (1 - self.total_part_share) 
        for key, part in self.partList.items():
            cur += part.totalValue

        self.curValue = cur
        self.changeRatio = ((self.curValue - self.startValue) / self.startValue) * 100
        self.changeRatioList.append(self.changeRatio)
        #计算回撤
        lastChange = (self.curValue - self.lastVal) / self.lastVal
        if lastChange > 0:
            self.lastUpVal = self.curValue
        else:
            ratio = (self.curValue - self.lastUpVal) / self.lastUpVal
            self.changeRatioCurve.drawdown.append(ratio)
            if abs(ratio) > abs(self.maxReturn):
                self.maxReturn = ratio * 100
        self.lastVal = self.curValue
                
        #构造曲线数据
        dt = datetime.strptime(date, "%Y%m%d")
        self.changeRatioCurve.dates.append(dt.strftime("%Y-%m-%d"))
        self.changeRatioCurve.returns.append(self.changeRatio)
        self.changeRatioCurve.equity.append(self.curValue)

        dailyList = []
        for key, part in self.partList.items():
            for singleStock in part.stockList:
                position = BackTestMsgDataStruct.Position()
                position.code = singleStock.stockCode
                position.name = singleStock.stockName
                position.shares = singleStock.volume
                dailyList.append(position)

        self.changeRatioCurve.positions.append(dailyList)
        self.changeRatioCurve.equity.append
        

        #更新操作时的仓价
        for key, part in self.partList.items():
            for newOperate in part.newOperate_recorder_List:
                newOperate.curTotalStockValue = self.curValue
                newOperate.curPartStockValue = part.totalValue
        for key, part in self.partList.items():
            part.newOperate_recorder_List.clear()


        self.Log()



        self.holdDay += 1


    #获取最终的回测结果
    def GetResult(self, day):
        #立即清空仓位
        for key, stockPart in self.partList.items():
            stockPart.CleanStock()
        self.UpdateStock(day)

        #平均日收益率
        avgRatio = 0
        if len(self.changeRatioList) > 0:
            addCount = 0
            for ratio in self.changeRatioList:
                addCount += 1
            avgRatio = self.changeRatio / addCount
        #平均日波动率
        daily_volatility = np.std(self.changeRatioList)

         #名称
        name = self.name

        #初始仓价
        startVal = self.startValue

        #当前仓价
        curVal = self.curValue

        #总收益率
        changeRatio = self.changeRatio

        #胜率
        totalCount = 0
        successCount = 0
        for key, stockPart in self.partList.items():
            for singleStock in stockPart.stockList_history:
                totalCount += 1
                if singleStock.curChangeRatio > 0:
                    successCount += 1

        successRatio = (successCount / totalCount)*100


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
        sharpe = yearAvgRatio / year_volatility if year_volatility != 0 else 0

        #成交笔数
        totalDealCount = totalCount

        #创建结果
        res = BackTestMsgDataStruct.BacktestResult()
        totalStock = BackTestMsgDataStruct.DivisionResult()
        res.divisions = {}

        #构造基本数据
        totalStock.division_name = self.name
        totalSummary = BackTestMsgDataStruct.TradeSummary()

        totalSummary.initial_fund = startVal
        totalSummary.final_fund = curVal
        totalSummary.total_return = changeRatio
        totalSummary.win_rate = successRatio
        totalSummary.annual_return = yearAvgRatio
        totalSummary.annual_volatility = year_volatility
        totalSummary.monthly_return = monthAvgRatio
        totalSummary.monthly_volatility = month_volatility
        totalSummary.max_drawdown = maxReturn
        totalSummary.sharpe_ratio = sharpe

        totalStock.summary = asdict(totalSummary)

        tradeRecorderList = []
        count_sell = 0
        count_buy = 0
        #构造收益率曲线
        for key, stockPart in self.partList.items():
            for operate in stockPart.operate_recorder_List:
                if operate.operate == "buy" and operate.isSuccess == True:
                    print(f"++++++++创建买入结果：名字：{operate.stockName}， 买入日期：{operate.buy_date}")
                    count_buy += 1
                    dt = datetime.strptime(operate.buy_date, "%Y%m%d")
                    operate_date = dt.strftime("%Y-%m-%d")
                    marker = BackTestMsgDataStruct.TradeMarker()
                    marker.date = operate_date
                    marker.code = operate.stockCode
                    marker.name = operate.stockName
                    marker.price = operate.buy_price
                    marker.equity = operate.curTotalStockValue
                    self.changeRatioCurve.buy_markers.append(marker)

                if operate.operate == "sell" and operate.isSuccess == True:
                    count_sell +=1
                    print(f"--------创建卖出结果：名字：{operate.stockName}， 卖出日期：{operate.sell_date}")
                    dt = datetime.strptime(operate.sell_date, "%Y%m%d")
                    operate_date = dt.strftime("%Y-%m-%d")
                    marker = BackTestMsgDataStruct.TradeMarker()
                    marker.date = operate_date
                    marker.code = operate.stockCode
                    marker.name = operate.stockName
                    marker.price = operate.sell_price_end
                    marker.equity = operate.curTotalStockValue 
                    self.changeRatioCurve.sell_markers.append(marker)

                    dt_buy = datetime.strptime(operate.buy_date, "%Y%m%d")
                    buy_date = dt_buy.strftime("%Y-%m-%d")

                    dt_sell = datetime.strptime(operate.sell_date, "%Y%m%d")
                    sell_date = dt_sell.strftime("%Y-%m-%d")


                    tradeRecorder = BackTestMsgDataStruct.TradeRecord()
                    tradeRecorder.trade_id = count_sell
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
        print(f"########买入数量：{count_buy}，  卖出数量：{count_sell}")
        totalStock.equity_curve = asdict(self.changeRatioCurve)
        totalStock.trades = tradeRecorderList

        for key, stockPart in self.partList.items():
            divisions = stockPart.GetResult()
            res.divisions[stockPart.name] = divisions

        res.total = asdict(totalStock)

        return asdict(res)




    def Log(self):
        print("")
        for key, part in self.partList.items():
            part.Log()
        print(f"----更新总仓：日期：{self.handler.backTestCalculationHandle.todayStr}， 开仓价：{self.startValue}， 当前价：{self.curValue}， 涨跌幅：{self.changeRatio}")
        print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    
        