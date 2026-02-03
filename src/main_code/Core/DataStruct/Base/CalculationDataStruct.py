from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
@dataclass(slots=True)
class StructBaseClass :
    def __init__(self):
        pass
    """
    code  股票代码
    - trade_date: 交易日（datetime.date）
    - open/high/low/close: 当日价格
    - volume: 成交量（手）——保持与 data source 单位一致
    - turn: 换手率（%），例如 1.23 表示 1.23%
    - volume_price: 成交额（万元/元/任意单位，可选）
    - avg  均价 
        adjust:float 复权
    industry  行业
    isST:int是否st股
    """
    code:str
    trade_date:date #交易日期
    open: float     #开盘价
    close: float     #收盘价
    last_close: float       #昨收价
    high: float     #最高价
    low: float      #最低价
    volume: float   #成交量
    volume_ratio:float        #成交量涨跌幅
    volume_price: Optional[float] = None        #成交额
    volume_price_ratio: Optional[float] = None        #成交额涨跌幅
    volume_ratio:float       #量比 
    turn: float             #换手率
    turn_ratio:float        #换手率涨跌幅
    change_Ratio:float      #涨跌幅
    earn:float              #市盈率
    clean:float             #市净率
    cash:float              #市销率
    sale:float              #市现率
    earn_ratio:float              #市盈率排行业前%
    clean_ratio:float             #市净率排行业前%
    cash_ratio:float              #市销率排行业前%
    sale_ratio:float              #市现率排行业前%

    amplitude:float         #振幅
    industry:str            #行业
    isST:int                #1是  .0否
    trade_state:int         #交易状态1正常交易，0停牌
    adjust:float            #复权因子
    avg:float               #当日均价
    avg_7:float             #均价
    avg_20:float
    avg_60:float
    avg_120:float

    
    
    #这下面还有行业相关的排名数据没有写
    #成交量排名
    #成交额排名
    #成交额涨跌幅排名
    #成交量涨跌幅排名
    #涨跌幅排名
    #振幅排名
    #换手率涨跌幅排名
    #均价涨跌幅排名

#这里包装一段时间的base
class StructBaseWindowClass :
    code:str
    trade_date_from:date    #交易日期
    trade_date_to:date      #交易日期
    up_stopCount:int        #涨停次数
    down_stopCount:int      #跌停次数
    industry:str            #行业
    isST:int                #1是  .0否

    
    volume:float   #整体成交量
    volume_price:float   #整体成交额
    volume_ratio:float   #整体成交量涨跌幅
    volume_price_ratio:float   #整体成交额涨跌幅
    turn_ratio:float          #整体换手率涨跌幅
    change_Ratio:float      #整体涨跌幅
    avg_Ratio:float      #均价涨跌幅


    avg_open: float         #平均开盘价
    avg_close: float            #平均收盘价
    avg_last_close: float       #平均昨收价
    avg_high: float         #平均最高价
    avg_low: float          #平均最低价
    avg_volume: float        #平均成交量
    avg_volume_price: Optional[float] = None        #平均成交额
    avg_volume_rito:float       #平均量比 
    avg_turn: float             #平均换手率
    avg_change_Ratio:float      #平均涨跌幅
    avg_amplitude:float         #平均振幅
    avg_avg:float         #平均均价

    min_open: float         #最低开盘价
    min_close: float            #最低收盘价
    min_last_close: float       #最低昨收价
    min_high: float         #最低最高价
    min_low: float          #最低最低价
    min_volume: float        #最低成交量
    min_volume_price: Optional[float] = None        #最低成交额
    min_volume_rito:float       #最低量比 
    min_turn: float             #最低换手率
    min_change_Ratio:float      #最低涨跌幅
    min_amplitude:float         #最低振幅
    min_avg:float         #最低均价

    max_open: float         #最高开盘价
    max_close: float            #最高收盘价
    max_last_close: float       #最高昨收价
    max_high: float         #最高最高价
    max_low: float          #最高最低价
    max_volume: float        #最高成交量
    max_volume_price: Optional[float] = None        #最高成交额
    max_volume_rito:float       #最高量比 
    max_turn: float             #最高换手率
    max_change_Ratio:float      #最高涨跌幅
    max_amplitude:float         #最高振幅
    max_avg:float         #最高均价

    decrease_price:float  #这段时间的跌价总和
    increase_price:float  #这段时间的涨价总和

    #这下面还有行业相关的排名数据没有写
    #整体成交量排名
    #整体成交额排名
    #成交额涨跌幅排名
    #成交量涨跌幅排名
    #整体涨跌幅排名
    #整体振幅排名
    #整体换手率涨跌幅排名
    #均价涨跌幅排名



class StructIndustryClass():
    name:str        #行业名
    trade_date:date #交易日期
    volume: float   #成交量
    volume_ratio:float        #成交量涨跌幅
    volume_price: Optional[float] = None        #成交额
    volume_price_ratio: Optional[float] = None        #成交额涨跌幅
    volume_ratio:float       #量比 
    change_Ratio:float      #行业涨跌幅
    stockNum:int            #行业股数量
    stockNum_up:int         #行业上涨股数量
    stockNum_down:int       #行业下跌股数量
    


class StructIndustryWindowClass():
    name:str        #行业名
    trade_date_from:date #交易日期
    trade_date_to:date #交易日期
    stockNum:int            #行业股数量
    volume: float   #整体成交量
    volume_ratio:float        #整体成交量涨跌幅
    volume_price: Optional[float] = None        #整体成交额
    volume_price_ratio: Optional[float] = None        #整体成交额涨跌幅
    change_Ratio:float      #整体行业涨跌幅
    avg_stockNum_up:int         #平均行业上涨股数量
    avg_stockNum_down:int       #平均行业下跌股数量

    avg_volume: float   #平均成交量
    avg_volume_price: Optional[float] = None        #平均成交额

    decrease_price:float  #这段时间的行业跌价总和
    increase_price:float  #这段时间的行业涨价总和

