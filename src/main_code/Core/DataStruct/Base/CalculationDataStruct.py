from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct

from src.main_code.Core.Calculate import CalculationUtil
#用于条件指标记录类
class AllDateStructBaseClass:
    def __init__(self):
        self.allDic = {} #{code, date}:StructBaseClass
        self.isInit = False
    def GetBaseClass(self, code, data):
        return self.allDic[code, data]
    

class StructBaseClass :
    def __init__(self):
        self.isCalculate = False
        self.isCalculateRank = False
        self.isInit = False
        self.dataList_240 : list[StructBaseClass]  = []

        self._computed_fields = set()
        self.dic = {}
        self.calculateCount = 0

    def Init(self, handler, stockCode, date):
        self.handler = handler
        tempDailyCls = DailyDBStruct.DBStructClass()
        tempAdjustCls = AdjustDBStruct.DBStructClass()

        dailyData = handler.main.dbHandler.GetDailyRowByCodeAndDate(stockCode, date)
        if(dailyData == None):
            #print("日期不存在")
            return None
        adjustTable = handler.main.dbHandler.GetAdjustRowByCodeAndDate(stockCode, date)

        adjust = adjustTable[tempAdjustCls.GetNameByEnum(AdjustDBStruct.ColumnEnum.For_Adjust)]
        cur_date = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)]
        open_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Open_Price)] * adjust
        close_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Close_Price)] * adjust
        high_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.High_Price)] * adjust
        low_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Low_Price)] * adjust
        turn = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Exchange_Hand)]
        change_Ratio = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Change_Ratio)]
        amount = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount)]
        amount_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount_Price)]
        earn_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Earn_TTM)]
        clean = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Clean)]
        cash_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Cash_TTM)]
        sale_TTM = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Sale_TTM)]
        is_ST = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_ST)]
        is_Trading = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_Trading)]
        last_close_price = dailyData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Last_Close_Price)]
        if(is_Trading != 1):
            average_price = 0
            amplitude = 0
        else:
            average_price = (amount_price / amount) * adjust
            amplitude = ((high_price - low_price) / last_close_price) * 100
            #print(f"成交价：{amount_price}   成交量：{amount}，振幅：{amplitude}, 均价{average_price}， 日期：{date}，上市状态：{is_Trading}")

        self.code = stockCode
        self.adjst = adjust
        self.trade_date = cur_date
        self.open = open_price * adjust
        self.close = close_price * adjust
        self.last_close = last_close_price
        self.high = high_price * adjust
        self.low = low_price * adjust

        self.open_ori = open_price
        self.close_ori = close_price
        self.high_ori = high_price
        self.low_ori = low_price

        self.volume = amount
        self.change_Ratio = change_Ratio
        self.volume_price = amount_price

        self.turn = turn
        if(is_Trading):
            self.total_value = (amount / (turn / 100 )) * average_price
        self.earn = earn_TTM
        self.clean = clean
        self.cash = cash_TTM
        self.sale = sale_TTM

        self.amplitude = amplitude
        self.industry = handler.totalComponyIns.GetIndustryStrByCode(stockCode)
        self.isST = is_ST
        self.trade_state = is_Trading
        self.avg = average_price * adjust

        #self.dic = {
        #    "dataList_240" :(handler.GetLastDateDataByNum,(self.code, self.trade_date, 240)),
        #    "change_Ratio_3":(CalculationUtil.GetChange_Ratio, (self, 3)),
        #    "change_Ratio_5":(CalculationUtil.GetChange_Ratio, (self, 5)),
        #    "volume_ratio_10":(CalculationUtil.GetVolume_Ratio, (self, 3))
        #}
        self.isInit = True
    
    #def __getattr__(self, field_name):
    #    if self.isInit == False:
    #        return None
    #    #print("触发首次读取")
    #    # 1. 如果字段不在懒加载映射里，抛出常规属性不存在异常（避免无意义递归）
    #    if field_name not in self.dic:
    #        raise AttributeError(f"'StructBaseClass' object has no attribute '{field_name}'")
        
    #    # 2. 如果字段未计算，执行计算逻辑
    #    if field_name not in self._computed_fields:
    #        self.calculateCount += 1
    #        # 从dic中取出方法和参数
    #        if field_name == "change_Ratio_5":
    #            print("???????执行啊啊啊啊啊啊啊")
    #        calc_method, args = self.dic[field_name]
    #        # 执行计算并赋值给实例（存入__dict__，避免再次触发__getattr__）
    #        calc_result = calc_method(*args)

    #        setattr(self, field_name, calc_result)
    #        # 标记为已计算
    #        self._computed_fields.add(field_name)
        
    #    # 3. 返回计算后的属性值（此时已存入__dict__，直接取）
    #    return calc_result

    code:str
    adjst:float #前复权因子
    trade_date:date #交易日期
    open: float     #当日开盘价
    close: float     #当日收盘价
    last_close: float#当日昨收价
    high: float     #当日最高价
    low: float      #当日最低价
    volume: float   #当日成交量
    change_Ratio:float      #当日涨跌幅


    open_ori: float     #当日开盘价(原始价格)
    close_ori: float     #当日收盘价(原始价格)
    high_ori: float     #当日最高价(原始价格)
    low_ori: float      #当日最低价(原始价格)



    change_Ratio_3:float      #3日涨跌幅
    change_Ratio_5:float      #5日涨跌幅
    change_Ratio_10:float      #10日涨跌幅
    change_Ratio_20:float      #20日涨跌幅
    change_Ratio_40:float      #40日涨跌幅
    change_Ratio_60:float      #60日涨跌幅
    change_Ratio_120:float      #120日涨跌幅
    change_Ratio_240:float      #240日涨跌幅


    volume_ratio:float        #当日成交量涨跌幅

    volume_ratio_3:float        #3日成交量涨跌幅
    volume_ratio_5:float        #5日成交量涨跌幅
    volume_ratio_10:float        #10日成交量涨跌幅
    volume_ratio_20:float        #20日成交量涨跌幅
    volume_ratio_40:float        #40日成交量涨跌幅

    volume_price: Optional[float] = None        #当日成交额
    volume_price_ratio: Optional[float] = None        #当日成交额涨跌幅

    volume_price_ratio_3: Optional[float] = None        #3日成交额涨跌幅
    volume_price_ratio_5: Optional[float] = None        #5日成交额涨跌幅
    volume_price_ratio_10: Optional[float] = None        #10日成交额涨跌幅
    volume_price_ratio_20: Optional[float] = None        #20日成交额涨跌幅
    volume_price_ratio_40: Optional[float] = None        #40日成交额涨跌幅
    
    volume_price_energy:float    #当日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_5:float    #5日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_10:float    #10日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_20:float    #20日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_60:float    #60日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_120:float    #120日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_240:float    #240日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大



    volume_ratio_5:float       #当日量比 
    turn: float             #当日换手率
    turn_ratio:float        #当日换手率涨跌幅
    total_value:float       #总市值
    earn:float              #当日市盈率
    clean:float             #当日市净率
    cash:float              #当日市销率
    sale:float              #当日市现率



    amplitude:float         #当日振幅
    amplitude_3:float         #3日振幅
    amplitude_5:float         #5日振幅
    amplitude_10:float         #10日振幅

    industry:str            #当日行业
    isST:int                #1是  .0否
    trade_state:int         #交易状态1正常交易，0停牌
    adjust:float            #当日复权因子
    avg:float               #当日均价
    avg_ratio:float               #当日均价涨跌幅
    avg_5:float             #十日均价
    avg_10:float             #十日均价
    avg_20:float            #20日均价
    avg_40:float             #40均价
    avg_60:float            #60日均价
    avg_120:float           #120日均价
    avg_240:float           #240日均价

    avg_ratio_5:float             #当日均价与其他日均价的比
    avg_ratio_10:float             #当日均价与其他日均价的比
    avg_ratio_20:float              #20日均价
    avg_ratio_40:float             #40均价
    avg_ratio_60:float               #60日均价
    avg_ratio_120:float              #120日均价
    avg_ratio_240:float           #240日均价
    
    
    #这下面还有行业相关的排名数据没有写

    total_value_ratio:float       #总市值排行业前%
    earn_ratio:float              #当日市盈率排行业前%
    clean_ratio:float             #当日市净率排行业前%
    cash_ratio:float              #当日市销率排行业前%
    sale_ratio:float              #当日市现率排行业前%

    volume_industry_rank:float #成交量排名(前%)
    total_price_industry_rank:float #成交额排名(前%)
    total_price_ratio_industry_rank:float#成交额涨跌幅排名(前%)
    volume_ratio_industry_rank:float #成交量涨跌幅排名(前%)
    ratio_industry_rank:float#涨跌幅排名(前%)
    amplitude_industry_rank:float#振幅排名(前%)
    turn_industry_rank:float#换手率涨跌幅排名(前%)
    turn_ratio_industry_rank:float#换手率涨跌幅排名(前%)
    avg_industry_rank:float#均价涨跌幅排名(前%)


    #快捷指标
    is_up_up:float#是否放量增长(>或小于1)
    is_low_up:float#是否缩量增长
    is_up_low:float#是否放量降低
    is_low_low:float#是否缩量降低
    is_up_mid:float#是否放量横盘
    is_low_mid:float#是否缩量横盘
    is_mid_up:float#是否平量增长
    is_mid_low:float#是否平量降低

    is_up_up_3:float#3日是否放量增长(>或小于1)
    is_low_up_3:float#3日是否缩量增长
    is_up_low_3:float#3日是否放量降低
    is_low_low_3:float#3日是否缩量降低
    is_up_mid_3:float#3日是否放量横盘
    is_low_mid_3:float#3日是否缩量横盘
    is_mid_up_3:float#3日是否平量增长
    is_mid_low_3:float#3日是否平量降低

    is_up_up_5:float#5日是否放量增长(>或小于1)
    is_low_up_5:float#5日是否缩量增长
    is_up_low_5:float#5日是否放量降低
    is_low_low_5:float#5日是否缩量降低
    is_up_mid_5:float#5日是否放量横盘
    is_low_mid_5:float#5日是否缩量横盘
    is_mid_up_5:float#5日是否平量增长
    is_mid_low_5:float#5日是否平量降低


    is_up_up_10:float#10日是否放量增长(>或小于1)
    is_low_up_10:float#10日是否缩量增长
    is_up_low_10:float#10日是否放量降低
    is_low_low_10:float#10日是否缩量降低
    is_up_mid_10:float#10日是否放量横盘
    is_low_mid_10:float#10日是否缩量横盘
    is_mid_up_10:float#10日是否平量增长
    is_mid_low_10:float#10日是否平量降低

    is_pop_up:float#是否震荡上行
    is_pop_down:float#是否震荡下行

    is_pop_up_3:float#是否震荡上行
    is_pop_down_3:float#是否震荡下行

    is_pop_up_5:float#是否震荡上行
    is_pop_down_5:float#是否震荡下行

    is_pop_up_10:float#是否震荡上行
    is_pop_down_10:float#是否震荡下行


    #是否涨停
    #是否跌停
    #是否触及涨停
    #是否触及跌停

    #是否长上下影线十字
    #是否正T字
    #是否倒T字
    
    #快捷技术指标（布林线，macd，rsi，均价交叉）


