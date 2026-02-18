from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core.Select import CalculationDataHandle
from operator import attrgetter
from datetime import date,datetime, timedelta
from datetime import date

#计算行业内公司基本面数据（市值，盈，净，销，现）排名百分比
def CalculateIndustryBase(industryCls: CalculationDataStruct.StructIndustryInfoClass,
                          handler: CalculationDataHandle.BaseClass):

    # 如果已经计算过，直接退出
    if industryCls.isCalculate:
        return

    today_str = date.today().strftime("%Y%m%d")

    stock_count = len(industryCls.stockList)
    current_index = 0

    # 遍历行业内所有股票
    for stock_key, stock_val in industryCls.stockList.items():

        current_index += 1

        code = stock_val.Code

        # 获取公司信息实例（只获取一次）
        company_info = handler.totalComponyIns.GetComponyInfo(code)

        # 如果五个字段已经全部存在，直接跳过该股票
        if (
            company_info.Total_Value != 0 and
            company_info.Earn != 0 and
            company_info.Clean != 0 and
            company_info.Sale != 0 and
            company_info.Cash != 0
        ):
            continue

        # 获取最近240个交易日（只获取一次）
        listDay = handler.GetLastTradeDateList(code, today_str, 10)

        if not listDay:
            print(f"!!!!!!!!!遇到了没法计算的：{code}")
            continue

        # 记录还缺哪些字段（减少重复判断）
        need_total   = company_info.Total_Value == 0
        need_earn    = company_info.Earn == 0
        need_clean   = company_info.Clean == 0
        need_sale    = company_info.Sale == 0
        need_cash    = company_info.Cash == 0

        # 如果已经全部满足，直接跳过
        if not (need_total or need_earn or need_clean or need_sale or need_cash):
            continue
        dayCount = 0
        
        # 遍历历史交易日，直到找到有效数据
        for dayStr in listDay:
            base_data = handler.GetBaseDataClass(code, dayStr, False)
            dayCount = dayCount + 1
            # 如果全部填满了，提前终止
            if (
                company_info.Total_Value != 0 and
                company_info.Earn != 0 and
                company_info.Clean != 0 and
                company_info.Sale != 0 and
                company_info.Cash != 0
            ):
                break

            # 分别填充缺失字段（只填一次）
            if need_total and base_data.total_value != 0:
                company_info.Total_Value = base_data.total_value
                need_total = False

            if need_earn and base_data.earn != 0:
                company_info.Earn = base_data.earn
                need_earn = False

            if need_clean and base_data.clean != 0:
                company_info.Clean = base_data.clean
                need_clean = False

            if need_sale and base_data.sale != 0:
                company_info.Sale = base_data.sale
                need_sale = False

            if need_cash and base_data.cash != 0:
                company_info.Cash = base_data.cash
                need_cash = False

            # 如果已经全部填满，提前退出
            if not (need_total or need_earn or need_clean or need_sale or need_cash):
                break
        #print(f"正在计算公司基本净，盈，销，现：{current_index}/{stock_count}, 循环次数：{dayCount}")
    #print("公司基本净，盈，销，现计算完毕")


#涨跌幅计算
def GetChange_Ratio(NowData:CalculationDataStruct.StructBaseClass, num):
    count = 0
    target_Price = 0
    for val in NowData.dataList_240:
        target_Price = val.close
        count = count + 1
        if count >= num:
            break
    return ((NowData.close - target_Price) / target_Price) * 100

#成交量涨跌幅计算
def GetVolume_Ratio(NowData:CalculationDataStruct.StructBaseClass, num):
    count = 1
    avg1 = NowData.volume
    avg2 = 0
    for val in NowData.dataList_240:
        if count < num:
            avg1 = avg1 + val.volume
        elif count >=num and count < num * 2:
            avg2 = avg2 + val.volume
        else:
            break
        count = count + 1

    avg1 = avg1 / num
    avg2 = avg2 / num

    target =  (avg1 - avg2) / avg2
    #if num != 1:
        #print(f"计算出的结果是 {target *100}， 均价1：{avg1 / 10000}，  均价2： {avg2 / 10000}，  数量：{num}")
    return target *100

