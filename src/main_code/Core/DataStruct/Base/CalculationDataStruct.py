from __future__ import annotations
from datetime import date
from typing import List, Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core.Calculate import CalculationUtil
import time
import src.main_code.Core.Const as ConstVal
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

        self._computed_fields = set()
        self.calculateCount = 0

    def Init(self, handler, stockCode, date, dbData):
        if(dbData == None):
            return None

        self.handler = handler
        tempDailyCls = DailyDBStruct.DBStructClass()
        tempAdjustCls = AdjustDBStruct.DBStructClass()


        componyInfo = handler.totalComponyIns.GetComponyInfo(stockCode)
        self.componyInfo = componyInfo

        adjustTable = handler.GetLatestAdjustDataByCodeAndDate(stockCode, date)
        adjust = adjustTable[tempAdjustCls.GetNameByEnum(AdjustDBStruct.ColumnEnum.For_Adjust)]
        
        cur_date = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)]
        open_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Open_Price)]
        close_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Close_Price)]
        high_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.High_Price)]
        low_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Low_Price)]
        turn = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Exchange_Hand)]
        change_Ratio = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Change_Ratio)]
        amount = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount)]
        amount_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Amount_Price)]
        earn_TTM = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Earn_TTM)]
        clean = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Clean)]
        cash_TTM = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Cash_TTM)]
        sale_TTM = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Sale_TTM)]
        is_ST = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_ST)]
        is_Trading = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Is_Trading)]
        last_close_price = dbData[tempDailyCls.GetNameByEnum(DailyDBStruct.ColumnEnum.Last_Close_Price)]
        if(is_Trading != 1):
            average_price = 0
            amplitude = 0
        else:
            average_price = (amount_price / amount) if amount != 0 else 0
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


        if self.code == "300502.SZ" and (cur_date == "20250324" or date == "20250324"):
            print(f"计算一年前的新医生：{close_price}，  {adjust} ,  {self.close} ,  {cur_date}  {date}")




        self.open_ori = open_price
        self.close_ori = close_price
        self.high_ori = high_price
        self.low_ori = low_price
        self.avg_ori = average_price
        self.volume = amount / 100
        self.change_Ratio = change_Ratio
        self.volume_price = amount_price

        self.is_up_stop = 1 if self.change_Ratio >= ConstVal.GetStopRatio(stockCode) else 0
        self.is_down_stop= 1 if self.change_Ratio <= -ConstVal.GetStopRatio(stockCode) else 0 #是否跌停
        self.is_touch_up_stop = 1 if ((self.high - self.last_close) * 100/ self.last_close) >= ConstVal.GetStopRatio(stockCode) else 0#是否触及涨停
        self.is_touch_down_stop = 1 if ((self.low - self.last_close) * 100 / self.last_close) <= -ConstVal.GetStopRatio(stockCode) else 0#是否触及跌停


        self.is_one_ban = 1 if (self.open == self.close == self.high == self.low) else 0   #是否短十字

        self.is_short_entity = 1 if (self.open / self.close) < 1.003 and (self.open / self.close) > 0.997  else 0   #是否短实体
        if self.change_Ratio >= 0:
            self.is_long_shadow_up = 1 if ((self.high - self.close) / self.close) > 0.05 else 0#是否长上影线
            self.is_long_shadow_down = 1 if ((self.open - self.low) / self.low) > 0.05 else 0#是否长下影线
        elif self.change_Ratio < 0:
            self.is_long_shadow_up = 1 if ((self.high - self.open) / self.close) > 0.05 else 0#是否长上影线
            self.is_long_shadow_down = 1 if ((self.close - self.low) / self.low) > 0.05 else 0#是否长下影线

        if self.change_Ratio >= 0:
            self.shortUp = 1 if ((self.high - self.close) / self.close) < 0.01 else 0#是否短上影线
            self.shortDown = 1 if ((self.open - self.low) / self.low) < 0.01 else 0#是否短下影线
        elif self.change_Ratio < 0:
            self.shortUp = 1 if ((self.high - self.open) / self.close) < 0.01 else 0#是否短上影线
            self.shortDown = 1 if ((self.close - self.low) / self.low) < 0.01 else 0#是否短下影线


        self.is_long_cross = 1 if self.is_short_entity == 1 and self.is_long_shadow_up == 1 and self.is_long_shadow_down == 1 else 0#是否长十字
        self.is_short_cross = 1 if self.is_short_entity == 1 and self.shortUp == 1 and self.shortDown == 1 else 0#是否长十字

        self.is_T_up =  1 if self.change_Ratio >= 0 and self.is_short_entity == 1 and self.shortUp == 1 and self.is_long_shadow_down == 1 else 0#是否正T字
        self.is_T_down =  1 if self.change_Ratio <= 0 and self.is_short_entity == 1 and self.is_long_shadow_up == 1 and self.shortDown == 1 else 0##是否倒T字


        self.turn = turn
        if(is_Trading):
            self.total_value = (amount / (turn / 100 )) * average_price
            self.turn_value = amount_price / self.total_value
        else:
            self.total_value = 0
            self.turn_value = 0
        self.earn = earn_TTM
        self.clean = clean
        self.cash = cash_TTM
        self.sale = sale_TTM

        self.amplitude = amplitude
        self.industry = handler.totalComponyIns.GetIndustryStrByCode(stockCode)
        self.isST = is_ST
        self.trade_state = is_Trading
        self.avg = average_price * adjust
        self.isInit = True

        self.totalCacheLength = 60

    def Clear(self):
        """
        彻底清空当前对象的所有属性，释放内存
        调用后对象仅保留基础标记，所有数据字段全部删除
        """
        self.dataList_240.clear()
        self.dataList_240 = None
        # 1. 清空所有动态计算的字段集合
        self._computed_fields.clear()
        
        # 2. 清空所有实例属性（核心：释放所有大数据、列表、对象引用）
        attrs = list(self.__dict__.keys())  # 先转列表避免遍历中修改报错
        for attr in attrs:
            # 保留基础初始化标记，不删除，避免后续访问报错
            if attr in ['isCalculate', 'isCalculateRank', 'isInit', '_computed_fields', 'calculateCount']:
                setattr(self, attr, False if attr != 'calculateCount' else 0)
            else:
                # 其他所有属性全部删除 = 释放内存
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

        # 3. 强制标记未初始化
        self.isInit = False


    def __getattr__(self, field_name):
        #print(f"!!!!!!{field_name}")
        if self.isInit == False:
            #print(f"！！！！！！！！！！！！！ 没有执行初始化:{field_name}")
            return None
        #print("触发首次读取")
        # 1. 如果字段不在懒加载映射里，抛出常规属性不存在异常（避免无意义递归）
        if field_name not in self.handler.CalculateBaseAttrDic:
            raise AttributeError(f"'StructBaseClass' object has no attribute '{field_name}'")
        
        # 2. 如果字段未计算，执行计算逻辑
        if field_name not in self._computed_fields:
            self.calculateCount += 1
            # 从dic中取出方法和参数
            #if field_name == "change_Ratio_5":
            calc_method = self.handler.CalculateBaseAttrDic[field_name]
            # 执行计算并赋值给实例（存入__dict__，避免再次触发__getattr__）
            t0 = time.perf_counter()
            #print(f"{self.code}  开始计算新的字段：{field_name}")

            calc_result = calc_method(self)
            t1 = time.perf_counter()
            totalCostTime = (t1 - t0)
            totalCostTimeStr1 = self.handler.main.requestor.format_seconds(totalCostTime)
            #print(f"{self.code}新的字段{field_name}计算完毕, 时间：{totalCostTimeStr1}")

            setattr(self, field_name, calc_result)
            # 标记为已计算
            self._computed_fields.add(field_name)
        
        # 3. 返回计算后的属性值（此时已存入__dict__，直接取）
        return calc_result




    dataList_240 : list[StructBaseClass]
    componyInfo: StructComponyInfoClass
    code:str
    ValueScore:float     #价值股评分
    GrowScore:float      #成长股评分

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
    avg_ori: float      #当日均价(原始价格)

    isInIndustryUp:int  #是否处在行业上涨周期

    #压力位开始----------------------------------------------------------------‘、
    up_pressure_20:float         #20日上压力位
    down_pressure_20:float       #20日下压力位

    up_pressure_40:float         #40日上压力位
    down_pressure_40:float       #40日下压力位

    up_pressure_60:float         #60日上压力位
    down_pressure_60:float       #60日下压力位

    up_pressure_120:float         #120日上压力位
    down_pressure_120:float       #120日下压力位

    up_pressure_240:float         #240日上压力位
    down_pressure_240:float       #240日下压力位


    # 单一日突破/跌破对应周期压力位（整型）
    is_break_upper_20: int      #是否突破20日上压力位
    is_break_lower_20: int      #是否跌破20日下压力位
    is_break_upper_40: int      #是否突破40日上压力位
    is_break_lower_40: int      #是否跌破40日下压力位
    is_break_upper_60: int      #是否突破60日上压力位
    is_break_lower_60: int      #是否跌破60日下压力位
    is_break_upper_120: int     #是否突破120日上压力位
    is_break_lower_120: int     #是否跌破120日下压力位
    is_break_upper_240: int     #是否突破240日上压力位
    is_break_lower_240: int     #是否跌破240日下压力位

    # 连续2日突破/跌破对应周期压力位（整型）
    is_break_upper_20_2: int   #是否连续2日突破20日上压力位
    is_break_lower_20_2: int   #是否连续2日跌破20日下压力位
    is_break_upper_40_2: int   #是否连续2日突破40日上压力位
    is_break_lower_40_2: int   #是否连续2日跌破40日下压力位
    is_break_upper_60_2: int   #是否连续2日突破60日上压力位
    is_break_lower_60_2: int   #是否连续2日跌破60日下压力位
    is_break_upper_120_2: int  #是否连续2日突破120日上压力位
    is_break_lower_120_2: int  #是否连续2日跌破120日下压力位
    is_break_upper_240_2: int  #是否连续2日突破240日上压力位
    is_break_lower_240_2: int  #是否连续2日跌破240日下压力位

    # 连续3日突破/跌破对应周期压力位（整型）
    is_break_upper_20_3: int   #是否连续3日突破20日上压力位
    is_break_lower_20_3: int   #是否连续3日跌破20日下压力位
    is_break_upper_40_3: int   #是否连续3日突破40日上压力位
    is_break_lower_40_3: int   #是否连续3日跌破40日下压力位
    is_break_upper_60_3: int   #是否连续3日突破60日上压力位
    is_break_lower_60_3: int   #是否连续3日跌破60日下压力位
    is_break_upper_120_3: int  #是否连续3日突破120日上压力位
    is_break_lower_120_3: int  #是否连续3日跌破120日下压力位
    is_break_upper_240_3: int  #是否连续3日突破240日上压力位
    is_break_lower_240_3: int  #是否连续3日跌破240日下压力位

    # 连续5日突破/跌破对应周期压力位（整型）
    is_break_upper_20_5: int   #是否连续5日突破20日上压力位
    is_break_lower_20_5: int   #是否连续5日跌破20日下压力位
    is_break_upper_40_5: int   #是否连续5日突破40日上压力位
    is_break_lower_40_5: int   #是否连续5日跌破40日下压力位
    is_break_upper_60_5: int   #是否连续5日突破60日上压力位
    is_break_lower_60_5: int   #是否连续5日跌破60日下压力位
    is_break_upper_120_5: int  #是否连续5日突破120日上压力位
    is_break_lower_120_5: int  #是否连续5日跌破120日下压力位
    is_break_upper_240_5: int  #是否连续5日突破240日上压力位
    is_break_lower_240_5: int  #是否连续5日跌破240日下压力位

    # 当日价格与20日压力位比值（浮点型）
    ratio_close_upper_20: float  #当日收盘价与20日上压力位的比
    ratio_close_lower_20: float  #当日收盘价与20日下压力位的比

    # 当日价格与40日压力位比值（浮点型）
    ratio_close_upper_40: float  #当日收盘价与40日上压力位的比
    ratio_close_lower_40: float  #当日收盘价与40日下压力位的比

    # 当日价格与60日压力位比值（浮点型）
    ratio_close_upper_60: float  #当日收盘价与60日上压力位的比
    ratio_close_lower_60: float  #当日收盘价与60日下压力位的比

    # 当日价格与120日压力位比值（浮点型）
    ratio_close_upper_120: float #当日收盘价与120日上压力位的比
    ratio_close_lower_120: float #当日收盘价与120日下压力位的比

    # 当日价格与240日压力位比值（浮点型）
    ratio_close_upper_240: float #当日收盘价与240日上压力位的比
    ratio_close_lower_240: float #当日收盘价与240日下压力位的比

    # 2日平均价格与20日压力位比值（浮点型）
    ratio_close_upper_2_20: float #2日平均收盘价与20日上压力位的比
    ratio_close_lower_2_20: float #2日平均收盘价与20日下压力位的比

    # 2日平均价格与40日压力位比值（浮点型）
    ratio_close_upper_2_40: float #2日平均收盘价与40日上压力位的比
    ratio_close_lower_2_40: float #2日平均收盘价与40日下压力位的比

    # 2日平均价格与60日压力位比值（浮点型）
    ratio_close_upper_2_60: float #2日平均收盘价与60日上压力位的比
    ratio_close_lower_2_60: float #2日平均收盘价与60日下压力位的比

    # 2日平均价格与120日压力位比值（浮点型）
    ratio_close_upper_2_120: float #2日平均收盘价与120日上压力位的比
    ratio_close_lower_2_120: float #2日平均收盘价与120日下压力位的比

    # 2日平均价格与240日压力位比值（浮点型）
    ratio_close_upper_2_240: float #2日平均收盘价与240日上压力位的比
    ratio_close_lower_2_240: float #2日平均收盘价与240日下压力位的比

    # 3日平均价格与20日压力位比值（浮点型）
    ratio_close_upper_3_20: float #3日平均收盘价与20日上压力位的比
    ratio_close_lower_3_20: float #3日平均收盘价与20日下压力位的比

    # 3日平均价格与40日压力位比值（浮点型）
    ratio_close_upper_3_40: float #3日平均收盘价与40日上压力位的比
    ratio_close_lower_3_40: float #3日平均收盘价与40日下压力位的比

    # 3日平均价格与60日压力位比值（浮点型）
    ratio_close_upper_3_60: float #3日平均收盘价与60日上压力位的比
    ratio_close_lower_3_60: float #3日平均收盘价与60日下压力位的比

    # 3日平均价格与120日压力位比值（浮点型）
    ratio_close_upper_3_120: float #3日平均收盘价与120日上压力位的比
    ratio_close_lower_3_120: float #3日平均收盘价与120日下压力位的比

    # 3日平均价格与240日压力位比值（浮点型）
    ratio_close_upper_3_240: float #3日平均收盘价与240日上压力位的比
    ratio_close_lower_3_240: float #3日平均收盘价与240日下压力位的比

    # 5日平均价格与20日压力位比值（浮点型）
    ratio_close_upper_5_20: float #5日平均收盘价与20日上压力位的比
    ratio_close_lower_5_20: float #5日平均收盘价与20日下压力位的比

    # 5日平均价格与40日压力位比值（浮点型）
    ratio_close_upper_5_40: float #5日平均收盘价与40日上压力位的比
    ratio_close_lower_5_40: float #5日平均收盘价与40日下压力位的比

    # 5日平均价格与60日压力位比值（浮点型）
    ratio_close_upper_5_60: float #5日平均收盘价与60日上压力位的比
    ratio_close_lower_5_60: float #5日平均收盘价与60日下压力位的比

    # 5日平均价格与120日压力位比值（浮点型）
    ratio_close_upper_5_120: float #5日平均收盘价与120日上压力位的比
    ratio_close_lower_5_120: float #5日平均收盘价与120日下压力位的比

    # 5日平均价格与240日压力位比值（浮点型）
    ratio_close_upper_5_240: float #5日平均收盘价与240日上压力位的比
    ratio_close_lower_5_240: float #5日平均收盘价与240日下压力位的比




    #压力位结束-------------------------------------------------------------------------------------23
    

    change_Ratio_3:float      #3日涨跌幅
    change_Ratio_5:float      #5日涨跌幅
    change_Ratio_10:float      #10日涨跌幅
    change_Ratio_20:float      #20日涨跌幅
    change_Ratio_40:float      #40日涨跌幅
    change_Ratio_60:float      #60日涨跌幅
    change_Ratio_120:float      #120日涨跌幅
    change_Ratio_240:float      #240日涨跌幅

    change_Ratio_single_3:float      #3日距今涨跌幅
    change_Ratio_single_5:float      #5日距今涨跌幅
    change_Ratio_single_10:float      #10日距今涨跌幅
    change_Ratio_single_20:float      #20日距今涨跌幅
    change_Ratio_single_40:float      #40日距今涨跌幅
    change_Ratio_single_60:float      #60日距今涨跌幅
    change_Ratio_single_120:float      #120日距今涨跌幅
    change_Ratio_single_240:float      #240日距今涨跌幅



    volume_ratio:float        #当日成交量涨跌幅

    volume_ratio_3:float        #3日成交量涨跌幅
    volume_ratio_5_percent:float        #5日成交量涨跌幅
    volume_ratio_10:float        #10日成交量涨跌幅
    volume_ratio_20:float        #20日成交量涨跌幅
    volume_ratio_40:float        #40日成交量涨跌幅

    volume_price: Optional[float]        #当日成交额
    volume_price_ratio: Optional[float]        #当日成交额涨跌幅

    volume_price_ratio_3: Optional[float]        #3日成交额涨跌幅
    volume_price_ratio_5: Optional[float]        #5日成交额涨跌幅
    volume_price_ratio_10: Optional[float]        #10日成交额涨跌幅
    volume_price_ratio_20: Optional[float]        #20日成交额涨跌幅
    volume_price_ratio_40: Optional[float]        #40日成交额涨跌幅
    
    volume_price_energy:float    #当日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_5:float    #5日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_10:float    #10日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_20:float    #20日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_60:float    #60日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_120:float    #120日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大
    volume_price_energy_240:float    #240日资金成交动量，正数越大向上推动越大，负数越小向下抛压越大



    volume_ratio_5:float       #当日量比 
    turn: float             #当日换手率  1-3（普通股）   3-5（关注股）  5-10（热门股）   10->（大热门）
    turn_value:float        #当日资金流通率   2-5（普通股）  5-8（热门股）  8 ->(大热门)
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

    total_value_ratio:float       #总市值排行业
    earn_ratio:float              #当日市盈率排行业
    clean_ratio:float             #当日市净率排行业
    cash_ratio:float              #当日市销率排行业
    sale_ratio:float              #当日市现率排行业

    volume_industry_rank:float #成交量排名(
    total_price_industry_rank:float #成交额排名(
    total_price_ratio_industry_rank:float#成交额涨跌幅排名(
    volume_ratio_industry_rank:float #成交量涨跌幅排名(
    ratio_industry_rank:float#涨跌幅排名(
    amplitude_industry_rank:float#振幅排名(
    turn_industry_rank:float#换手率涨跌幅排名(
    turn_ratio_industry_rank:float#换手率涨跌幅排名(
    avg_industry_rank:float#均价涨跌幅排名(



    #快捷指标
    # 基础状态指标（1/3/5/10/20/40/60/120周期）
    volumeState_1: float #成交量状态_1周期
    volumeState_3: float #成交量状态_3周期
    volumeState_5: float #成交量状态_5周期
    volumeState_10: float #成交量状态_10周期
    volumeState_20: float #成交量状态_20周期
    volumeState_40: float #成交量状态_40周期
    volumeState_60: float #成交量状态_60周期
    volumeState_120: float #成交量状态_120周期
    volumeState_240: float #成交量状态_240周期

    priceState_1: float #价格状态_1周期
    priceState_3: float #价格状态_3周期
    priceState_5: float #价格状态_5周期
    priceState_10: float #价格状态_10周期
    priceState_20: float #价格状态_20周期
    priceState_40: float #价格状态_40周期
    priceState_60: float #价格状态_60周期
    priceState_120: float #价格状态_120周期
    priceState_240: float #价格状态_240周期

    amplitudeState_1: float #振幅状态_1周期
    amplitudeState_3: float #振幅状态_3周期
    amplitudeState_5: float #振幅状态_5周期
    amplitudeState_10: float #振幅状态_10周期
    amplitudeState_20: float #振幅状态_20周期
    amplitudeState_40: float #振幅状态_40周期
    amplitudeState_60: float #振幅状态_60周期
    amplitudeState_120: float #振幅状态_120周期
    amplitudeState_240: float #振幅状态_240周期

    # 1日交易状态判断
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

    # 3日交易状态判断
    is_up_up_3:float#3日是否放量增长(>或小于1)
    is_low_up_3:float#3日是否缩量增长
    is_up_low_3:float#3日是否放量降低
    is_low_low_3:float#3日是否缩量降低
    is_up_mid_3:float#3日是否放量横盘
    is_low_mid_3:float#3日是否缩量横盘
    is_mid_up_3:float#3日是否平量增长
    is_mid_low_3:float#3日是否平量降低
    is_pop_up_3:float#3日是否震荡上行 （修正原字段缺失的_3后缀）
    is_pop_down_3:float#3日是否震荡下行 （修正原字段缺失的_3后缀）

    # 5日交易状态判断
    is_up_up_5:float#5日是否放量增长(>或小于1)
    is_low_up_5:float#5日是否缩量增长
    is_up_low_5:float#5日是否放量降低
    is_low_low_5:float#5日是否缩量降低
    is_up_mid_5:float#5日是否放量横盘
    is_low_mid_5:float#5日是否缩量横盘
    is_mid_up_5:float#5日是否平量增长
    is_mid_low_5:float#5日是否平量降低
    is_pop_up_5:float#5日是否震荡上行
    is_pop_down_5:float#5日是否震荡下行

    # 10日交易状态判断
    is_up_up_10:float#10日是否放量增长(>或小于1)
    is_low_up_10:float#10日是否缩量增长
    is_up_low_10:float#10日是否放量降低
    is_low_low_10:float#10日是否缩量降低
    is_up_mid_10:float#10日是否放量横盘
    is_low_mid_10:float#10日是否缩量横盘
    is_mid_up_10:float#10日是否平量增长
    is_mid_low_10:float#10日是否平量降低
    is_pop_up_10:float#10日是否震荡上行
    is_pop_down_10:float#10日是否震荡下行

    # 20日交易状态判断
    is_up_up_20:float#20日是否放量增长(>或小于1)
    is_low_up_20:float#20日是否缩量增长
    is_up_low_20:float#20日是否放量降低
    is_low_low_20:float#20日是否缩量降低
    is_up_mid_20:float#20日是否放量横盘
    is_low_mid_20:float#20日是否缩量横盘
    is_mid_up_20:float#20日是否平量增长
    is_mid_low_20:float#20日是否平量降低
    is_pop_up_20:float#20日是否震荡上行
    is_pop_down_20:float#20日是否震荡下行

    # 40日交易状态判断
    is_up_up_40:float#40日是否放量增长(>或小于1)
    is_low_up_40:float#40日是否缩量增长
    is_up_low_40:float#40日是否放量降低
    is_low_low_40:float#40日是否缩量降低
    is_up_mid_40:float#40日是否放量横盘
    is_low_mid_40:float#40日是否缩量横盘
    is_mid_up_40:float#40日是否平量增长
    is_mid_low_40:float#40日是否平量降低
    is_pop_up_40:float#40日是否震荡上行
    is_pop_down_40:float#40日是否震荡下行

    # 60日交易状态判断
    is_up_up_60:float#60日是否放量增长(>或小于1)
    is_low_up_60:float#60日是否缩量增长
    is_up_low_60:float#60日是否放量降低
    is_low_low_60:float#60日是否缩量降低
    is_up_mid_60:float#60日是否放量横盘
    is_low_mid_60:float#60日是否缩量横盘
    is_mid_up_60:float#60日是否平量增长
    is_mid_low_60:float#60日是否平量降低
    is_pop_up_60:float#60日是否震荡上行
    is_pop_down_60:float#60日是否震荡下行

    # 120日交易状态判断
    is_up_up_120:float#120日是否放量增长(>或小于1)
    is_low_up_120:float#120日是否缩量增长
    is_up_low_120:float#120日是否放量降低
    is_low_low_120:float#120日是否缩量降低
    is_up_mid_120:float#120日是否放量横盘
    is_low_mid_120:float#120日是否缩量横盘
    is_mid_up_120:float#120日是否平量增长
    is_mid_low_120:float#120日是否平量降低
    is_pop_up_120:float#120日是否震荡上行
    is_pop_down_120:float#120日是否震荡下行

    is_up_up_240:float#240日是否放量增长(>或小于1)
    is_low_up_240:float#240日是否缩量增长
    is_up_low_240:float#240日是否放量降低
    is_low_low_240:float#240日是否缩量降低
    is_up_mid_240:float#240日是否放量横盘
    is_low_mid_240:float#240日是否缩量横盘
    is_mid_up_240:float#240日是否平量增长
    is_mid_low_240:float#240日是否平量降低
    is_pop_up_240:float#240日是否震荡上行
    is_pop_down_240:float#240日是否震荡下行





    is_up_stop:int #是否涨停
    is_down_stop:int#是否跌停
    is_touch_up_stop:int#是否触及涨停
    is_touch_down_stop:int#是否触及跌停



    is_one_ban:int     #是否一字板

    is_short_entity:int     #是否短实体
    
    is_long_shadow_up:int#是否长上影线
    is_long_shadow_down:int#是否长下影线

    is_long_cross:int#是否长十字
    is_short_cross:int#是否短十字

    is_T_up:int#是否正T字
    is_T_down:int#是否倒T字


    #是否是成长股
    #是否是价值股
    ##支当日收盘价与支撑位


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
        self.trade_date_from = self.startDataCls.trade_date
        self.industry = handler.totalComponyIns.GetComponyInfo(self.code).Industry
        self.isST = self.startDataCls.isST
        #if self.code == "688152.SH":
        #    print(f"麒麟信安的设置：{self.startCount}，  {self.toCount}")


    def Clear(self):
        """
        彻底清空当前对象的所有属性，释放内存
        调用后对象仅保留基础标记，所有数据字段全部删除
        """
        # 1. 清空所有动态计算的字段集合
        self._computed_fields.clear()
        
        # 2. 清空所有实例属性（核心：释放所有大数据、列表、对象引用）
        attrs = list(self.__dict__.keys())  # 先转列表避免遍历中修改报错
        for attr in attrs:
            # 保留基础初始化标记，不删除，避免后续访问报错
            if attr in ['isCalculate', 'isCalculateRank', 'isInit', '_computed_fields', 'calculateCount']:
                setattr(self, attr, False if attr != 'calculateCount' else 0)
            else:
                # 其他所有属性全部删除 = 释放内存
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

        # 3. 强制标记未初始化
        self.isInit = False


    def __getattr__(self, field_name):
        if self.isInit == False:
            return None
        #print("触发首次读取")
        # 1. 如果字段不在懒加载映射里，抛出常规属性不存在异常（避免无意义递归）
        if field_name not in self.handler.CalculateBaseWindowAttrDic:
            raise AttributeError(f"'StructBaseWindowClass' object has no attribute '{field_name}'")
        

        # 2. 如果字段未计算，执行计算逻辑
        if field_name not in self._computed_fields:
            self.calculateCount += 1
            # 从dic中取出方法和参数
            #if field_name == "change_Ratio_5":
            #    print("???????执行啊啊啊啊啊啊啊")
            calc_method, args_names = self.handler.CalculateBaseWindowAttrDic[field_name]

            real_args = []
            for arg_name in args_names:
                if arg_name == "self":
                    real_args.append(self)
                else:
                    real_args.append(getattr(self, arg_name))

            # 执行计算（对lambda表达式，传入self作为cls参数）
            if callable(calc_method) and calc_method.__name__ == "<lambda>":
                # lambda表达式特殊处理：传入self作为cls参数
                calc_result = calc_method(self)
            else:
                # 普通函数：传入解析后的实际参数
                calc_result = calc_method(*real_args)

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
    avg_volume_price:float        #平均成交额
    avg_volume_rito:float       #平均量比 
    avg_turn: float             #平均换手率
    avg_change_Ratio:float      #平均涨跌幅
    avg_amplitude:float         #平均振幅
    avg_avg:float         #平均均价

    #压力位开始---------------------------------------------------------------------------
    # 区间压力位突破/跌破次数（整型）
    break_upper_count_20: int      #区间突破20日上压力位次数
    break_lower_count_20: int      #区间跌破20日下压力位次数
    break_upper_count_40: int      #区间突破40日上压力位次数
    break_lower_count_40: int      #区间跌破40日下压力位次数
    break_upper_count_60: int      #区间突破60日上压力位次数
    break_lower_count_60: int      #区间跌破60日下压力位次数
    break_upper_count_120: int     #区间突破120日上压力位次数
    break_lower_count_120: int     #区间跌破120日下压力位次数
    break_upper_count_240: int     #区间突破240日上压力位次数
    break_lower_count_240: int     #区间跌破240日下压力位次数

    # 区间平均价格与20日压力位比值（浮点型）
    ratio_avg_close_upper_20: float  #区间平均收盘价与20日上压力位的比
    ratio_avg_close_lower_20: float  #区间平均收盘价与20日下压力位的比

    # 区间平均价格与40日压力位比值（浮点型）
    ratio_avg_close_upper_40: float  #区间平均收盘价与40日上压力位的比
    ratio_avg_close_lower_40: float  #区间平均收盘价与40日下压力位的比

    # 区间平均价格与60日压力位比值（浮点型）
    ratio_avg_close_upper_60: float  #区间平均收盘价与60日上压力位的比
    ratio_avg_close_lower_60: float  #区间平均收盘价与60日下压力位的比

    # 区间平均价格与120日压力位比值（浮点型）
    ratio_avg_close_upper_120: float #区间平均收盘价与120日上压力位的比
    ratio_avg_close_lower_120: float #区间平均收盘价与120日下压力位的比

    # 区间平均价格与240日压力位比值（浮点型）
    ratio_avg_close_upper_240: float #区间平均收盘价与240日上压力位的比
    ratio_avg_close_lower_240: float #区间平均收盘价与240日下压力位的比
    #压力位结束---------------------------------------------------------------------------



    min_open: float         #最低开盘价
    min_close: float            #最低收盘价
    min_last_close: float       #最低昨收价
    min_high: float         #最低最高价
    min_low: float          #最低最低价
    min_volume: float        #最低成交量
    min_volume_price:float        #最低成交额
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
    max_volume_price:float        #最高成交额
    max_volume_rito:float       #最高量比 
    max_turn: float             #最高换手率
    max_change_Ratio:float      #最高涨跌幅
    max_amplitude:float         #最高振幅
    max_avg:float         #最高均价

    
    volume_industry_rank:float #成交量排名(
    total_price_industry_rank:float #成交额排名(
    total_price_ratio_industry_rank:float#成交额涨跌幅排名(
    volume_ratio_industry_rank:float #成交量涨跌幅排名(
    ratio_industry_rank:float#涨跌幅排名(
    amplitude_industry_rank:float#振幅排名(
    turn_ratio_industry_rank:float#换手率涨跌幅排名(
    avg_industry_rank:float#均价涨跌幅排名(


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