class StructBaseWindowClass :
    isCalculateRank:bool    #是否已经计算了排名数据
    isCalculateOther:bool    #是否已经计算了其他数据
    startDataCls : StructBaseClass
    def __init__(self):
        self.isCalculateRank = False
        self.isCalculateOther = False

        self._computed_fields = set()
        self.dic = {}
        self.calculateCount = 0
        self.isInit = False

    def Init(self, startDataCls, startCount, toCount, handler):
        self.isInit = True
        self.startDataCls : StructBaseClass = startDataCls
        self.code = self.startDataCls.code
        self.startCount = startCount
        self.toCount = toCount
        self.handler = handler
        self.dic = {
            "change_Ratio_Total":(CalculationUtil.GetChange_Ratio_Total_Window, (startDataCls, startCount, toCount)),
            "ratio_industry_rank":(CalculationUtil.GetChange_Ratio_Window_Rank, (startDataCls, startCount, toCount, handler)),
            #"is_up_up":(CalculationUtil.GetVolume_Ratio, (self, 3))
        }

    def __getattr__(self, field_name):
        if self.isInit == False:
            return None
        #print("触发首次读取")
        # 1. 如果字段不在懒加载映射里，抛出常规属性不存在异常（避免无意义递归）
        if field_name not in self.dic:
            raise AttributeError(f"'StructBaseClass' object has no attribute '{field_name}'")
        
        # 2. 如果字段未计算，执行计算逻辑
        if field_name not in self._computed_fields:
            self.calculateCount += 1
            # 从dic中取出方法和参数
            #if field_name == "change_Ratio_5":
            #    print("???????执行啊啊啊啊啊啊啊")
            calc_method, args = self.dic[field_name]
            # 执行计算并赋值给实例（存入__dict__，避免再次触发__getattr__）
            calc_result = calc_method(*args)

            setattr(self, field_name, calc_result)
            # 标记为已计算
            self._computed_fields.add(field_name)
        
        # 3. 返回计算后的属性值（此时已存入__dict__，直接取）
        return calc_result



    code:str
    trade_date_from:date    #交易日期
    startCount:int
    #trade_date_to:date      #交易日期
    toCount:int
    up_stopCount:int        #涨停次数
    down_stopCount:int      #跌停次数
    industry:str            #行业
    isST:int                #1是  .0否

    
    volume:float   #整体成交量
    volume_price:float   #整体成交额
    volume_ratio:float   #整体成交量涨跌幅
    volume_price_ratio:float   #整体成交额涨跌幅
    turn_ratio:float          #整体换手率涨跌幅
    change_Ratio:float      #涨跌幅
    change_Ratio_Total:float      #整体涨跌幅
    avg_Ratio:float      #均价涨跌幅
    avg_Ratio_Total:float      #整体均价涨跌幅


    avg_open: float         #平均开盘价
    avg_close: float            #平均收盘价
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

    
    volume_industry_rank:float #成交量排名(前%)
    total_price_industry_rank:float #成交额排名(前%)
    total_price_ratio_industry_rank:float#成交额涨跌幅排名(前%)
    volume_ratio_industry_rank:float #成交量涨跌幅排名(前%)
    ratio_industry_rank:float#涨跌幅排名(前%)
    amplitude_industry_rank:float#振幅排名(前%)
    turn_ratio_industry_rank:float#换手率涨跌幅排名(前%)
    avg_industry_rank:float#均价涨跌幅排名(前%)


    #快捷指标
    is_up_up:float#是否放量增长(>或小于1)
    is_low_up:float#是否缩量增长
    is_up_low:float#是否放量降低
    is_low_low:float#是否缩量降低
    is_up_mid:float#是否放量横盘
    is_low_mid:float#是否缩量横盘
    is_mid_up:float#是否平量增长
    is_mid_low:float#是否平量降低


    is_pop_up:float#是否震荡上行
    is_pop_down:float#是否震荡下行

    #是否出现过涨停
    #是否出现过跌停
    #是否出现过长上下影线十字
    #是否出现过正T字
    #是否出现过倒T字