#平均振幅计算
def GetAmplitude_Avg(NowData:CalculationDataStruct.StructBaseClass, num):
    count = 1
    avg1 = NowData.amplitude
    avg2 = 0
    for val in NowData.dataList_240:
        if count < num:
            avg1 = avg1 + val.amplitude
        elif count >=num and count < num * 2:
            avg2 = avg2 + val.amplitude
        else:
            break
        count = count + 1

    avg1 = avg1 / num
    avg2 = avg2 / num

    #target =  (avg1 - avg2) / avg2
    #if num != 1:
        #print(f"计算出的结果是 {target *100}， 均价1：{avg1 / 10000}，  均价2： {avg2 / 10000}，  数量：{num}")
    return avg1




#成交额涨跌幅计算
def GetVolume_Price(NowData:CalculationDataStruct.StructBaseClass, num):
    count = 0
    avg = 0
    for val in NowData.dataList_240:
        avg = avg + val.volume_price
        count = count + 1
        if count >= num:
            break
    avg = avg / num

    target = (NowData.volume_price - avg) / avg
    return target * 100



def GetAvg_Ratio(NowData:CalculationDataStruct.StructBaseClass):
    lastDay = NowData.dataList_240[0]
    target = (NowData.avg - lastDay.avg) / lastDay.avg
    return target *100


#量比计算
def GetVolume_5(NowData : CalculationDataStruct.StructBaseClass):
    total = 0
    count = 0
    for val in NowData.dataList_240:
        total = total + val.volume
        count = count + 1
        if(count >= 5):
            break
    total = total / 5
    target = NowData.volume / total
    return target


#换手率涨跌幅计算
def GetTurn_Ratio(NowData : CalculationDataStruct.StructBaseClass):
    lastDay = NowData.dataList_240[0]
    target = (NowData.turn - lastDay.turn) / lastDay.turn
    return target * 100


#成交动量计算
def GetVolume_Energy(NowData : CalculationDataStruct.StructBaseClass, dayNum):
    count = 0
    total_Value = 0
    for data in NowData.dataList_240:
        total_Value = total_Value + data.volume_price
        count = count + 1 
        if(count >= dayNum):
            break
    #print(f"平均成交额变换：{(NowData.volume_price / (total_Value / dayNum))}， 涨跌幅{NowData.change_Ratio}")
    target = (NowData.volume_price / (total_Value / dayNum)) * (NowData.change_Ratio / 100)
    return target


