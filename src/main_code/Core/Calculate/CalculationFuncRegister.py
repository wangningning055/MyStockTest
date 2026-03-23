def RegisterCalculateFunc(calculationHandler):
    from src.main_code.Core.Calculate import CalculationUtil
    from functools import partial

    calculationHandler.CalculateBaseWindowAttrDic = {
        # -------------------------- 涨跌停相关 --------------------------
        "up_stopCount": (CalculationUtil.GetUpStopCount, ("startDataCls", "startCount", "toCount")),
        "down_stopCount": (CalculationUtil.GetDownStopCount, ("startDataCls", "startCount", "toCount")),
        
        # -------------------------- 基础量价相关 --------------------------
        "volume": (CalculationUtil.GetVolume_Window, ("startDataCls", "startCount", "toCount")),
        "volume_price": (CalculationUtil.GetVolume_Price_Window, ("startDataCls", "startCount", "toCount")),
        "volume_ratio": (CalculationUtil.GetVolume_Ratio_Window, ("startDataCls", "startCount", "toCount")),
        "volume_price_ratio": (CalculationUtil.GetVolume_Price_Ratio_Window, ("startDataCls", "startCount", "toCount")),

        "turn_ratio": (CalculationUtil.GetTurn_Ratio_Window, ("startDataCls", "startCount", "toCount")),
        "change_Ratio": (CalculationUtil.GetChange_Ratio_Window, ("startDataCls", "startCount", "toCount")),
        "change_Ratio_Total": (CalculationUtil.GetChange_Ratio_Total_Window, ("startDataCls", "startCount", "toCount")),
        "avg_Ratio": (CalculationUtil.GetAvg_Ratio_Window, ("startDataCls", "startCount", "toCount")),
        "avg_Ratio_Total": (CalculationUtil.GetAvg_Ratio_Total_Window, ("startDataCls", "startCount", "toCount")),
        
        # -------------------------- 平均值类字段 --------------------------
        "avg_open": (CalculationUtil.GetOpen_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_close": (CalculationUtil.GetClose_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_high": (CalculationUtil.GetHigh_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_low": (CalculationUtil.GetLow_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_volume": (CalculationUtil.GetVolume_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_volume_price": (CalculationUtil.GetVolume_Price_Window_Avg, ("startDataCls", "startCount", "toCount")),

        "avg_volume_rito": (CalculationUtil.Get_VolumeRatio_5_Window_Avg, ("startDataCls", "startCount", "toCount", "handler")),
        "avg_turn": (CalculationUtil.GetTurn_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_change_Ratio": (CalculationUtil.GetChangeRatio_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_amplitude": (CalculationUtil.GetAmplitude_Window_Avg, ("startDataCls", "startCount", "toCount")),
        "avg_avg": (CalculationUtil.GetAvg_Price_Window_Avg, ("startDataCls", "startCount", "toCount")),
        
        # -------------------------- 最小值类字段 --------------------------
        "min_open": (CalculationUtil.GetOpen_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_close": (CalculationUtil.GetClose_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_last_close": (CalculationUtil.GetLastClose_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_high": (CalculationUtil.GetHigh_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_low": (CalculationUtil.GetLow_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_volume": (CalculationUtil.GetVolume_Window_Low, ("startDataCls", "startCount", "toCount")),

        "min_volume_price": (CalculationUtil.GetVolume_Price_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_volume_rito": (CalculationUtil.GetVolume_Ratio_5_Window_Low, ("startDataCls", "startCount", "toCount", "handler")),
        "min_turn": (CalculationUtil.GetTurn_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_change_Ratio": (CalculationUtil.GetChange_Ratio_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_amplitude": (CalculationUtil.GetAmplitude_Window_Low, ("startDataCls", "startCount", "toCount")),
        "min_avg": (CalculationUtil.GetAvg_Window_Low, ("startDataCls", "startCount", "toCount")),
        
        # -------------------------- 最大值类字段 --------------------------
        "max_open": (CalculationUtil.GetOpen_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_close": (CalculationUtil.GetClose_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_last_close": (CalculationUtil.GetLastClose_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_high": (CalculationUtil.GetHigh_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_low": (CalculationUtil.GetLow_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_volume": (CalculationUtil.GetVolume_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_volume_price": (CalculationUtil.GetVolume_Price_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_volume_rito": (CalculationUtil.GetVolume_Ratio_5_Window_High, ("startDataCls", "startCount", "toCount", "handler")),
        "max_turn": (CalculationUtil.GetTurn_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_change_Ratio": (CalculationUtil.GetChange_Ratio_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_amplitude": (CalculationUtil.GetAmplitude_Window_High, ("startDataCls", "startCount", "toCount")),
        "max_avg": (CalculationUtil.GetAvg_Window_High, ("startDataCls", "startCount", "toCount")),
        
        # -------------------------- 状态类字段（依赖windowsClass） --------------------------
        "volumeState": (CalculationUtil.GetVolume_State_Windows, ("self",)),
        "priceState": (CalculationUtil.GetChange_Ratio_State_Windows, ("self",)),
        "amplitudeState": (CalculationUtil.GetAmplitude_State_Windows, ("self",)),
        
        # -------------------------- 行业排名类字段 --------------------------
        "volume_industry_rank": (CalculationUtil.GetVolume_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "total_price_industry_rank": (CalculationUtil.GetVolume_Price_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "total_price_ratio_industry_rank": (CalculationUtil.GetVolume_Price_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "volume_ratio_industry_rank": (CalculationUtil.GetVolume_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "ratio_industry_rank": (CalculationUtil.GetChange_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "amplitude_industry_rank": (CalculationUtil.GetAmplitude_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "turn_ratio_industry_rank": (CalculationUtil.GetTurn_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),
        "avg_industry_rank": (CalculationUtil.GetAvg_Ratio_Window_Rank, ("startDataCls", "startCount", "toCount", "handler")),


        "is_up_up": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == 1 else 0, ()),
        "is_low_up": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == 1 else 0, ()),
        "is_up_low": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == -1 else 0, ()),
        "is_low_low": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == -1 else 0, ()),
        "is_up_mid": (lambda cls: 1 if cls.volumeState == 1 and cls.priceState == 0 else 0, ()),
        "is_low_mid": (lambda cls: 1 if cls.volumeState == -1 and cls.priceState == 0 else 0, ()),
        "is_mid_up": (lambda cls: 1 if cls.volumeState == 0 and cls.priceState == 1 else 0, ()),
        "is_mid_low": (lambda cls: 1 if cls.volumeState == 0 and cls.priceState == -1 else 0, ()),
        
        # 振幅+价格组合属性
        "is_pop_up": (lambda cls: 1 if cls.amplitudeState == 1 and cls.priceState == 1 else 0, ()),
        "is_pop_down": (lambda cls: 1 if cls.amplitudeState == 1 and cls.priceState == -1 else 0, ()),


        #break_upper_count_20: int      #区间突破20日上压力位次数
        "break_upper_count_20": (CalculationUtil.GetBreakUpCount_20, ("startDataCls", "startCount", "toCount")),
        #break_lower_count_20: int      #区间跌破20日下压力位次数
        "break_lower_count_20": (CalculationUtil.GetBreakDownCount_20, ("startDataCls", "startCount", "toCount")),

        #break_upper_count_40: int      #区间突破40日上压力位次数
        "break_upper_count_40": (CalculationUtil.GetBreakUpCount_40, ("startDataCls", "startCount", "toCount")),
        #break_lower_count_40: int      #区间跌破40日下压力位次数
        "break_lower_count_40": (CalculationUtil.GetBreakDownCount_40, ("startDataCls", "startCount", "toCount")),

        #break_upper_count_60: int      #区间突破60日上压力位次数
        "break_upper_count_60": (CalculationUtil.GetBreakUpCount_60, ("startDataCls", "startCount", "toCount")),
        #break_lower_count_60: int      #区间跌破60日下压力位次数
        "break_lower_count_60": (CalculationUtil.GetBreakDownCount_60, ("startDataCls", "startCount", "toCount")),

        #break_upper_count_120: int     #区间突破120日上压力位次数
        "break_upper_count_120": (CalculationUtil.GetBreakUpCount_120, ("startDataCls", "startCount", "toCount")),
        #break_lower_count_120: int     #区间跌破120日下压力位次数
        "break_lower_count_120": (CalculationUtil.GetBreakDownCount_120, ("startDataCls", "startCount", "toCount")),

        #break_upper_count_240: int     #区间突破240日上压力位次数
        "break_upper_count_240": (CalculationUtil.GetBreakUpCount_240, ("startDataCls", "startCount", "toCount")),
        #break_lower_count_240: int     #区间跌破240日下压力位次数
        "break_lower_count_240": (CalculationUtil.GetBreakDownCount_240, ("startDataCls", "startCount", "toCount")),

        ## 区间平均价格与20日压力位比值（浮点型）
        #ratio_avg_close_upper_20: float  #区间平均收盘价与20日上压力位的比
        "ratio_avg_close_upper_20": (CalculationUtil.Get_Close_Break_Up_Ratio_20, ("startDataCls", "startCount", "toCount", "handler")),
        #ratio_avg_close_lower_20: float  #区间平均收盘价与20日下压力位的比
        "ratio_avg_close_lower_20": (CalculationUtil.Get_Close_Break_Low_Ratio_20, ("startDataCls", "startCount", "toCount", "handler")),

        ## 区间平均价格与40日压力位比值（浮点型）
        #ratio_avg_close_upper_40: float  #区间平均收盘价与40日上压力位的比
        "ratio_avg_close_upper_40": (CalculationUtil.Get_Close_Break_Up_Ratio_40, ("startDataCls", "startCount", "toCount", "handler")),
        #ratio_avg_close_lower_40: float  #区间平均收盘价与40日下压力位的比
        "ratio_avg_close_lower_40": (CalculationUtil.Get_Close_Break_Low_Ratio_40, ("startDataCls", "startCount", "toCount", "handler")),

        ## 区间平均价格与60日压力位比值（浮点型）
        #ratio_avg_close_upper_60: float  #区间平均收盘价与60日上压力位的比
        "ratio_avg_close_upper_60": (CalculationUtil.Get_Close_Break_Up_Ratio_60, ("startDataCls", "startCount", "toCount", "handler")),
        #ratio_avg_close_lower_60: float  #区间平均收盘价与60日下压力位的比
        "ratio_avg_close_lower_60": (CalculationUtil.Get_Close_Break_Low_Ratio_60, ("startDataCls", "startCount", "toCount", "handler")),

        ## 区间平均价格与120日压力位比值（浮点型）
        #ratio_avg_close_upper_120: float #区间平均收盘价与120日上压力位的比
        "ratio_avg_close_upper_120": (CalculationUtil.Get_Close_Break_Up_Ratio_120, ("startDataCls", "startCount", "toCount", "handler")),
        #ratio_avg_close_lower_120: float #区间平均收盘价与120日下压力位的比
        "ratio_avg_close_lower_120": (CalculationUtil.Get_Close_Break_Low_Ratio_120, ("startDataCls", "startCount", "toCount", "handler")),

        ## 区间平均价格与240日压力位比值（浮点型）
        #ratio_avg_close_upper_240: float #区间平均收盘价与240日上压力位的比
        "ratio_avg_close_upper_240": (CalculationUtil.Get_Close_Break_Up_Ratio_240, ("startDataCls", "startCount", "toCount", "handler")),
        #ratio_avg_close_lower_240: float #区间平均收盘价与240日下压力位的比
        "ratio_avg_close_lower_240": (CalculationUtil.Get_Close_Break_Low_Ratio_240, ("startDataCls", "startCount", "toCount", "handler")),

    }


    calculationHandler.CalculateBaseAttrDic = {
        "dataList_240" :partial(calculationHandler.GetLastDateDataByNum, dayNum = 240),

        "isInIndustryUp" :partial(CalculationUtil.GetIsInIndustryUp, handler = calculationHandler),

        "ValueScore" :partial(CalculationUtil.GetValueScore, handler = calculationHandler),
        "GrowScore" :partial(CalculationUtil.GetGrowScore, handler = calculationHandler),

        "up_pressure_20": partial(CalculationUtil.GetUpPressure, BreakWindowCount = 20, handler = calculationHandler),
        "down_pressure_20": partial(CalculationUtil.GetDownPressure, BreakWindowCount = 20, handler = calculationHandler),

        "up_pressure_40": partial(CalculationUtil.GetUpPressure, BreakWindowCount = 40, handler = calculationHandler),
        "down_pressure_40": partial(CalculationUtil.GetDownPressure, BreakWindowCount = 40, handler = calculationHandler),

        "up_pressure_60": partial(CalculationUtil.GetUpPressure, BreakWindowCount = 60, handler = calculationHandler),
        "down_pressure_60": partial(CalculationUtil.GetDownPressure, BreakWindowCount = 60, handler = calculationHandler),

        "up_pressure_120": partial(CalculationUtil.GetUpPressure, BreakWindowCount = 120, handler = calculationHandler),
        "down_pressure_120": partial(CalculationUtil.GetDownPressure, BreakWindowCount = 120, handler = calculationHandler),

        "up_pressure_240": partial(CalculationUtil.GetUpPressure, BreakWindowCount = 240, handler = calculationHandler),
        "down_pressure_240": partial(CalculationUtil.GetDownPressure, BreakWindowCount = 240, handler = calculationHandler),


        ## 单一日突破/跌破对应周期压力位（整型）
        #is_break_upper_20: int      #是否突破20日上压力位
        "is_break_upper_20": partial(CalculationUtil.GetIsBreakUpPressure, BreakWindowCount = 20),
        #is_break_lower_20: int      #是否跌破20日下压力位
        "is_break_lower_20": partial(CalculationUtil.GetIsBreakDownPressure, BreakWindowCount = 20),
        
        #is_break_upper_40: int      #是否突破40日上压力位
        "is_break_upper_40": partial(CalculationUtil.GetIsBreakUpPressure, BreakWindowCount = 40),
        #is_break_lower_40: int      #是否跌破40日下压力位
        "is_break_lower_40": partial(CalculationUtil.GetIsBreakDownPressure, BreakWindowCount = 40),

        #is_break_upper_60: int      #是否突破60日上压力位
        "is_break_upper_60": partial(CalculationUtil.GetIsBreakUpPressure, BreakWindowCount = 60),
        #is_break_lower_60: int      #是否跌破60日下压力位
        "is_break_lower_60": partial(CalculationUtil.GetIsBreakDownPressure, BreakWindowCount = 60),

        #is_break_upper_120: int     #是否突破120日上压力位
        "is_break_upper_120": partial(CalculationUtil.GetIsBreakUpPressure, BreakWindowCount = 120),
        #is_break_lower_120: int     #是否跌破120日下压力位
        "is_break_lower_120": partial(CalculationUtil.GetIsBreakDownPressure, BreakWindowCount = 120),

        #is_break_upper_240: int     #是否突破240日上压力位
        "is_break_upper_240": partial(CalculationUtil.GetIsBreakUpPressure, BreakWindowCount = 240),
        #is_break_lower_240: int     #是否跌破240日下压力位
        "is_break_lower_240": partial(CalculationUtil.GetIsBreakDownPressure, BreakWindowCount = 240),

        ## 连续2日突破/跌破对应周期压力位（整型）
        # is_break_upper_20_2: int   #是否连续2日突破20日上压力位
        "is_break_upper_20_2": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=2, BreakWindowCount=20),
        # is_break_lower_20_2: int   #是否连续2日跌破20日下压力位
        "is_break_lower_20_2": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=2, BreakWindowCount=20),
        # is_break_upper_40_2: int   #是否连续2日突破40日上压力位
        "is_break_upper_40_2": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=2, BreakWindowCount=40),
        # is_break_lower_40_2: int   #是否连续2日跌破40日下压力位
        "is_break_lower_40_2": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=2, BreakWindowCount=40),
        # is_break_upper_60_2: int   #是否连续2日突破60日上压力位
        "is_break_upper_60_2": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=2, BreakWindowCount=60),
        # is_break_lower_60_2: int   #是否连续2日跌破60日下压力位
        "is_break_lower_60_2": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=2, BreakWindowCount=60),
        # is_break_upper_120_2: int  #是否连续2日突破120日上压力位
        "is_break_upper_120_2": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=2, BreakWindowCount=120),
        # is_break_lower_120_2: int  #是否连续2日跌破120日下压力位
        "is_break_lower_120_2": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=2, BreakWindowCount=120),
        # is_break_upper_240_2: int  #是否连续2日突破240日上压力位
        "is_break_upper_240_2": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=2, BreakWindowCount=240),
        # is_break_lower_240_2: int  #是否连续2日跌破240日下压力位
        "is_break_lower_240_2": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=2, BreakWindowCount=240),

        ## 连续3日突破/跌破对应周期压力位（整型）
        # is_break_upper_20_3: int   #是否连续3日突破20日上压力位
        "is_break_upper_20_3": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=3, BreakWindowCount=20),
        # is_break_lower_20_3: int   #是否连续3日跌破20日下压力位
        "is_break_lower_20_3": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=3, BreakWindowCount=20),
        # is_break_upper_40_3: int   #是否连续3日突破40日上压力位
        "is_break_upper_40_3": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=3, BreakWindowCount=40),
        # is_break_lower_40_3: int   #是否连续3日跌破40日下压力位
        "is_break_lower_40_3": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=3, BreakWindowCount=40),
        # is_break_upper_60_3: int   #是否连续3日突破60日上压力位
        "is_break_upper_60_3": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=3, BreakWindowCount=60),
        # is_break_lower_60_3: int   #是否连续3日跌破60日下压力位
        "is_break_lower_60_3": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=3, BreakWindowCount=60),
        # is_break_upper_120_3: int  #是否连续3日突破120日上压力位
        "is_break_upper_120_3": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=3, BreakWindowCount=120),
        # is_break_lower_120_3: int  #是否连续3日跌破120日下压力位
        "is_break_lower_120_3": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=3, BreakWindowCount=120),
        # is_break_upper_240_3: int  #是否连续3日突破240日上压力位
        "is_break_upper_240_3": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=3, BreakWindowCount=240),
        # is_break_lower_240_3: int  #是否连续3日跌破240日下压力位
        "is_break_lower_240_3": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=3, BreakWindowCount=240),

        ## 连续5日突破/跌破对应周期压力位（整型）
        # is_break_upper_20_5: int   #是否连续5日突破20日上压力位
        "is_break_upper_20_5": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=5, BreakWindowCount=20),
        # is_break_lower_20_5: int   #是否连续5日跌破20日下压力位
        "is_break_lower_20_5": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=5, BreakWindowCount=20),
        # is_break_upper_40_5: int   #是否连续5日突破40日上压力位
        "is_break_upper_40_5": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=5, BreakWindowCount=40),
        # is_break_lower_40_5: int   #是否连续5日跌破40日下压力位
        "is_break_lower_40_5": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=5, BreakWindowCount=40),
        # is_break_upper_60_5: int   #是否连续5日突破60日上压力位
        "is_break_upper_60_5": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=5, BreakWindowCount=60),
        # is_break_lower_60_5: int   #是否连续5日跌破60日下压力位
        "is_break_lower_60_5": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=5, BreakWindowCount=60),
        # is_break_upper_120_5: int  #是否连续5日突破120日上压力位
        "is_break_upper_120_5": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=5, BreakWindowCount=120),
        # is_break_lower_120_5: int  #是否连续5日跌破120日下压力位
        "is_break_lower_120_5": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=5, BreakWindowCount=120),
        # is_break_upper_240_5: int  #是否连续5日突破240日上压力位
        "is_break_upper_240_5": partial(CalculationUtil.GetIsBreakUpPressure_Length, Length=5, BreakWindowCount=240),
        # is_break_lower_240_5: int  #是否连续5日跌破240日下压力位
        "is_break_lower_240_5": partial(CalculationUtil.GetIsBreakDownPressure_Length, Length=5, BreakWindowCount=240),


        ## 当日价格与20日压力位比值（浮点型）
        #ratio_close_upper_20: float  #当日收盘价与20日上压力位的比
        "ratio_close_upper_20": (lambda cls: cls.close / cls.up_pressure_20),
        #ratio_close_lower_20: float  #当日收盘价与20日下压力位的比
        "ratio_close_lower_20": (lambda cls: cls.close / cls.down_pressure_20),

        ## 当日价格与40日压力位比值（浮点型）
        #ratio_close_upper_40: float  #当日收盘价与40日上压力位的比
        "ratio_close_upper_20": (lambda cls: cls.close / cls.up_pressure_40),
        #ratio_close_lower_40: float  #当日收盘价与40日下压力位的比
        "ratio_close_lower_20": (lambda cls: cls.close / cls.down_pressure_40),

        ## 当日价格与60日压力位比值（浮点型）
        #ratio_close_upper_60: float  #当日收盘价与60日上压力位的比
        "ratio_close_upper_20": (lambda cls: cls.close / cls.up_pressure_60),
        #ratio_close_lower_60: float  #当日收盘价与60日下压力位的比
        "ratio_close_lower_20": (lambda cls: cls.close / cls.down_pressure_60),

        ## 当日价格与120日压力位比值（浮点型）
        #ratio_close_upper_120: float #当日收盘价与120日上压力位的比
        "ratio_close_upper_20": (lambda cls: cls.close / cls.up_pressure_120),
        #ratio_close_lower_120: float #当日收盘价与120日下压力位的比
        "ratio_close_lower_20": (lambda cls: cls.close / cls.down_pressure_120),

        ## 当日价格与240日压力位比值（浮点型）
        #ratio_close_upper_240: float #当日收盘价与240日上压力位的比
        "ratio_close_upper_20": (lambda cls: cls.close / cls.up_pressure_240),
        #ratio_close_lower_240: float #当日收盘价与240日下压力位的比
        "ratio_close_lower_20": (lambda cls: cls.close / cls.down_pressure_240),


        ## 2日平均价格与20日压力位比值（浮点型）
        #ratio_close_upper_2_20: float #2日平均收盘价与20日上压力位的比
        "ratio_close_upper_2_20": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=2, BreakWindowCount=20),
        #ratio_close_lower_2_20: float #2日平均收盘价与20日下压力位的比
        "ratio_close_lower_2_20": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=2, BreakWindowCount=20),

        ## 2日平均价格与40日压力位比值（浮点型）
        #ratio_close_upper_2_40: float #2日平均收盘价与40日上压力位的比
        "ratio_close_upper_2_40": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=2, BreakWindowCount=40),
        #ratio_close_lower_2_40: float #2日平均收盘价与40日下压力位的比
        "ratio_close_lower_2_40": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=2, BreakWindowCount=40),

        ## 2日平均价格与60日压力位比值（浮点型）
        #ratio_close_upper_2_60: float #2日平均收盘价与60日上压力位的比
        "ratio_close_upper_2_60": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=2, BreakWindowCount=60),
        #ratio_close_lower_2_60: float #2日平均收盘价与60日下压力位的比
        "ratio_close_lower_2_60": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=2, BreakWindowCount=60),

        ## 2日平均价格与120日压力位比值（浮点型）
        #ratio_close_upper_2_120: float #2日平均收盘价与120日上压力位的比
        "ratio_close_upper_2_120": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=2, BreakWindowCount=120),
        #ratio_close_lower_2_120: float #2日平均收盘价与120日下压力位的比
        "ratio_close_lower_2_120": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=2, BreakWindowCount=120),

        ## 2日平均价格与240日压力位比值（浮点型）
        #ratio_close_upper_2_240: float #2日平均收盘价与240日上压力位的比
        "ratio_close_upper_2_240": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=2, BreakWindowCount=240),
        #ratio_close_lower_2_240: float #2日平均收盘价与240日下压力位的比
        "ratio_close_lower_2_240": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=2, BreakWindowCount=240),

        ## 3日平均价格与20日压力位比值（浮点型）
        #ratio_close_upper_3_20: float #3日平均收盘价与20日上压力位的比
        "ratio_close_upper_3_20": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=3, BreakWindowCount=20),
        #ratio_close_lower_3_20: float #3日平均收盘价与20日下压力位的比
        "ratio_close_lower_3_20": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=3, BreakWindowCount=20),

        ## 3日平均价格与40日压力位比值（浮点型）
        #ratio_close_upper_3_40: float #3日平均收盘价与40日上压力位的比
        "ratio_close_upper_3_40": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=3, BreakWindowCount=40),
        #ratio_close_lower_3_40: float #3日平均收盘价与40日下压力位的比
        "ratio_close_lower_3_40": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=3, BreakWindowCount=40),

        ## 3日平均价格与60日压力位比值（浮点型）
        #ratio_close_upper_3_60: float #3日平均收盘价与60日上压力位的比
        "ratio_close_upper_3_60": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=3, BreakWindowCount=60),
        #ratio_close_lower_3_60: float #3日平均收盘价与60日下压力位的比
        "ratio_close_lower_3_60": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=3, BreakWindowCount=60),

        ## 3日平均价格与120日压力位比值（浮点型）
        #ratio_close_upper_3_120: float #3日平均收盘价与120日上压力位的比
        "ratio_close_upper_3_120": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=3, BreakWindowCount=120),
        #ratio_close_lower_3_120: float #3日平均收盘价与120日下压力位的比
        "ratio_close_lower_3_120": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=3, BreakWindowCount=120),

        ## 3日平均价格与240日压力位比值（浮点型）
        #ratio_close_upper_3_240: float #3日平均收盘价与240日上压力位的比
        "ratio_close_upper_3_240": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=3, BreakWindowCount=240),
        #ratio_close_lower_3_240: float #3日平均收盘价与240日下压力位的比
        "ratio_close_lower_3_240": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=3, BreakWindowCount=240),

        ## 5日平均价格与20日压力位比值（浮点型）
        #ratio_close_upper_5_20: float #5日平均收盘价与20日上压力位的比
        "ratio_close_upper_5_20": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=5, BreakWindowCount=20),
        #ratio_close_lower_5_20: float #5日平均收盘价与20日下压力位的比
        "ratio_close_lower_5_20": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=5, BreakWindowCount=20),

        ## 5日平均价格与40日压力位比值（浮点型）
        #ratio_close_upper_5_40: float #5日平均收盘价与40日上压力位的比
        "ratio_close_upper_5_40": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=5, BreakWindowCount=40),
        #ratio_close_lower_5_40: float #5日平均收盘价与40日下压力位的比
        "ratio_close_lower_5_40": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=5, BreakWindowCount=40),

        ## 5日平均价格与60日压力位比值（浮点型）
        #ratio_close_upper_5_60: float #5日平均收盘价与60日上压力位的比
        "ratio_close_upper_5_60": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=5, BreakWindowCount=60),
        #ratio_close_lower_5_60: float #5日平均收盘价与60日下压力位的比
        "ratio_close_lower_5_60": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=5, BreakWindowCount=60),

        ## 5日平均价格与120日压力位比值（浮点型）
        #ratio_close_upper_5_120: float #5日平均收盘价与120日上压力位的比
        "ratio_close_upper_5_120": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=5, BreakWindowCount=120),
        #ratio_close_lower_5_120: float #5日平均收盘价与120日下压力位的比
        "ratio_close_lower_5_120": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=5, BreakWindowCount=120),

        ## 5日平均价格与240日压力位比值（浮点型）
        #ratio_close_upper_5_240: float #5日平均收盘价与240日上压力位的比
        "ratio_close_upper_5_240": partial(CalculationUtil.GetRatioDayAvg_Up_PressureWindow, Length=5, BreakWindowCount=240),
        #ratio_close_lower_5_240: float #5日平均收盘价与240日下压力位的比
        "ratio_close_lower_5_240": partial(CalculationUtil.GetRatioDayAvg_Down_PressureWindow, Length=5, BreakWindowCount=240),

        # -------------------------- 振幅相关 --------------------------
        "amplitude_3": partial(CalculationUtil.GetAmplitude_Avg, num =3),
        "amplitude_5": partial(CalculationUtil.GetAmplitude_Avg, num =5),
        "amplitude_10": partial(CalculationUtil.GetAmplitude_Avg, num =10),

        # -------------------------- 涨跌幅相关 --------------------------
        "change_Ratio_3": partial(CalculationUtil.GetChange_Ratio, num =3),
        "change_Ratio_5": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 5),
        "change_Ratio_10": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 10),
        "change_Ratio_20": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 20),
        "change_Ratio_40": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 40),
        "change_Ratio_60": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 60),
        "change_Ratio_120": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 120),
        "change_Ratio_240": partial(CalculationUtil.GetChange_Ratio_Total_Window, StartDayCount = 0, ToDayCount = 240),


        "change_Ratio_single_3": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 3),
        "change_Ratio_single_5": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 5),
        "change_Ratio_single_10": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 10),
        "change_Ratio_single_20": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 20),
        "change_Ratio_single_40": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 40),
        "change_Ratio_single_60": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 60),
        "change_Ratio_single_120": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 120),
        "change_Ratio_single_240": partial(CalculationUtil.GetChange_Ratio_Window, StartDayCount = 0, ToDayCount = 240),

        # -------------------------- 成交量相关 --------------------------
        "volume_ratio": partial(CalculationUtil.GetVolume_Ratio),
        "volume_ratio_3": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=3),
        "volume_ratio_5_percent": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=5),
        "volume_ratio_10": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=10),
        "volume_ratio_20": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=20),
        "volume_ratio_40": partial(CalculationUtil.GetVolume_Ratio_Window, StartDayCount=0, ToDayCount=40),


        

        # -------------------------- 量价相关 --------------------------
        "volume_price_ratio": partial(CalculationUtil.GetVolume_Price, num=1),
        "volume_price_ratio_3": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=3),
        "volume_price_ratio_5": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=5),
        "volume_price_ratio_10": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=10),
        "volume_price_ratio_20": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=20),
        "volume_price_ratio_40": partial(CalculationUtil.GetVolume_Price_Ratio_Window, StartDayCount=0, ToDayCount=40),
        "volume_ratio_5": partial(CalculationUtil.GetVolume_5),

        
        # -------------------------- 均价/换手率相关 --------------------------
        "avg_ratio": partial(CalculationUtil.GetAvg_Ratio),
        "turn_ratio": partial(CalculationUtil.GetTurn_Ratio),

        # -------------------------- 资金成交动量 --------------------------
        "volume_price_energy": partial(CalculationUtil.GetVolume_Energy, num=1),
        "volume_price_energy_5": partial(CalculationUtil.GetVolume_Energy, num=5),
        "volume_price_energy_10": partial(CalculationUtil.GetVolume_Energy, num=10),
        "volume_price_energy_20": partial(CalculationUtil.GetVolume_Energy, num=20),
        "volume_price_energy_60": partial(CalculationUtil.GetVolume_Energy, num=60),
        "volume_price_energy_120": partial(CalculationUtil.GetVolume_Energy, num=120),
        "volume_price_energy_240": partial(CalculationUtil.GetVolume_Energy, num=240),

        # -------------------------- 均价相关 --------------------------
        "avg_5": partial(CalculationUtil.GetAvg, num=5),
        "avg_10": partial(CalculationUtil.GetAvg, num=10),
        "avg_20": partial(CalculationUtil.GetAvg, num=20),
        "avg_40": partial(CalculationUtil.GetAvg, num=40),
        "avg_60": partial(CalculationUtil.GetAvg, num=60),
        "avg_120": partial(CalculationUtil.GetAvg, num=120),
        "avg_240": partial(CalculationUtil.GetAvg, num=240),

        # -------------------------- 均价比率 --------------------------
        "avg_ratio_5": (lambda cls: cls.avg / cls.avg_5),
        "avg_ratio_10": (lambda cls: cls.avg / cls.avg_10),
        "avg_ratio_20": (lambda cls: cls.avg / cls.avg_20),
        "avg_ratio_40": (lambda cls: cls.avg / cls.avg_40),
        "avg_ratio_60": (lambda cls: cls.avg / cls.avg_60),
        "avg_ratio_120": (lambda cls: cls.avg / cls.avg_120),
        "avg_ratio_240": (lambda cls: cls.avg / cls.avg_240),

        # -------------------------- 行业排名相关 --------------------------
        "total_value_ratio": partial(CalculationUtil.GetIndustry_Rank_Value, handler = calculationHandler),
        "earn_ratio": partial(CalculationUtil.GetIndustry_Rank_Earn, handler = calculationHandler),
        "clean_ratio": partial(CalculationUtil.GetIndustry_Rank_Clean, handler = calculationHandler),
        "cash_ratio": partial(CalculationUtil.GetIndustry_Rank_Cash, handler = calculationHandler),
        "sale_ratio": partial(CalculationUtil.GetIndustry_Rank_Sale, handler = calculationHandler),
        "volume_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume, handler = calculationHandler),
        "total_price_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume_Price, handler = calculationHandler),
        "total_price_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Price_Ratio, handler = calculationHandler),
        "volume_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Volume_Ratio, handler = calculationHandler),
        "ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Ratio, handler = calculationHandler),
        "amplitude_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Amplitude, handler = calculationHandler),
        "turn_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Turn, handler = calculationHandler),
        "turn_ratio_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Turn_Ratio, handler = calculationHandler),
        "avg_industry_rank": partial(CalculationUtil.GetIndustry_Rank_Avg_Ratio, handler = calculationHandler),



        # -------------------------- 基础状态 - 成交量 --------------------------
        "volumeState_1": partial(CalculationUtil.GetVolumeState, num=1),
        "volumeState_3": partial(CalculationUtil.GetVolumeState, num=3),
        "volumeState_5": partial(CalculationUtil.GetVolumeState, num=5),
        "volumeState_10": partial(CalculationUtil.GetVolumeState, num=10),
        "volumeState_20": partial(CalculationUtil.GetVolumeState, num=20),  # 新增20日
        "volumeState_40": partial(CalculationUtil.GetVolumeState, num=40),  # 新增40日
        "volumeState_60": partial(CalculationUtil.GetVolumeState, num=60),  # 新增60日
        "volumeState_120": partial(CalculationUtil.GetVolumeState, num=120),  # 新增120日
        "volumeState_240": partial(CalculationUtil.GetVolumeState, num=240),  # 新增120日
        
        # -------------------------- 基础状态 - 价格 --------------------------
        "priceState_1": partial(CalculationUtil.GetRatioState, num=1),
        "priceState_3": partial(CalculationUtil.GetRatioState, num=3),
        "priceState_5": partial(CalculationUtil.GetRatioState, num=5),
        "priceState_10": partial(CalculationUtil.GetRatioState, num=10),
        "priceState_20": partial(CalculationUtil.GetRatioState, num=20),  # 新增20日
        "priceState_40": partial(CalculationUtil.GetRatioState, num=40),  # 新增40日
        "priceState_60": partial(CalculationUtil.GetRatioState, num=60),  # 新增60日
        "priceState_120": partial(CalculationUtil.GetRatioState, num=120),  # 新增120日
        "priceState_240": partial(CalculationUtil.GetRatioState, num=240),  # 新增120日
        
        # -------------------------- 基础状态 - 振幅 --------------------------
        "amplitudeState_1": partial(CalculationUtil.GetAmplitudeState, num=1),
        "amplitudeState_3": partial(CalculationUtil.GetAmplitudeState, num=3),
        "amplitudeState_5": partial(CalculationUtil.GetAmplitudeState, num=5),
        "amplitudeState_10": partial(CalculationUtil.GetAmplitudeState, num=10),
        "amplitudeState_20": partial(CalculationUtil.GetAmplitudeState, num=20),  # 新增20日
        "amplitudeState_40": partial(CalculationUtil.GetAmplitudeState, num=40),  # 新增40日
        "amplitudeState_60": partial(CalculationUtil.GetAmplitudeState, num=60),  # 新增60日
        "amplitudeState_120": partial(CalculationUtil.GetAmplitudeState, num=120),  # 新增120日
        "amplitudeState_240": partial(CalculationUtil.GetAmplitudeState, num=240),  # 新增120日
        
        # -------------------------- 状态相关 - 1日 --------------------------
        "is_up_up": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == 1 else 0),
        "is_low_up": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == 1 else 0),
        "is_up_low": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == -1 else 0),
        "is_low_low": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == -1 else 0),
        "is_up_mid": (lambda cls: 1 if cls.volumeState_1 == 1 and cls.priceState_1 == 0 else 0),
        "is_low_mid": (lambda cls: 1 if cls.volumeState_1 == -1 and cls.priceState_1 == 0 else 0),
        "is_mid_up": (lambda cls: 1 if cls.volumeState_1 == 0 and cls.priceState_1 == 1 else 0),
        "is_mid_low": (lambda cls: 1 if cls.volumeState_1 == 0 and cls.priceState_1 == -1 else 0),

        # -------------------------- 状态相关 - 3日 --------------------------
        "is_up_up_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == 1 else 0),
        "is_low_up_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == 1 else 0),
        "is_up_low_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == -1 else 0),
        "is_low_low_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == -1 else 0),
        "is_up_mid_3": (lambda cls: 1 if cls.volumeState_3 == 1 and cls.priceState_3 == 0 else 0),
        "is_low_mid_3": (lambda cls: 1 if cls.volumeState_3 == -1 and cls.priceState_3 == 0 else 0),
        "is_mid_up_3": (lambda cls: 1 if cls.volumeState_3 == 0 and cls.priceState_3 == 1 else 0),
        "is_mid_low_3": (lambda cls: 1 if cls.volumeState_3 == 0 and cls.priceState_3 == -1 else 0),

        # -------------------------- 状态相关 - 5日 --------------------------
        "is_up_up_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == 1 else 0),
        "is_low_up_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == 1 else 0),
        "is_up_low_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == -1 else 0),
        "is_low_low_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == -1 else 0),
        "is_up_mid_5": (lambda cls: 1 if cls.volumeState_5 == 1 and cls.priceState_5 == 0 else 0),
        "is_low_mid_5": (lambda cls: 1 if cls.volumeState_5 == -1 and cls.priceState_5 == 0 else 0),
        "is_mid_up_5": (lambda cls: 1 if cls.volumeState_5 == 0 and cls.priceState_5 == 1 else 0),
        "is_mid_low_5": (lambda cls: 1 if cls.volumeState_5 == 0 and cls.priceState_5 == -1 else 0),

        # -------------------------- 状态相关 - 10日 --------------------------
        "is_up_up_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == 1 else 0),
        "is_low_up_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == 1 else 0),
        "is_up_low_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == -1 else 0),
        "is_low_low_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == -1 else 0),
        "is_up_mid_10": (lambda cls: 1 if cls.volumeState_10 == 1 and cls.priceState_10 == 0 else 0),
        "is_low_mid_10": (lambda cls: 1 if cls.volumeState_10 == -1 and cls.priceState_10 == 0 else 0),
        "is_mid_up_10": (lambda cls: 1 if cls.volumeState_10 == 0 and cls.priceState_10 == 1 else 0),
        "is_mid_low_10": (lambda cls: 1 if cls.volumeState_10 == 0 and cls.priceState_10 == -1 else 0),

        # -------------------------- 状态相关 - 20日 --------------------------  # 新增20日
        "is_up_up_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == 1 else 0),
        "is_low_up_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == 1 else 0),
        "is_up_low_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == -1 else 0),
        "is_low_low_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == -1 else 0),
        "is_up_mid_20": (lambda cls: 1 if cls.volumeState_20 == 1 and cls.priceState_20 == 0 else 0),
        "is_low_mid_20": (lambda cls: 1 if cls.volumeState_20 == -1 and cls.priceState_20 == 0 else 0),
        "is_mid_up_20": (lambda cls: 1 if cls.volumeState_20 == 0 and cls.priceState_20 == 1 else 0),
        "is_mid_low_20": (lambda cls: 1 if cls.volumeState_20 == 0 and cls.priceState_20 == -1 else 0),

        # -------------------------- 状态相关 - 40日 --------------------------  # 新增40日
        "is_up_up_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == 1 else 0),
        "is_low_up_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == 1 else 0),
        "is_up_low_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == -1 else 0),
        "is_low_low_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == -1 else 0),
        "is_up_mid_40": (lambda cls: 1 if cls.volumeState_40 == 1 and cls.priceState_40 == 0 else 0),
        "is_low_mid_40": (lambda cls: 1 if cls.volumeState_40 == -1 and cls.priceState_40 == 0 else 0),
        "is_mid_up_40": (lambda cls: 1 if cls.volumeState_40 == 0 and cls.priceState_40 == 1 else 0),
        "is_mid_low_40": (lambda cls: 1 if cls.volumeState_40 == 0 and cls.priceState_40 == -1 else 0),

        # -------------------------- 状态相关 - 60日 --------------------------  # 新增60日
        "is_up_up_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == 1 else 0),
        "is_low_up_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == 1 else 0),
        "is_up_low_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == -1 else 0),
        "is_low_low_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == -1 else 0),
        "is_up_mid_60": (lambda cls: 1 if cls.volumeState_60 == 1 and cls.priceState_60 == 0 else 0),
        "is_low_mid_60": (lambda cls: 1 if cls.volumeState_60 == -1 and cls.priceState_60 == 0 else 0),
        "is_mid_up_60": (lambda cls: 1 if cls.volumeState_60 == 0 and cls.priceState_60 == 1 else 0),
        "is_mid_low_60": (lambda cls: 1 if cls.volumeState_60 == 0 and cls.priceState_60 == -1 else 0),

        # -------------------------- 状态相关 - 120日 --------------------------  # 新增120日
        "is_up_up_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == 1 else 0),
        "is_low_up_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == 1 else 0),
        "is_up_low_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == -1 else 0),
        "is_low_low_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == -1 else 0),
        "is_up_mid_120": (lambda cls: 1 if cls.volumeState_120 == 1 and cls.priceState_120 == 0 else 0),
        "is_low_mid_120": (lambda cls: 1 if cls.volumeState_120 == -1 and cls.priceState_120 == 0 else 0),
        "is_mid_up_120": (lambda cls: 1 if cls.volumeState_120 == 0 and cls.priceState_120 == 1 else 0),
        "is_mid_low_120": (lambda cls: 1 if cls.volumeState_120 == 0 and cls.priceState_120 == -1 else 0),

        # -------------------------- 状态相关 - 240日 --------------------------  # 新增240日
        "is_up_up_240": (lambda cls: 1 if cls.volumeState_240 == 1 and cls.priceState_240 == 1 else 0),
        "is_low_up_240": (lambda cls: 1 if cls.volumeState_240 == -1 and cls.priceState_240 == 1 else 0),
        "is_up_low_240": (lambda cls: 1 if cls.volumeState_240 == 1 and cls.priceState_240 == -1 else 0),
        "is_low_low_240": (lambda cls: 1 if cls.volumeState_240 == -1 and cls.priceState_240 == -1 else 0),
        "is_up_mid_240": (lambda cls: 1 if cls.volumeState_240 == 1 and cls.priceState_240 == 0 else 0),
        "is_low_mid_240": (lambda cls: 1 if cls.volumeState_240 == -1 and cls.priceState_240 == 0 else 0),
        "is_mid_up_240": (lambda cls: 1 if cls.volumeState_240 == 0 and cls.priceState_240 == 1 else 0),
        "is_mid_low_240": (lambda cls: 1 if cls.volumeState_240 == 0 and cls.priceState_240 == -1 else 0),


        # -------------------------- 振幅+价格状态 --------------------------
        "is_pop_up": (lambda cls: 1 if cls.amplitudeState_1 == 1 and cls.priceState_1 == 1 else 0),
        "is_pop_down": (lambda cls: 1 if cls.amplitudeState_1 == 1 and cls.priceState_1 == -1 else 0),
        "is_pop_up_3": (lambda cls: 1 if cls.amplitudeState_3 == 1 and cls.priceState_3 == 1 else 0),
        "is_pop_down_3": (lambda cls: 1 if cls.amplitudeState_3 == 1 and cls.priceState_3 == -1 else 0),
        "is_pop_up_5": (lambda cls: 1 if cls.amplitudeState_5 == 1 and cls.priceState_5 == 1 else 0),
        "is_pop_down_5": (lambda cls: 1 if cls.amplitudeState_5 == 1 and cls.priceState_5 == -1 else 0),
        "is_pop_up_10": (lambda cls: 1 if cls.amplitudeState_10 == 1 and cls.priceState_10 == 1 else 0),
        "is_pop_down_10": (lambda cls: 1 if cls.amplitudeState_10 == 1 and cls.priceState_10 == -1 else 0),
        "is_pop_up_20": (lambda cls: 1 if cls.amplitudeState_20 == 1 and cls.priceState_20 == 1 else 0),  # 新增20日
        "is_pop_down_20": (lambda cls: 1 if cls.amplitudeState_20 == 1 and cls.priceState_20 == -1 else 0),  # 新增20日
        "is_pop_up_40": (lambda cls: 1 if cls.amplitudeState_40 == 1 and cls.priceState_40 == 1 else 0),  # 新增40日
        "is_pop_down_40": (lambda cls: 1 if cls.amplitudeState_40 == 1 and cls.priceState_40 == -1 else 0),  # 新增40日
        "is_pop_up_60": (lambda cls: 1 if cls.amplitudeState_60 == 1 and cls.priceState_60 == 1 else 0),  # 新增60日
        "is_pop_down_60": (lambda cls: 1 if cls.amplitudeState_60 == 1 and cls.priceState_60 == -1 else 0),  # 新增60日
        "is_pop_up_120": (lambda cls: 1 if cls.amplitudeState_120 == 1 and cls.priceState_120 == 1 else 0),  # 新增120日
        "is_pop_down_120": (lambda cls: 1 if cls.amplitudeState_120 == 1 and cls.priceState_120 == -1 else 0),  # 新增120日
        "is_pop_up_240": (lambda cls: 1 if cls.amplitudeState_240 == 1 and cls.priceState_240 == 1 else 0),  # 新增240日
        "is_pop_down_240": (lambda cls: 1 if cls.amplitudeState_240 == 1 and cls.priceState_240 == -1 else 0),  # 新增240日

    }


    calculationHandler.CalculateIndustryBaseClassAttrDic = {
            
        # 成交量相关（核心修正：self → handler）
        "volume": (
            CalculationUtil.GetIndustry_Volume,
            ["industryInfoCls", "trade_date", "handler"]  # 原self改为handler
        ),
        "volume_ratio": (
            CalculationUtil.GetIndustry_Volume_Ratio,
            ["industryInfoCls", "trade_date", 1, "handler"]  # 原self改为handler
        ),
        "volume_ratio_3": (
            CalculationUtil.GetIndustry_Volume_Ratio,
            ["industryInfoCls", "trade_date", 3, "handler"]
        ),
        "volume_ratio_5": (
            CalculationUtil.GetIndustry_Volume_Ratio,
            ["industryInfoCls", "trade_date", 5, "handler"]
        ),
        "volume_ratio_10": (
            CalculationUtil.GetIndustry_Volume_Ratio,
            ["industryInfoCls", "trade_date", 10, "handler"]
        ),
        "volume_ratio_20": (
            CalculationUtil.GetIndustry_Volume_Ratio,
            ["industryInfoCls", "trade_date", 20, "handler"]
        ),
        
        # 成交额相关（核心修正：self → handler）
        "volume_price": (
            CalculationUtil.GetIndustry_Volume_Price,
            ["industryInfoCls", "trade_date", "handler"]
        ),
        "volume_price_ratio": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio,
            ["industryInfoCls", "trade_date", 1, "handler"]
        ),
        "volume_price_ratio_3": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio,
            ["industryInfoCls", "trade_date", 3, "handler"]
        ),
        "volume_price_ratio_5": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio,
            ["industryInfoCls", "trade_date", 5, "handler"]
        ),
        "volume_price_ratio_10": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio,
            ["industryInfoCls", "trade_date", 10, "handler"]
        ),
        "volume_price_ratio_20": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio,
            ["industryInfoCls", "trade_date", 20, "handler"]
        ),
        
        # 涨跌幅相关（核心修正：self → handler）
        "change_Ratio": (
            CalculationUtil.GetIndustry_Change_Ratio,
            ["industryInfoCls", "trade_date", "handler"]
        ),
        
        # 股票数量相关（无需传handler，保持不变）
        "stockNum": (lambda industryInfoCls: len(industryInfoCls.stockList), ["industryInfoCls"]),
        "stockNum_up": (
            CalculationUtil.GetIndustry_Up_Count,
            ["industryInfoCls", "trade_date", "handler"]  # 同步修正为handler
        ),
        "stockNum_up_Ratio": (
            lambda stockNum_up, stockNum: (stockNum_up / stockNum) * 100 if stockNum > 0 else 0,
            ["stockNum_up", "stockNum"]
        ),
        "stockNum_down": (
            CalculationUtil.GetIndustry_Down_Count,
            ["industryInfoCls", "trade_date", "handler"]  # 同步修正为handler
        ),
        "stockNum_down_Ratio": (
            lambda stockNum_down, stockNum: (stockNum_down / stockNum) * 100 if stockNum > 0 else 0,
            ["stockNum_down", "stockNum"]
        ),
    }


    calculationHandler.CalculateIndustryWindowClassAttrDic = {

        # 成交量相关
        "volume": (
            CalculationUtil.GetIndustry_Volume_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]  # 修正：self → handler
        ),
        "volume_price": (
            CalculationUtil.GetIndustry_Volume_Price_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "avg_volume": (
            CalculationUtil.GetIndustry_Volume_Avg_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "avg_volume_price": (
            CalculationUtil.GetIndustry_Volume_Price_Avg_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "volume_ratio": (
            CalculationUtil.GetIndustry_Volume_Ratio_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "volume_price_ratio": (
            CalculationUtil.GetIndustry_Volume_Price_Ratio_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        
        # 涨跌幅相关
        "change_Ratio": (
            CalculationUtil.GetIndustry_Change_Ratio_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "change_Ratio_Total": (
            CalculationUtil.GetIndustry_Change_Ratio_Total_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        
        # 股票数量相关
        "avg_stockNum_up": (
            CalculationUtil.GetIndustry_Up_Stock_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "avg_stockNum_down": (
            CalculationUtil.GetIndustry_Down_Stock_Window,
            ["industryInfoCls", "trade_date", "startDateCount", "toDateCount", "handler"]
        ),
        "stockNum_up_Ratio": (
            # 1:1复刻你的原始代码逻辑
            lambda cls: (cls.avg_stockNum_up / cls.stockNum) * 100 if cls.stockNum > 0 else 0,
            ["self"]  # 仅需传self一个参数
        ),
        "stockNum_down_Ratio": (
            # 1:1复刻你的原始代码逻辑
            lambda cls: (cls.avg_stockNum_down / cls.stockNum) * 100 if cls.stockNum > 0 else 0,
            ["self"]  # 仅需传self一个参数
        ),
    }