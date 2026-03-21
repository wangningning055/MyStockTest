import main_code.Core.BackTest.StockPart as StockPart
from typing import List, Optional, Callable, Dict, Any, Union
class BaseClass:
    partList : Dict[str, StockPart.BaseClass]        #分仓列表
    startValue : int                                #开仓价
    curValue : int                                  #当前价
    changeRatio : float                             #涨跌幅
    def __init__(self):
        pass