#获取在行业的市值排名
def GetIndustry_Rank_Value(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    value = NowData.total_value
    name = handler.totalComponyIns.GetComponyInfo(code).Name
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)
    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Total_Value, reverse=True)
    )
    count = 0
    for key, val in sorted_dict.items():
        count = count + 1
        if val.Code == code:
            return (count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，流通市值 {val.Total_Value / 100000000}, 排名是：{count} / {len(industryCls.stockList)}")
    return 100
    
#获取在行业的市盈率排名
def GetIndustry_Rank_Earn(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    value = NowData.total_value
    name = handler.totalComponyIns.GetComponyInfo(code).Name
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)

    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Earn, reverse=True)
    )
    count = 0
    for key, val in sorted_dict.items():
        count = count + 1
        if val.Code == code:
            return (count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return 100

#获取在行业的市净率排名
def GetIndustry_Rank_Clean(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    value = NowData.total_value
    name = handler.totalComponyIns.GetComponyInfo(code).Name
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)

    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Clean, reverse=True)
    )
    count = 0
    for key, val in sorted_dict.items():
        count = count + 1
        if val.Code == code:
            return (count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市净率 {val.Clean}, 排名是：{count} / {len(industryCls.stockList)}")

    return 100


#获取在行业的市销率排名
def GetIndustry_Rank_Sale(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    value = NowData.total_value
    name = handler.totalComponyIns.GetComponyInfo(code).Name
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)

    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Sale, reverse=True)
    )
    count = 0
    for key, val in sorted_dict.items():
        count = count + 1
        if val.Code == code:
            return (count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市销率 {val.Sale}, 排名是：{count} / {len(industryCls.stockList)}")

    return 100

#获取在行业的市现率排名
def GetIndustry_Rank_Cash(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    value = NowData.total_value
    name = handler.totalComponyIns.GetComponyInfo(code).Name
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)

    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Cash, reverse=True)
    )
    count = 0
    for key, val in sorted_dict.items():
        count = count + 1
        if val.Code == code:
            return (count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市现率 {val.Cash}, 排名是：{count} / {len(industryCls.stockList)}")
    return 100




#获取当日行业成交量排名(前%)
def GetIndustry_Rank_Volume(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100




    #获取当日行业成交额排名(前%)
def GetIndustry_Rank_Volume_Price(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_price, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交额（万） {val.volume_price / 10000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100



#获取当日行业成交额涨跌幅排名(前%)
def GetIndustry_Rank_Price_Ratio(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if not dailyCls.isCalculate :
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(dailyCls.code, dailyCls.trade_date, 20)
            dailyCls.dataList_240 = dataList_20
            dailyCls.volume_price_ratio = GetVolume_Price(dailyCls, 1)
            pass
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_price_ratio, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交额涨跌幅 {val.volume_price_ratio}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100


#获取当日行业成交量涨跌幅排名(前%)
def GetIndustry_Rank_Volume_Ratio(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if not dailyCls.isCalculate :
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(dailyCls.code, dailyCls.trade_date, 40)
            dailyCls.dataList_240 = dataList_20
            dailyCls.volume_ratio = GetVolume_Ratio(dailyCls, 1)
            pass
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_ratio, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量涨跌幅 {val.volume_ratio}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100



    
#获取当日涨跌幅排名(前%)
def GetIndustry_Rank_Ratio(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.change_Ratio, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 涨跌幅 ： {val.change_Ratio}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100






#获取当日振幅排名(前%)
def GetIndustry_Rank_Amplitude(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.amplitude, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 振幅 ： {val.amplitude}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100


#获取换手率排名(前%)
def GetIndustry_Rank_Turn(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.turn, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 换手率 ： {val.turn}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100


#获取当日换手率涨跌幅排名(前%)
def GetIndustry_Rank_Turn_Ratio(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if not dailyCls.isCalculate :
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(dailyCls.code, dailyCls.trade_date, 20)
            dailyCls.dataList_240 = dataList_20
            dailyCls.turn_ratio = GetTurn_Ratio(dailyCls)
            pass
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.turn_ratio, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 换手率涨跌幅 {val.turn_ratio}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100



#获取当日均价涨跌幅排名(前%)
def GetIndustry_Rank_Avg_Ratio(NowData : CalculationDataStruct.StructBaseClass,handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if not dailyCls.isCalculate :
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(dailyCls.code, dailyCls.trade_date, 20)
            dailyCls.dataList_240 = dataList_20
            dailyCls.avg_ratio = GetAvg_Ratio(dailyCls)
            pass
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.avg_ratio, reverse=True)
    count = 0
    for val in industryDailyList:
        count = count + 1
        name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 均价涨跌幅 {val.avg_ratio}, 排名是：{count} / {len(industryCls.stockList)}")
        if val.code == code:
            return (count / len(industryCls.stockList)) * 100
    return 100


##X日均价
def GetAvg(NowData : CalculationDataStruct.StructBaseClass, num):
    count = 1
    total = NowData.avg
    for data in NowData.dataList_240:
        total = total + data.avg
        if count >= (num - 1):
            break
        count = count + 1
    
    total = total / num
    return total



#获取成交量状态：1放量， -1缩量， 0平量
def GetVolumeState(NowData : CalculationDataStruct.StructBaseClass, num):
    target = 0
    if num == 1:
        target = NowData.volume_ratio
    if num == 3:
        target = NowData.volume_ratio_3
    elif num == 5:
        target = NowData.volume_ratio_5
    elif num == 10:
        target = NowData.volume_ratio_10
    print(f"成交量状态：{target}， {num}")
    if target > 0.2:
        return 1
    elif target < -0.2:
        return -1
    return 0

#获取涨跌状态：1涨， -1跌， 0横盘
def GetRatioState(NowData : CalculationDataStruct.StructBaseClass, num):
    target = 0
    if num  == 1:
        target = NowData.change_Ratio
    if num == 3:
        target = NowData.change_Ratio_3
    elif num == 5:
        target = NowData.change_Ratio_5
    elif num == 10:
        target = NowData.change_Ratio_10
    print(f"涨跌幅状态：{target}， {num}")

    if target > 2:
        return 1
    elif target < -2:
        return -1
    return 0

#获取震荡状态：1震荡， -1不震荡
def GetAmplitudeState(NowData : CalculationDataStruct.StructBaseClass, num):
    target = 0
    if num  == 1:
        target = NowData.amplitude
    if num == 3:
        target = NowData.amplitude_3
    elif num == 5:
        target = NowData.amplitude_5
    elif num == 10:
        target = NowData.amplitude_10
    #print(f"振幅状态：{target}， {num}")

    if target > 4:
        return 1
    else:
        return -1