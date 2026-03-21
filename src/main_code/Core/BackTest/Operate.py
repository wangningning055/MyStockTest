import src.main_code.Core.BackTest.StockSingle as StockSingle
class BaseClass:
    date : str                  #操作日期
    partStockId : int           #操作的分仓id
    stockCode : str             #操作的股票代码
    operate : int               #操作类型  buy = 0   sell = 1
    isSuccess : bool            #操作是否成功


    def __init__(self):
        pass