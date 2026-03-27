import src.main_code.Core.BackTest.StockSingle as StockSingle

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.StockPart as StockPart

class BaseClass:
    date : str                  #操作日期
    partStock : "StockPart.BaseClass"           #操作的分仓
    stockCode : str             #操作的股票代码
    operate : int               #操作类型  buy = 0   sell = 1
    isSuccess : bool            #操作是否成功
    failReason : str                  #失败原因
    successReason : str                  #成功卖出原因

    #买入
    buy_price:float             #买入操作的买入价
    buy_volume:int              #买入操作的买入股数

    #卖出
    sell_price_start:float            #卖出操作的对应的买入时的买入价
    sell_price_end:float            #卖出操作的卖出价

    def __init__(self):
        pass

    def Log(self):
            main = self.partStock.totalStock.handler.main
            backTestCalculationHandle = self.partStock.totalStock.handler.backTestCalculationHandle
            componenyInfo = backTestCalculationHandle.totalComponyIns.GetComponyInfo(self.stockCode)
            name = componenyInfo.Name

            print("")
            if self.isSuccess == True:
                if self.operate == "buy":
                    print(f"在 {self.date} 执行买入：{name}，操作的分仓是：{self.partStock.name}， 买入价是：{self.buy_price} 买入手数：{self.buy_volume / 100}, 总花费{self.buy_price * self.buy_volume}")
                    pass
                if self.operate == "sell":
                    earn = (self.sell_price_end * self.buy_volume * 100) - (self.sell_price_start * self.buy_volume * 100)

                    ratio = ((self.sell_price_end - self.sell_price_start) / self.sell_price_start) * 100
                    print(f"在 {self.date} 执行卖出:{name}, 卖出原因：{self.successReason},操作的分仓是：{self.partStock.name},当时买入价是：{self.sell_price_start}, 卖出价是：{self.sell_price_end} 卖出手数：{self.buy_volume * 100}  总获利：{earn}, 单笔盈亏：{ratio}")
                    pass
            else:
                if self.operate == "buy":
                    print(f"在 {self.date} 买入 {name} 失败，操作的分仓是：{self.partStock.name}, 失败原因是：{self.failReason}")
                    pass
                if self.operate == "sell":
                    print(f"在 {self.date} 卖出 {name} 失败，操作的分仓是：{self.partStock.name}, 失败原因是：{self.failReason}")
                    pass
            print("")
            