class StructIndustryClass():
    name:str        #行业名
    trade_date:date #交易日期
    volume: float   #成交量
    volume_ratio:float        #成交量涨跌幅
    volume_ratio_3:float        #当日成交量与3日平均成交量的比
    volume_ratio_5:float        #当日成交量与5日平均成交量的比
    volume_ratio_10:float        #当日成交量与10日平均成交量的比
    volume_ratio_20:float        #当日成交量与20日平均成交量的比


    volume_price: Optional[float] = None        #成交额
    volume_price_ratio: Optional[float] = None        #成交额涨跌幅

    volume_price_ratio_3: Optional[float] = None        #当日成交额与3日平均成交额的比
    volume_price_ratio_5: Optional[float] = None        #当日成交额与5日平均成交额的比
    volume_price_ratio_10: Optional[float] = None        #当日成交额与10日平均成交额的比
    volume_price_ratio_20: Optional[float] = None        #当日成交额与20日平均成交额的比


    change_Ratio:float      #行业涨整体跌幅
    stockNum:int            #行业股数量

    stockNum_up:int         #行业上涨股数量
    stockNum_up_Ratio:int         #行业上涨股比例
    
    stockNum_down:int       #行业下跌股数量
    stockNum_down_Ratio:int         #行业下跌股比例



