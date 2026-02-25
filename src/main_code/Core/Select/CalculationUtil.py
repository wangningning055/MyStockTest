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

    if count < num:
        num = count

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

    if count < num:
        num = count

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

    if count < num:
        num = count

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
    target_num = 5
    for val in NowData.dataList_240:
        total = total + val.volume
        count = count + 1
        if(count >= 5):
            break
    if count < 5:
        target_num = count

    total = total / target_num
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

    if count < num:
        num = count

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



#获取涨停次数
def GetUpStopCount(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    upStopCount = 0
    target = 0.1
    if NowData.code.startswith("300") or NowData.code.startswith("688"):
        #print("这个涨跌幅超过20")
        target = 0.2
    if StartDayCount <= 0:
        if abs(NowData.close - (NowData.last_close + NowData.last_close * target)) / NowData.close <= 0.003 :
            upStopCount = upStopCount + 1
            #print(f"当天，这天涨停")
            #print(f"这是第{count}天, 开盘价：{NowData.open}，  收盘价：{NowData.close}  涨停价：{NowData.last_close + NowData.last_close * target}，  插值：{abs(NowData.close - (NowData.open + NowData.open * target)) / NowData.open}")
        
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if abs(single.close - (single.last_close + single.last_close * target)) / single.close <= 0.003 :
                upStopCount = upStopCount + 1
                #print(f"前{count}天，这天涨停")
            #print(f"这是第{count}天, 开盘价：{single.open}，  收盘价：{single.close}  涨停价：{single.last_close + single.last_close * target}，  插值：{abs(single.close - (single.open + single.open * target)) / single.open}")
        count = count + 1
    return upStopCount

#获取跌停次数
def GetDownStopCount(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    upStopCount = 0
    target = 0.1
    if NowData.code.startswith("300") or NowData.code.startswith("688"):
        #print("这个涨跌幅超过20")
        target = 0.2
    if StartDayCount <= 0:
        if abs(NowData.close - (NowData.last_close - NowData.last_close * target)) / NowData.close <= 0.003 :
            upStopCount = upStopCount + 1
            #print(f"当天，这天涨停")
            #print(f"这是第{count}天, 开盘价：{NowData.open}，  收盘价：{NowData.close}  涨停价：{NowData.last_close + NowData.last_close * target}，  插值：{abs(NowData.close - (NowData.open + NowData.open * target)) / NowData.open}")
        
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if abs(single.close - (single.last_close - single.last_close * target)) / single.close <= 0.003 :
                upStopCount = upStopCount + 1
                #print(f"前{count}天，这天涨停")
            #print(f"这是第{count}天, 开盘价：{single.open}，  收盘价：{single.close}  涨停价：{single.last_close + single.last_close * target}，  插值：{abs(single.close - (single.open + single.open * target)) / single.open}")
        count = count + 1
    return upStopCount

#期间的整体成交量
def GetVolume_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    totalVolume = 0
    dataList_240 = NowData.dataList_240
    count = 1
    if StartDayCount <= 0:
        totalVolume = NowData.volume
        
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            totalVolume = totalVolume + single.volume
        count = count + 1
    return totalVolume


#期间的整体成交额
def GetVolume_Price_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    totalVolume = 0
    dataList_240 = NowData.dataList_240
    count = 1
    if StartDayCount <= 0:
        totalVolume = NowData.volume_price
        
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            totalVolume = totalVolume + single.volume_price
        count = count + 1
    return totalVolume


#期间的整体成交量涨跌幅
def GetVolume_Ratio_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    startVal = 0
    endVal = 0
    history = NowData.dataList_240

    # 把今天 + 历史拼成一个统一序列
    full_list = [NowData] + history

    count = 0
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (ToDayCount - StartDayCount) / 2:
                avg1 += single.volume
                avg1_count += 1
            if count > (ToDayCount - StartDayCount) / 2 and count <= ToDayCount:
                avg2 += single.volume
                avg2_count += 1
            if count > ToDayCount:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.volume
            if count == ToDayCount:
                endVal = single.volume
            count = count + 1
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0


#期间的整体成交额涨跌幅
def GetVolume_Price_Ratio_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    startVal = 0
    endVal = 0
    history = NowData.dataList_240

    # 把今天 + 历史拼成一个统一序列
    full_list = [NowData] + history

    count = 0
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (ToDayCount - StartDayCount) / 2:
                avg1 += single.volume_price
                avg1_count += 1
            if count > (ToDayCount - StartDayCount) / 2 and count <= ToDayCount:
                avg2 += single.volume_price
                avg2_count += 1
            if count > ToDayCount:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.volume_price
            if count == ToDayCount:
                endVal = single.volume_price
            count = count + 1
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0
    

#期间的整体换手率涨跌幅
def GetTurn_Ratio_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    startVal = 0
    endVal = 0
    history = NowData.dataList_240

    # 把今天 + 历史拼成一个统一序列
    full_list = [NowData] + history

    count = 0
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (ToDayCount - StartDayCount) / 2:
                avg1 += single.turn
                avg1_count += 1
            if count > (ToDayCount - StartDayCount) / 2 and count <= ToDayCount:
                avg2 += single.turn
                avg2_count += 1
            if count > ToDayCount:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.turn
            if count == ToDayCount:
                endVal = single.turn
            count = count + 1
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0


#期间的整体跌幅
def GetChange_Ratio_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    startVal = 0
    endVal = 0
    if StartDayCount <= 0:
        startVal = NowData.close
        
    for single in dataList_240:
        if count == StartDayCount and StartDayCount > 0:
            startVal = single.close
        if count == ToDayCount:
            endVal = single.close
        count = count + 1
    return (startVal - endVal)*100 / endVal


#期间的整体均价涨跌幅
def GetAvg_Ratio_Window(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 1
    startVal = 0
    endVal = 0
    if StartDayCount <= 0:
        startVal = NowData.avg
        
    for single in dataList_240:
        if count == StartDayCount and StartDayCount > 0:
            startVal = single.avg
        if count == ToDayCount:
            endVal = single.avg
        count = count + 1
    return (startVal - endVal)*100 / endVal



#期间的平均开盘价
def GetOpen_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    if StartDayCount <= 0:
        totalVal = NowData.open
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.open
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.open
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    #print(f"总共的天数是{num},加了：{num}    total = {totalVal}")
    return totalVal / (num)


#期间的平均收盘价
def GetClose_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    if StartDayCount <= 0:
        totalVal = NowData.close
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.close
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.close
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    #print(f"总共的天数是{num},加了：{num}    total = {totalVal}")
    return totalVal / (num)


#期间的平均最高价
def GetHigh_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.high
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.high
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.high
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)

#期间的平均最低价
def GetLow_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.low
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.low
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.low
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)


#期间的平均成交量
def GetVolume_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.volume
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.volume
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)


