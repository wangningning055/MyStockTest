from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
@dataclass(slots=True)
class StructBaseClass :
    def __init__(self):
        pass
    """
    - trade_date: 交易日（datetime.date）
    - open/high/low/close: 当日价格
    - volume: 成交量（手）——保持与 data source 单位一致
    - turnover: 换手率（%），例如 1.23 表示 1.23%
    - amount: 成交额（万元/元/任意单位，可选）
    - avg  均价 
    """
    trade_date:date #交易日期
    open: float     #
    close: float
    high: float
    low: float
    volume: float
    turnover: float
    amount: Optional[float] = None
    avg:float#当日均价
    avg_7:float
    avg_30:float
    avg_60:float
    avg_120:float

#这里包装一段时间的base
class StructWindowClass :
    #涨跌幅
    increase_today:float
    increase_total:float
    increase_avg:float
    increase_max:float

    decrease_today:float
    decrease_total:float
    decrease_avg:float
    decrease_max:float

    #成交量
    volume_today:int
    volume_avg:int
    volume_max:int
    volume_min:int
    
    def __init__(self):
        pass