class StructIndustryWindowClass():
    name:str        #行业名
    stockNum:int            #行业股数量

    volume: float   #整体成交量
    volume_price: Optional[float] = None        #整体成交额
    avg_volume: float   #平均成交量
    avg_volume_price: Optional[float] = None        #平均成交额


    volume_ratio:float        #整体成交量涨跌幅
    volume_price_ratio: Optional[float] = None        #整体成交额涨跌幅

    change_Ratio:float      #行业涨跌幅
    change_Ratio_Total:float      #整体行业涨跌幅

    avg_stockNum_up:int         #平均行业上涨股数量
    avg_stockNum_down:int       #平均行业下跌股数量
    
    stockNum_up_Ratio:int         #平均行业上涨股比例
    stockNum_down_Ratio:int         #平均行业下跌股比例






#总数据存储类

class StructComponyInfoClass:
    Ts_code:str                                 #股票TS代码(已有)
    Code:str                                    #股票代码(已有)
    Name:str                                    #股票名称(已有)
    Area:str                                    #地域(已有)
    Industry:str                                #所属行业(已有)
    Cn_spell:str                                #拼音缩写(已有)
    Market:str                                  #市场类型（主板/创业板/科创板/CDR）(已有)
    List_Status:str                           #上市状态 L上市 D退市 P暂停上市(已有)
    List_date:str                            #上市日期(已有)
    Act_name:str                              #实控人名称(已有)
    Act_ent_type:str                            #实际企业类型(已有)
    Product:str                                 #主要产品(已有)
    Business_Scope:str                            #经营范围(已有)
    Introduction:str                             #公司简介(已有)
    Com_name:str                                   #公司名称(已有)
    Total_Value:int                                   #总流通股本
    Earn:float              #市盈率
    Clean:float             #市净率
    Cash:float              #市销率
    Sale:float              #市现率

    def __init__(self):
        self.Total_Value = 0
        self.Earn = 0
        self.Clean = 0
        self.Cash = 0
        self.Sale = 0

    