#期间的平均成交额
def GetVolume_Price_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_price
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.volume_price
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.volume_price
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)



#期间的平均量比
def Get_VolumeRatio_5_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_ratio_5
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(single.code, single.trade_date, 20)
                single.dataList_240 = dataList_20
                volume_Ratio_5 = GetVolume_5(single)
                
                totalVal = totalVal + volume_Ratio_5
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(single.code, single.trade_date, 20)
                single.dataList_240 = dataList_20
                volume_Ratio_5 = GetVolume_5(single)

                totalVal = totalVal + volume_Ratio_5
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)


def GetTurn_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.turn
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.turn
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.turn
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)


def GetChangeRatio_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.change_Ratio
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.change_Ratio
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.change_Ratio
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)

def GetAmplitude_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.amplitude
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.amplitude
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.amplitude
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)

def GetAvg_Price_Window_Avg(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.avg
        count = 1
        num = 1
    for single in dataList_240:
        if StartDayCount <= 0:
            if count >= 0 and count <= ToDayCount:
                totalVal = totalVal + single.avg
                num = num + 1
        else:
            if count >= StartDayCount and count <= ToDayCount:
                totalVal = totalVal + single.avg
                num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal / (num)





#最低开盘价
def GetOpen_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.open
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.open:
                totalVal = single.open
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低收盘价
def GetClose_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.close
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.close:
                totalVal = single.close
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低昨收价
def GetLastClose_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.last_close
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.last_close:
                totalVal = single.last_close
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低最高价
def GetHigh_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.high
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.high:
                totalVal = single.high
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低最低价
def GetLow_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.low
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.low:
                totalVal = single.low
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低成交量
def GetVolume_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.volume:
                totalVal = single.volume
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低成交额
def GetVolume_Price_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_price
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.volume_price:
                totalVal = single.volume_price
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低量比
def GetVolume_Ratio_5_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_ratio_5
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(single.code, single.trade_date, 20)
            single.dataList_240 = dataList_20
            volume_Ratio_5 = GetVolume_5(single)

            if totalVal > volume_Ratio_5:
                totalVal = volume_Ratio_5
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低换手率
def GetTurn_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.turn
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.turn:
                totalVal = single.turn
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低涨跌幅
def GetChange_Ratio_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.change_Ratio
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.change_Ratio:
                totalVal = single.change_Ratio
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低振幅
def GetAmplitude_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.amplitude
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.amplitude:
                totalVal = single.amplitude
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最低均价
def GetAvg_Window_Low(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.avg
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal > single.avg:
                totalVal = single.avg
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal





#最高开盘价
def GetOpen_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.open
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.open:
                totalVal = single.open
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高收盘价
def GetClose_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.close
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.close:
                totalVal = single.close
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高昨收价
def GetLastClose_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.last_close
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.last_close:
                totalVal = single.last_close
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高最高价
def GetHigh_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.high
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.high:
                totalVal = single.high
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高最低价
def GetLow_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.low
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.low:
                totalVal = single.low
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高成交量
def GetVolume_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.volume:
                totalVal = single.volume
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高成交额
def GetVolume_Price_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_price
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.volume_price:
                totalVal = single.volume_price
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高量比
def GetVolume_Ratio_5_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.volume_ratio_5
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            dataList_20:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(single.code, single.trade_date, 20)
            single.dataList_240 = dataList_20
            volume_Ratio_5 = GetVolume_5(single)

            if totalVal < volume_Ratio_5:
                totalVal = volume_Ratio_5
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高换手率
def GetTurn_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.turn
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.turn:
                totalVal = single.turn
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高涨跌幅
def GetChange_Ratio_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.change_Ratio
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.change_Ratio:
                totalVal = single.change_Ratio
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高振幅
def GetAmplitude_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.amplitude
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.amplitude:
                totalVal = single.amplitude
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal

#最高均价
def GetAvg_Window_High(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    if StartDayCount <= 0:
        totalVal = NowData.avg
        count = 1
        num = 1
    for single in dataList_240:
        if count >= StartDayCount and count <= ToDayCount:
            if totalVal < single.avg:
                totalVal = single.avg
            num = num + 1

        if count > ToDayCount:
            break
        count = count + 1
    return totalVal


#期间的成交量排名
def GetVolume_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界

        totalVolume = sum(
            x.volume 
            for x in full_list[StartDayCount:ToDayCount+1]
        )
        tempList.append({
            "code": val.code,
            "volume": totalVolume
        })


    tempList.sort(key=lambda x: x["volume"], reverse=True)

    count = 0
    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100


#期间的成交额排名
def GetVolume_Price_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界

        totalVolume_Price = sum(
            x.volume_price 
            for x in full_list[StartDayCount:ToDayCount+1]
        )
        tempList.append({
            "code": val.code,
            "volume_price": totalVolume_Price
        })


    tempList.sort(key=lambda x: x["volume_price"], reverse=True)

    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交额(万) {val['volume_price'] / 10000}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100



#期间的成交额涨跌幅排名
def GetVolume_Price_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        for single in full_list:
            if count == StartDayCount:
                startPrice = single.volume_price
            if count == ToDayCount:
                endPrice = single.volume_price
                ratio = (startPrice - endPrice) / endPrice if endPrice != 0 else 0
                tempList.append({
                    "code": val.code,
                    "ratio": ratio
                })
                break
            count = count + 1



    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交涨跌幅(万) {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100

#期间的成交量涨跌幅排名
def GetVolume_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        for single in full_list:
            if count == StartDayCount:
                startPrice = single.volume
            if count == ToDayCount:
                endPrice = single.volume
                ratio = (startPrice - endPrice) / endPrice if endPrice != 0 else 0
                tempList.append({
                    "code": val.code,
                    "ratio": ratio
                })
                break
            count = count + 1



    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万) {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100


#期间的涨跌幅排名
def GetChange_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        for single in full_list:
            if count == StartDayCount:
                startPrice = single.close
            if count == ToDayCount:
                endPrice = single.close
                ratio = (startPrice - endPrice) / endPrice
                tempList.append({
                    "code": val.code,
                    "ratio": ratio
                })
                break
            count = count + 1



    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    #count = 0
    #for val in tempList:
    #    count = count + 1
    #    print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 涨跌幅（无%） {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")

    count = 0
    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 涨跌幅（无%） {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100



#期间的振幅排名
def GetAmplitude_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        test_count = 0
        total = 0
        for single in full_list:
            if count >= StartDayCount and count <= ToDayCount:
                test_count = test_count + 1
                total = total + single.amplitude

            if count > ToDayCount:
                ratio = total / test_count
                tempList.append({
                    "code": val.code,
                    "ratio": ratio
                })
                break
            count = count + 1

    tempList.sort(key=lambda x: x["ratio"], reverse=True)


    #count = 0
    #for val in tempList:
    #    count = count + 1
        #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 振幅 {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")


    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 振幅: {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100



#期间的换手率涨跌幅排名
def GetTurn_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        if ToDayCount - StartDayCount > 3:
            avg1 = 0
            avg2 = 0
            avg1_count = 0
            avg2_count = 0
            for single in full_list:
                if count >= StartDayCount and count <= (ToDayCount - StartDayCount) / 2:
                    avg1 += single.turn
                    avg1_count += 1
                if count > (ToDayCount - StartDayCount) / 2 and count <= ToDayCount:
                    avg2 += single.turn
                    avg2_count += 1
                if count > ToDayCount:
                    avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                    avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                    ratio = (avg1 - avg2) / avg2
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count += 1
        else:
            for single in full_list:
                if count == StartDayCount:
                    startPrice = single.turn
                if count == ToDayCount:
                    endPrice = single.turn
                    ratio = (startPrice - endPrice) / endPrice
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count = count + 1
    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万) {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100


#期间的均价涨跌幅排名
def GetAvg_Ratio_Window_Rank(NowData : CalculationDataStruct.StructBaseClass, StartDayCount, ToDayCount, handler:CalculationDataHandle.BaseClass):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName

    industryDailyList : list[CalculationDataStruct.StructBaseClass] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        dataList_240:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.code, val.trade_date, 240)
        val.dataList_240 = dataList_240
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        history = val.dataList_240

        if not history:
            continue

        # 把今天 + 历史拼成一个统一序列
        full_list = [val] + history

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        if ToDayCount - StartDayCount > 3:
            avg1 = 0
            avg2 = 0
            avg1_count = 0
            avg2_count = 0
            for single in full_list:
                if count >= StartDayCount and count <= (ToDayCount - StartDayCount) / 2:
                    avg1 += single.avg
                    avg1_count += 1
                if count > (ToDayCount - StartDayCount) / 2 and count <= ToDayCount:
                    avg2 += single.avg
                    avg2_count += 1
                if count > ToDayCount:
                    avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                    avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                    ratio = (avg1 - avg2) / avg2
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count += 1
        else:
            for single in full_list:
                if count == StartDayCount:
                    startPrice = single.avg
                if count == ToDayCount:
                    endPrice = single.avg
                    ratio = (startPrice - endPrice) / endPrice
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count = count + 1
    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    for val in tempList:
        count = count + 1
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万) {val['ratio']}, 排名是：{count} / {len(industryCls.stockList)}")
            return (count / len(industryCls.stockList)) * 100
    return 100



#获取期间成交量状态：1放量， -1缩量， 0平量
def GetVolume_State_Windows(WindowData : CalculationDataStruct.StructBaseWindowClass):
    ratio = WindowData.volume_ratio
    if ratio > 0.2:
        return 1
    elif ratio < -0.2:
        return -1
    return 0
    


#获取涨跌状态：1涨， -1跌， 0横盘
def GetChange_Ratio_State_Windows(WindowData : CalculationDataStruct.StructBaseWindowClass):
    target = WindowData.change_Ratio
    if target > 2:
        return 1
    elif target < -2:
        return -1
    return 0


#获取震荡状态：1震荡， -1不震荡
def GetAmplitude_State_Windows(WindowData : CalculationDataStruct.StructBaseWindowClass):
    target = WindowData.avg_amplitude
    if target > 4:
        return 1
    else:
        return -1


#获取行业成交量
def GetIndustry_Volume(industryInfo :CalculationDataStruct.StructIndustryInfoClass, trade_date, handler:CalculationDataHandle.BaseClass):
    totalVolume = 0
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.volume:
            totalVolume += dailyCls.volume
    return totalVolume

#获取行业成交量涨跌幅
def GetIndustry_Volume_Ratio(industryInfo :CalculationDataStruct.StructIndustryInfoClass, trade_date, num, handler:CalculationDataHandle.BaseClass):
    if num == 1:
        for key, val in industryInfo.stockList.items():
            totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
            dataList:list[CalculationDataStruct.StructBaseClass] = handler.GetLastDateDataByNum(val.Code, trade_date, 1)
            lastTotalVolume = GetIndustry_Volume(industryInfo, dataList[0].trade_date, handler)
            print(f"上一个交易日是：{dataList[0].trade_date}, 上一个交易日的行业成交量是：{lastTotalVolume}, 当前交易日的行业成交量是：{totalVolume}")
            ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
            return ratio
    #elif num == 3:
    #        totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
    #        lastTotalVolume = GetIndustry_Volume(industryInfo, handler.GetLastDateByNum(trade_date, 3), handler)
    #        ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
    #        return ratio
    #elif num == 5:
    #elif num == 10:
    #elif num == 20:

