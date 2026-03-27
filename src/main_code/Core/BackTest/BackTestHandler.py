import src.main_code.Core.BackTest.StockTotal as StockTotal
from src.main_code.Core import Main
import traceback
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct
from datetime import date, datetime, timedelta
from src.main_code.Core.Calculate import CalculationDataHandle
class BaseClass:
    totalStock : StockTotal.BaseClass
    startDate : str     #开始日期
    stopDate : str      #结束日期
    isOutST : bool
    isOutCY : bool
    isOutKC : bool
    isInit :bool
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
            print("仓位初始化完毕")


            #await self.StartBackTest()
        except Exception as e:
            print(f"❌ 回测数据验证失败: {e}")
            self.main.BoardCast(f"❌ 回测数据验证失败: {e}")
            full_trace = traceback.format_exc()

            print(f"❌ 回测数据验证失败: {full_trace}")


    async def StartBackTest(self):
        print("开始执行回测")
        # 20210104
        self.main.SetIsInHandle(True)
        backTestCalculationHandle = CalculationDataHandle.BaseClass()
        self.backTestCalculationHandle = backTestCalculationHandle
        backTestCalculationHandle.Init(self.main, self.startDate)
        await backTestCalculationHandle.DataPreheating()

        #初始化数据
        nextDayStr = self.startDate
        date_format = "%Y%m%d"
        nextDayStd = datetime.strptime(nextDayStr, date_format)

        stopStr = self.stopDate
        stopDayStd = datetime.strptime(stopStr, date_format)



        while nextDayStd < stopDayStd:

            #20210104这里执行筛选操作，得出一个买列表，一个卖列表
            await self.ExecuteSelect()

            #移动到下一天
            nextDayStr = await backTestCalculationHandle.MoveDateToNextDay()
            if(nextDayStr == ""):
                return

            #20210105这天，基于上一天的数据执行买卖
            await self.ExecuteBuySell()

            nextDayStd = datetime.strptime(nextDayStr, date_format)



        #结束
        self.main.SetIsInHandle(False)
        print("回测结束")



    async def ExecuteSelect(self):
        await self.totalStock.ExecuteSelect()



    async def ExecuteBuySell(self):
        await self.totalStock.ExecuteBuySell()