class StructIndustryClass():
    name:str        #行业名
    trade_date:date #交易日期
    volume: float   #成交量
    volume_ratio:float        #成交量涨跌幅
    volume_ratio_3:float        #当日成交量与3日平均成交量的比
    volume_ratio_5:float        #当日成交量与5日平均成交量的比
    volume_ratio_10:float        #当日成交量与10日平均成交量的比
    volume_ratio_20:float        #当日成交量与20日平均成交量的比


    volume_price:float        #成交额
    volume_price_ratio:float        #成交额涨跌幅

    volume_price_ratio_3:float        #当日成交额与3日平均成交额的比
    volume_price_ratio_5:float        #当日成交额与5日平均成交额的比
    volume_price_ratio_10:float        #当日成交额与10日平均成交额的比
    volume_price_ratio_20:float        #当日成交额与20日平均成交额的比


    change_Ratio:float      #行业涨整体跌幅
    stockNum:int            #行业股数量

    stockNum_up:int         #行业上涨股数量
    stockNum_up_Ratio:int         #行业上涨股比例
    
    stockNum_down:int       #行业下跌股数量
    stockNum_down_Ratio:int         #行业下跌股比例
    def __init__(self):
        self.isInit = False
        self._computed_fields = set()

    def Init(self, industryInfoCls:StructIndustryInfoClass, trade_date, handler):
        self.industryInfoCls = industryInfoCls
        self.handler = handler
        self.trade_date = trade_date
        self.isInit = True
        self.calculateCount = 0
        self.name = industryInfoCls.industryName

    def Clear(self):
        """
        彻底清空当前对象的所有属性，释放内存
        调用后对象仅保留基础标记，所有数据字段全部删除
        """
        # 1. 清空所有动态计算的字段集合
        self._computed_fields.clear()
        
        # 2. 清空所有实例属性（核心：释放所有大数据、列表、对象引用）
        attrs = list(self.__dict__.keys())  # 先转列表避免遍历中修改报错
        for attr in attrs:
            # 保留基础初始化标记，不删除，避免后续访问报错
            if attr in ['isCalculate', 'isCalculateRank', 'isInit', '_computed_fields', 'calculateCount']:
                setattr(self, attr, False if attr != 'calculateCount' else 0)
            else:
                # 其他所有属性全部删除 = 释放内存
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

        # 3. 强制标记未初始化
        self.isInit = False


    def __getattr__(self, field_name):
        # 未初始化直接返回None
        if self.isInit == False:
            return None
        
        # 1. 字段不在映射字典中，抛出标准异常
        if field_name not in self.handler.CalculateIndustryBaseClassAttrDic:
            raise AttributeError(f"'StructIndustryBaseClass' object has no attribute '{field_name}'")
        
        # 2. 字段未计算则执行计算逻辑
        if field_name not in self._computed_fields:
            self.calculateCount += 1
            
            # 字典格式：(计算方法, 完整参数列表)
            # 参数列表元素规则：
            # - "self": 当前实例本身（原逻辑的self）
            # - "handler": 指向self.handler（核心修正）
            # - 其他字符串：从self中读取对应属性（如 "industryInfoCls"）
            # - 非字符串：固定值（如 1/3/5）
            calc_method, full_args = self.handler.CalculateIndustryBaseClassAttrDic[field_name]
            
            # 组装最终参数：解析特殊关键字 + 动态参数 + 固定值
            t0 = time.perf_counter()
            try:
                args = []
                for arg in full_args:
                    if arg == "self":
                        # 指向当前实例（原逻辑的self）
                        args.append(self)
                    elif arg == "handler":
                        # 核心修正：指向handler（而非当前实例self）
                        args.append(self.handler)
                    elif isinstance(arg, str):
                        # 其他字符串=从self取属性
                        args.append(getattr(self, arg))
                    else:
                        # 非字符串=固定值
                        args.append(arg)
                
                # 执行计算（纯位置参数，无关键字参数）
                calc_result = calc_method(*args)
            except Exception as e:
                print(f"计算字段 {field_name} 失败: {str(e)}")
                calc_result = None
            
            t1 = time.perf_counter()
            totalCostTime = (t1 - t0)
            totalCostTimeStr1 = self.handler.main.requestor.format_seconds(totalCostTime)
            
            # 赋值并标记已计算
            setattr(self, field_name, calc_result)
            self._computed_fields.add(field_name)
        
        # 3. 返回计算结果
        return getattr(self, field_name)


