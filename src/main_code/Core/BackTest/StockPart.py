import src.main_code.Core.BackTest.StockSingle as StockSingle
import main_code.Core.BackTest.Operate  as Operate
from typing import List, Optional, Callable, Dict, Any, Union
class BaseClass:
    id : int
    name : str                  #仓位名
    ratio : float               #占主仓比例
    startValue : float          #开仓价
    curValue : float            #当前价

    buy_Strategy_Id : int       #买入策略id
    sell_Strategy_Id : int      #卖出策略id
    
    curChangeRatio : float      #涨跌幅

    operate_recorder : List[Operate.BaseClass]      #操作记录
    stockList : List[StockSingle.BaseClass]         #持仓列表
    
    def __init__(self):
        pass