class StructIndustryInfoClass:
    industryName : str
    isCalculate:bool
    def __init__(self):
        self.stockList : Dict[str, StructComponyInfoClass] = {}
        self.stockForSortList : list[StructComponyInfoClass] = []
        self.isCalculate = False
        
        

class StructIndustryTotalInfoClass:
    def __init__(self):
        self.industryList:StructIndustryInfoClass = {}
        self.allStockList:StructComponyInfoClass = {}
        self.code_industryStr_List = {}  #{code : industry}


    def GetComponyInfo(self, code:str) -> StructComponyInfoClass:
        return self.allStockList[code]

    def GetIndustryStrByCode(self, code:str) -> str:
        return self.code_industryStr_List[code]


    def GetIndustryClsByCode(self, code:str) -> StructIndustryInfoClass:
        industryStr = self.GetIndustryStrByCode(code)
        return self.industryList[industryStr]
    
    def GetIndustryClsByIndustryStr(self, industry:str) -> StructIndustryInfoClass:
        return self.industryList[industry]


#行业分析结果类

class Stock_AnalysisResult:
    #高价值股列表
    High_Value_Stock_List = []

    #高成长股列表
    High_Grow_Stock_List = []

class IndustryAnalysisResult:
    Price_Increase_5_1:str                                 #过去五年1月份上涨的行业 (有三年在涨)
    Price_Increase_5_2:str                                 #过去五年2月份上涨的行业
    Price_Increase_5_3:str                                 #过去五年3月份上涨的行业
    Price_Increase_5_4:str                                 #过去五年4月份上涨的行业
    Price_Increase_5_5:str                                 #过去五年5月份上涨的行业
    Price_Increase_5_6:str                                 #过去五年6月份上涨的行业
    Price_Increase_5_7:str                                 #过去五年7月份上涨的行业
    Price_Increase_5_8:str                                 #过去五年8月份上涨的行业
    Price_Increase_5_9:str                                 #过去五年9月份上涨的行业
    Price_Increase_5_10:str                                 #过去五年10月份上涨的行业
    Price_Increase_5_11:str                                 #过去五年11月份上涨的行业
    Price_Increase_5_12:str                                 #过去五年12月份上涨的行业

    Price_Increase_3_1:str                                 #过去3年1月份上涨的行业（有两年在涨）
    Price_Increase_3_2:str                                 #过去3年2月份上涨的行业
    Price_Increase_3_3:str                                 #过去3年3月份上涨的行业
    Price_Increase_3_4:str                                 #过去3年4月份上涨的行业
    Price_Increase_3_5:str                                 #过去3年5月份上涨的行业
    Price_Increase_3_6:str                                 #过去3年6月份上涨的行业
    Price_Increase_3_7:str                                 #过去3年7月份上涨的行业
    Price_Increase_3_8:str                                 #过去3年8月份上涨的行业
    Price_Increase_3_9:str                                 #过去3年9月份上涨的行业
    Price_Increase_3_10:str                                 #过去3年10月份上涨的行业
    Price_Increase_3_11:str                                 #过去3年11月份上涨的行业
    Price_Increase_3_12:str                                 #过去3年12月份上涨的行业

    Price_Increase_1_1:str                                 #过去1年1月份上涨的行业
    Price_Increase_1_2:str                                 #过去1年2月份上涨的行业
    Price_Increase_1_3:str                                 #过去1年3月份上涨的行业
    Price_Increase_1_4:str                                 #过去1年4月份上涨的行业
    Price_Increase_1_5:str                                 #过去1年5月份上涨的行业
    Price_Increase_1_6:str                                 #过去1年6月份上涨的行业
    Price_Increase_1_7:str                                 #过去1年7月份上涨的行业
    Price_Increase_1_8:str                                 #过去1年8月份上涨的行业
    Price_Increase_1_9:str                                 #过去1年9月份上涨的行业
    Price_Increase_1_10:str                                 #过去1年10月份上涨的行业
    Price_Increase_1_11:str                                 #过去1年11月份上涨的行业
    Price_Increase_1_12:str                                 #过去1年12月份上涨的行业