class StructIndustryWindowClass():
    name:str        #行业名
    stockNum:int            #行业股数量

    volume: float   #整体成交量
    volume_price:float        #整体成交额
    avg_volume: float   #平均成交量
    avg_volume_price:float        #平均成交额


    volume_ratio:float        #整体成交量涨跌幅
    volume_price_ratio:float        #整体成交额涨跌幅

    change_Ratio:float      #行业涨跌幅
    change_Ratio_Total:float      #整体行业涨跌幅

    avg_stockNum_up:int         #平均行业上涨股数量
    avg_stockNum_down:int       #平均行业下跌股数量
    
    stockNum_up_Ratio:int         #平均行业上涨股比例
    stockNum_down_Ratio:int         #平均行业下跌股比例
    def __init__(self):
        self.isInit = False
        self._computed_fields = set()
    def Init(self, industryInfoCls:StructIndustryInfoClass, trade_date, startDateCount, toDateCount, handler):
        self.industryInfoCls = industryInfoCls
        self.handler = handler
        self.trade_date = trade_date
        self.startDateCount = startDateCount
        self.toDateCount = toDateCount
        self.isInit = True
        self.calculateCount = 0
        self.name = industryInfoCls.industryName
        self.stockNum = len(industryInfoCls.stockList)


    def Clear(self):
        """
        彻底清空当前对象的所有属性，释放内存
        调用后对象仅保留基础标记，所有数据字段全部删除
        """
        # 1. 清空所有动态计算的字段集合
        self._computed_fields.clear()
        
        # 2. 清空所有实例属性（核心：释放所有大数据、列表、对象引用）
        attrs = list(self.__dict__.keys())  # 先转列表避免遍历中修改报错
        for attr in attrs:
            # 保留基础初始化标记，不删除，避免后续访问报错
            if attr in ['isCalculate', 'isCalculateRank', 'isInit', '_computed_fields', 'calculateCount']:
                setattr(self, attr, False if attr != 'calculateCount' else 0)
            else:
                # 其他所有属性全部删除 = 释放内存
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

        # 3. 强制标记未初始化
        self.isInit = False


    def __getattr__(self, field_name):
        if self.isInit == False:
            return None
        #print("触发首次读取")
        # 1. 如果字段不在懒加载映射里，抛出常规属性不存在异常（避免无意义递归）
        if field_name not in self.handler.CalculateIndustryWindowClassAttrDic:
            raise AttributeError(f"'StructIndustryWindowClass' object has no attribute '{field_name}'")
        

        # 2. 如果字段未计算，执行计算逻辑
        if field_name not in self._computed_fields:
            self.calculateCount += 1
            # 从dic中取出方法和参数
            #if field_name == "change_Ratio_5":
            #    print("???????执行啊啊啊啊啊啊啊")
            calc_method, args_names = self.handler.CalculateIndustryWindowClassAttrDic[field_name]

            real_args = []
            for arg_name in args_names:
                if arg_name == "self":
                    real_args.append(self)
                else:
                    real_args.append(getattr(self, arg_name))

            # 执行计算（对lambda表达式，传入self作为cls参数）
            if callable(calc_method) and calc_method.__name__ == "<lambda>":
                # lambda表达式特殊处理：传入self作为cls参数
                calc_result = calc_method(self)
            else:
                # 普通函数：传入解析后的实际参数
                calc_result = calc_method(*real_args)

            setattr(self, field_name, calc_result)
            # 标记为已计算
            self._computed_fields.add(field_name)
        
        # 3. 返回计算后的属性值（此时已存入__dict__，直接取）
        return calc_result





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

    Roe:float               #roe：净资产收益率
    YOYNi : float           #净利润同比增长率
    LiabilityTo: float      #资产负债率 
    YOYEquity : float       #净资产同比增长率
    YOYLiability: float     #负债同比增长率
    
    Value_Score : float
    Grow_Score : float

    def __init__(self):
        self.Total_Value = 0
        self.Earn = 0
        self.Clean = 0
        self.Cash = 0
        self.Sale = 0
        self.Roe = 0
        self.YOYNi = 0
        self.LiabilityTo = 0
        self.YOYEquity = 0
        self.YOYLiability = 0

        self.Roe_Year = 0
        self.YOYNi_Year = 0
        self.LiabilityTo_Year = 0
        self.YOYEquity_Year = 0
        self.YOYLiability_Year = 0

        self.Value_Score = 0
        self.Grow_Score = 0


    #计算价值股或成长股得分, 计算指标得分，指标加权重，  判断优秀程度加不同的分，越优秀加的越多，越劣势减的越多， 为0的参数不参与计算
    def CalculationValueScore():
        pass


class StructIndustryInfoClass:
    industryName : str
    isCalculate:bool
    def __init__(self):
        self.stockList : Dict[str, StructComponyInfoClass] = {}
        self.stockForSortList : list[StructComponyInfoClass] = []
        self.isCalculate = False
        
        

class StructIndustryTotalInfoClass:
    def __init__(self):
        self.industryList:Dict[str,StructIndustryInfoClass] = {}
        self.allStockList:Dict[str,StructComponyInfoClass] = {}
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




class IndustryAnalysisResult:
    allDic:Dict[(str, str),List:[str]]
    def __init__(self):
        self.allDic = {}