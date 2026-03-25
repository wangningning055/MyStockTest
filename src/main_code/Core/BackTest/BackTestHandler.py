import src.main_code.Core.BackTest.StockTotal as StockTotal
from src.main_code.Core import Main
class BaseClass:
    totalStock : StockTotal.BaseClass
    startDate : str     #开始日期
    stopDate : str      #结束日期
    isOutST : bool
    isOutCY : bool
    isOutKC : bool

    def __init__(self):
        self.isOutCY = False
        self.isOutKC = False
        self.isOutCY = False
        self.Stock = None
        pass
    def Init(self, main):
        self.main : Main.processor = main
        print("回测模块初始化完毕")

    def CreateStockByJson(self, jsonStr):
        #这里解析json
        self.Stock = StockTotal.BaseClass(self)
        isSuccess = self.Stock.InitByJson(jsonStr)
        if isSuccess == False:
            return

    def StartBackTest():
        pass
