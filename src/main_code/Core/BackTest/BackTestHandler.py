import src.main_code.Core.BackTest.StockTotal as StockTotal
from src.main_code.Core import Main
import traceback
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from datetime import date, datetime, timedelta
import time
import asyncio
from src.main_code.Core.Calculate import CalculationDataHandle
import json
from dataclasses import dataclass, field, asdict
class BaseClass:
    totalStock : StockTotal.BaseClass
    startDate : str     #开始日期
    stopDate : str      #结束日期
    isOutST : bool
    isOutCY : bool
    isOutKC : bool
    isInit :bool

    isNeedStop : bool
    isInBackTest : bool

    def __init__(self):
        self.isOutCY = False
        self.isOutKC = False
        self.isOutCY = False
        self.Stock = None
        self.startDate = "20220104"
        self.stopDate = "20220204"
        self.isInit = False
    def Init(self, main):
        self.main : Main.processor = main
        print("回测模块初始化完毕")

    async def CreateStockByJson(self, jsonStr):
        #这里解析json
        try:
            print(f"回测数据验证:{jsonStr}")
            msgCls = BackTestMsgDataStruct.Msg_Base(**jsonStr)
            print("回测数据验证成功")
            self.main.BoardCast("回测数据验证成功")
            self.isOutCY = msgCls.isExcludeCY
            self.isOutKC = msgCls.isExcludeKC
            self.isOutST = msgCls.isExcludeST
            self.totalStock = StockTotal.BaseClass(self)
            self.isInit =  self.totalStock.Init(msgCls.config)
            self.startDate = msgCls.start_date
            self.stopDate = msgCls.end_date
            if self.isInit == False:
                print("回测仓位初始化失败")
                self.main.BoardCast("回测仓位初始化失败")
                return
            print("仓位初始化完毕")

            self.isNeedStop = False
            await self.StartBackTest()
        except Exception as e:
            print(f"❌ 回测数据验证失败: {e}")
            self.main.BoardCast(f"❌ 回测数据验证失败: {e}")
            full_trace = traceback.format_exc()

            print(f"❌ 回测数据验证失败: {full_trace}")


    async def StartBackTest(self):
        self.isInBackTest = True
        self.main.calculationDataHandle.ClearDic()
        self.main.calculationDataHandle.isPreheating = False
        print("开始执行回测")
        # 20210104
        self.main.SetIsInHandle(True)
        backTestCalculationHandle = CalculationDataHandle.BaseClass()
        self.backTestCalculationHandle = backTestCalculationHandle
        backTestCalculationHandle.isOutST = self.isOutST
        backTestCalculationHandle.isOutCY = self.isOutCY
        backTestCalculationHandle.isOutKC = self.isOutKC
        
        backTestCalculationHandle.Init(self.main, self.startDate)
        await backTestCalculationHandle.DataPreheating()

        #初始化数据
        nextDayStr = self.startDate
        starDayStr = self.startDate
        date_format = "%Y%m%d"
        nextDayStd = datetime.strptime(nextDayStr, date_format)
        starDayStd = datetime.strptime(starDayStr, date_format)

        stopStr = self.stopDate
        stopDayStd = datetime.strptime(stopStr, date_format)

        tempStop = 0

        totalDay = (stopDayStd - starDayStd).days


        #鉴于源数据源的滞后性，先依据昨天的数据执行买卖，再更新新一天的数据
        while nextDayStd < stopDayStd:
            if self.isNeedStop == True:
                print("回测被停止")
                self.main.BoardCast("回测被停止")
                self.isNeedStop = False
                break
            passDayCount = (nextDayStd - starDayStd).days
            print(f"------------------------开始新的一轮，这天是：{nextDayStr}， 结束天是：{stopStr}--过去了{passDayCount}天----总共是{totalDay}天------------------------------")
            self.main.SetIsInHandle(True)
            self.main.SendProgress(passDayCount / totalDay if totalDay > 0 else 1)
            await asyncio.sleep(0)

            #执行卖
            await self.ExecuteSell()
            await asyncio.sleep(0)


            #执行买
            await self.ExecuteBuy()
            await asyncio.sleep(0)


            #更新今天的数据
            await self.UpdateStock(nextDayStr)
            await asyncio.sleep(0)


            #移动到下一天
            nextDayStr = await backTestCalculationHandle.MoveDateToNextDay()
            if(nextDayStr == ""):
                return
            nextDayStd = datetime.strptime(nextDayStr, date_format)



        #这里需要整理结果数据，然后传给前端
        res = self.totalStock.GetResult(nextDayStr)
        #resJson = json.dumps(
        #    asdict(res),    # 自动把 dataclass 转字典
        #    ensure_ascii=False,  # 支持中文
        #    indent=2       # 格式化输出（好看）
        #)
        #self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_BACK_TEST, resJson)

        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_BACK_TEST, res)


        #结束
        self.isInBackTest = False
        self.main.SetIsInHandle(False)
        print("回测结束")



    def StopBackTest(self):
        if self.isInBackTest == True:
            self.isNeedStop = True
            print("回测停止")

    async def ExecuteBuy(self):
        await self.totalStock.ExecuteBuy()
        
    async def ExecuteSell(self):
        await self.totalStock.ExecuteSell()

    async def UpdateStock(self, date):
        self.totalStock.UpdateStock(date)




    def HandelResult():


        pass









