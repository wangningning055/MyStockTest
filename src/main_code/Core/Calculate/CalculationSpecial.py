#这里的计算方法是主要因子，其他的都是配合的次要因子
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core.Calculate import CalculationDataHandle

#买点判断
    #  是否处在下压力位为主要因子（占比0.5）， 再配合下面的次要因子：
    #  超大周期震荡下跌，  
    #  最近中等周期震荡上行，
    #  股价近二十日没有超涨
    #  股价处在大周期低点
    #  处在最近小周期股价低点且放量上涨，
    #  近十日平均资金流通率好  
    #  股价接近区间均线（区间是40天，就是40日均线），
    #  波动降低（10日振幅 < 20日振幅）
    #  长周期换手振幅资金流通率极低，近十日换手振幅资金流通率，成交量暴涨
    #  股票基本面好

#计算下压力位， 用于买在低点判断
def CalculateDownPressure(nowData:CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    todayStr = nowData.trade_date
    stockCode = nowData.code
    windowData : CalculationDataStruct.StructBaseWindowClass = handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)
    #我给你提供了CalculationDataStruct文件，里面的实现类StructBaseWindowClass  StructBaseClass记录了你需要的各种字段，
    # 你需要帮我实现下面的下压力位计算过程，注释要清晰明确，你需要的各种字段都在nowData，和windowData中，可以去CalculationDataStruct文件里面查找

#压力位计算  当日数据为 nowData， 区间数据为windowData
    #提前说明：ATR的计算：
    # TR = max(
        #当日最高 - 当日最低,
        #abs(当日最高 - 昨日收盘),
        #abs(当日最低 - 昨日收盘)
    #)
    #ATR = TR 的 14 日平均

    #正式计算：
    #如果整个区间换手率低于1% 且平均涨跌幅低于2%，或平均振幅小于2 那支撑价就是区间的平均均价
    #否则进行下面的计算：
    #收盘价跌到十日均价 - ATR（14日）以下，且跌幅超过五日平均振幅，且累积跌幅超过 3% 且连续两天收跌：认为是开始回调
    #然后从开始回调开始，到收盘价在十日均价以上为止，找到这个日期区间的最低点，这一天就是股价低点
    #如此遍历区间，获得一个低点价位的列表，遍历列表，剔除低点当日振幅超过三倍的20日平均振幅的低点
    #寻找近5个支撑位，如果有三个支撑位几乎相同（差别在1%以内），支撑价直接就是这个价，否则按下面的算支撑位
    # 再遍历剩余列表计算这些低点价位的平均涨跌幅（涨跌幅限制在5个点以内，防止主升浪影响），按这个涨跌幅算出下一个支撑位低点的价格，
    #最后判断今天和昨天是否跌破支撑位或者处在支撑位

    pass


#计算上压力位，用于买在趋势突破的判断
def CalculateUpPressure():
    #  是否大幅超过上压力位， 再配合下面的因子：
    pass





#计算是否处在行业上涨周期，用于板块轮动买入判断


#计算是否是套娃周期的低点，用于长期震荡周期买入判断
#计算是否是套娃周期的高点，用于长期震荡周期卖出判断



#计算是否价值股，用于长线买入判断



#计算是否成长股，用于长线买入判断







#这两个后续考虑吧

#计算是否是M顶图形， 下行M为卖出判断，上行M为买入判断


#计算是否是W低图形， 上行W为买入判断，下行W为卖出判断