## ============================
## Python 后端接入示例
## ============================

#def build_backtest_result(backtest_engine_output) -> dict:
#    """
#    将回测引擎的输出转换为前端需要的数据格式
    
#    参数:
#        backtest_engine_output: 你的回测引擎产出的原始数据
        
#    返回:
#        dict: 符合 BacktestResult 结构的字典，可直接 JSON 序列化发送给前端
#    """
    
#    # ---- 示例：构造总仓结果 ----
#    total_summary = TradeSummary(
#        initial_fund=100000.0,
#        final_fund=125000.0,
#        total_return=25.0,
#        win_rate=62.5,
#        annual_return=18.5,
#        annual_volatility=22.3,
#        monthly_return=1.5,
#        monthly_volatility=6.2,
#        max_drawdown=-12.5,
#        sharpe_ratio=0.83
#    )
    
#    # 构造权益曲线
#    total_equity = EquityCurve(
#        dates=["2024-01-02", "2024-01-03", "2024-01-04"],
#        nav=[1.0, 1.02, 1.015],
#        returns=[0.0, 2.0, 1.5],
#        drawdown=[0.0, 0.0, -0.49],
#        positions=[
#            [],                                                    # 第1天无持仓
#            [{"code": "600000", "name": "浦发银行", "shares": 1000}],  # 第2天
#            [{"code": "600000", "name": "浦发银行", "shares": 1000}],  # 第3天
#        ],
#        buy_markers=[
#            {"date": "2024-01-03", "code": "600000", "name": "浦发银行", "price": 10.5, "nav": 1.02}
#        ],
#        sell_markers=[]
#    )
    
#    # 构造成交记录
#    total_trades = [
#        TradeRecord(
#            trade_id="t001",
#            buy_date="2024-01-03",
#            sell_date="2024-01-15",
#            hold_days=12,
#            code="600000",
#            name="浦发银行",
#            buy_price=10.50,
#            sell_price=11.20,
#            profit_pct=6.67,
#            profit_money=700.0,
#            kline_data=asdict(KlineData(
#                dates=["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
#                       "2024-01-08", "2024-01-09", "2024-01-10", "2024-01-11",
#                       "2024-01-12", "2024-01-15"],
#                ohlc=[
#                    [10.3, 10.4, 10.2, 10.5],   # [open, close, low, high]
#                    [10.4, 10.5, 10.3, 10.6],
#                    [10.5, 10.3, 10.2, 10.6],
#                    [10.3, 10.6, 10.2, 10.7],
#                    [10.6, 10.8, 10.5, 10.9],
#                    [10.8, 10.7, 10.6, 10.9],
#                    [10.7, 11.0, 10.6, 11.1],
#                    [11.0, 10.9, 10.8, 11.1],
#                    [10.9, 11.1, 10.8, 11.2],
#                    [11.1, 11.2, 11.0, 11.3],
#                ],
#                volumes=[50000, 62000, 48000, 55000, 70000, 
#                         45000, 80000, 52000, 65000, 58000]
#            ))
#        ),
#    ]
    
#    total_result = DivisionResult(
#        division_name="总仓",
#        summary=asdict(total_summary),
#        equity_curve=asdict(total_equity),
#        trades=[asdict(t) for t in total_trades]
#    )
    
#    # ---- 构造分仓结果（示例1个分仓）----
#    div1_summary = TradeSummary(
#        initial_fund=50000.0,
#        final_fund=56000.0,
#        total_return=12.0,
#        win_rate=66.7,
#        annual_return=15.2,
#        annual_volatility=18.5,
#        monthly_return=1.2,
#        monthly_volatility=5.1,
#        max_drawdown=-8.3,
#        sharpe_ratio=0.82
#    )
    
#    div1_result = DivisionResult(
#        division_name="分仓1",
#        summary=asdict(div1_summary),
#        equity_curve=asdict(EquityCurve(
#            dates=["2024-01-02", "2024-01-03", "2024-01-04"],
#            nav=[1.0, 1.015, 1.008],
#            returns=[0.0, 1.5, 0.8],
#            drawdown=[0.0, 0.0, -0.69],
#            positions=[[], [], []],
#            buy_markers=[],
#            sell_markers=[]
#        )),
#        trades=[]
#    )
    
#    # ---- 组装最终结果 ----
#    result = BacktestResult(
#        total=asdict(total_result),
#        divisions={
#            "div-123-abc": asdict(div1_result),
#            # 更多分仓...
#        }
#    )
    
#    return asdict(result)



#数据结构
#{
#  "total": {
#    "division_name": "总仓",
#    "summary": {
#      "initial_fund": 100000.0,
#      "final_fund": 125000.0,
#      "total_return": 25.0,
#      "win_rate": 62.5,
#      "annual_return": 18.5,
#      "annual_volatility": 22.3,
#      "monthly_return": 1.5,
#      "monthly_volatility": 6.2,
#      "max_drawdown": -12.5,
#      "sharpe_ratio": 0.83
#    },
#    "equity_curve": {
#      "dates": ["2024-01-02", "2024-01-03", "..."],
#      "nav": [1.0, 1.02, "..."],
#      "returns": [0.0, 2.0, "..."],
#      "drawdown": [0.0, 0.0, "..."],
#      "positions": [
#        [],
#        [{"code": "600000", "name": "浦发银行", "shares": 1000}],
#        "..."
#      ],
#      "buy_markers": [
#        {"date": "2024-01-03", "code": "600000", "name": "浦发银行", "price": 10.5, "nav": 1.02}
#      ],
#      "sell_markers": [
#        {"date": "2024-01-15", "code": "600000", "name": "浦发银行", "price": 11.2, "nav": 1.08}
#      ]
#    },
#    "trades": [
#      {
#        "trade_id": "t001",
#        "buy_date": "2024-01-03",
#        "sell_date": "2024-01-15",
#        "hold_days": 12,
#        "code": "600000",
#        "name": "浦发银行",
#        "buy_price": 10.50,
#        "sell_price": 11.20,
#        "profit_pct": 6.67,
#        "profit_money": 700.0,
#        "kline_data": {
#          "dates": ["2024-01-02", "2024-01-03", "..."],
#          "ohlc": [[10.3, 10.4, 10.2, 10.5], "..."],
#          "volumes": [50000, 62000, "..."]
#        }
#      }
#    ]
#  },
#  "divisions": {
#    "div-123-abc": {
#      "division_name": "分仓1",
#      "summary": {"...同上结构...": ""},
#      "equity_curve": {"...同上结构...": ""},
#      "trades": ["...同上结构..."]
#    }
#  }
#}





