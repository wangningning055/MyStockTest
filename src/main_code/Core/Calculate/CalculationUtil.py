#from src.main_code.Core.Calculate import CalculationDataHandle
import traceback
import src.main_code.Core.Calculate.CalculationSpecial as CalculationSpecial
from operator import attrgetter
from datetime import date,datetime, timedelta
from datetime import date
import src.main_code.Core.Const as ConstVal

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core.Calculate import CalculationDataHandle
    from src.main_code.Core.DataStruct.Base import CalculationDataStruct

#计算行业内公司基本面数据（市值，盈，净，销，现）排名百分比
def CalculateIndustryBase(industryCls: "CalculationDataStruct.StructIndustryInfoClass",
                          handler: "CalculationDataHandle.BaseClass"):

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
        listDay = handler.totalDateList



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
            if base_data == None or base_data.trade_state == 0:
                continue
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

#获取上压力位
def GetUpPressure(NowData:"CalculationDataStruct.StructBaseClass", BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    #print("")
    #print("")
    #print(f"获取上压力位，日期是：{NowData.trade_date},  {BreakWindowCount}, ")
    #traceback.print_stack()
    #print("")
    #print("")
    return CalculationSpecial.CalculateUpPressure(NowData, 0, BreakWindowCount, handler)

#获取下压力位
def GetDownPressure(NowData:"CalculationDataStruct.StructBaseClass", BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressure(NowData, 0, BreakWindowCount, handler)

#是否突破上压力位
def GetIsBreakUpPressure(NowData:"CalculationDataStruct.StructBaseClass", BreakWindowCount):
    pressure = None
    if NowData == None:
        return 0
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20

    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40

    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60

    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120

    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure == None:
        return 0

    close = NowData.close
    
    ratio = (close - pressure) / pressure
    if ratio > 0.01:
        return 1
    return 0


#是否突破下压力位
def GetIsBreakDownPressure(NowData:"CalculationDataStruct.StructBaseClass", BreakWindowCount):
    pressure = None
    if NowData == None:
        return 0
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20

    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40

    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60

    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120

    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure == None:
        return 0

    close = NowData.close
    ratio = (close - pressure) / pressure
    #print(f"日期是：{NowData.trade_date}， 收盘价是：{close}， 下压力位是：{pressure}，下压力位窗口是：{BreakWindowCount}， 跌幅是：{ratio}")
    if ratio < -0.01:
        return 1
    return 0

#是否连续X日突破X日上压力位
def GetIsBreakUpPressure_Length(NowData:"CalculationDataStruct.StructBaseClass", Length, BreakWindowCount):
    breakCount= 0
    for single in NowData.dataList_240:
        isBreak = GetIsBreakUpPressure(single, BreakWindowCount)
        if isBreak == 1:
            breakCount += 1
            if breakCount >= Length:
                return 1
        else:
            break
    if breakCount >= Length:
        return 1
    return 0


#是否连续X日突破X日下压力位
def GetIsBreakDownPressure_Length(NowData:"CalculationDataStruct.StructBaseClass", Length, BreakWindowCount):
    breakCount= 0
    for single in NowData.dataList_240:
        isBreak = GetIsBreakDownPressure(single, BreakWindowCount)
        #print(f"是否连续{Length}日突破{BreakWindowCount}下压力位，当日是：{single.trade_date}, 是否突破：{isBreak}")
        if isBreak == 1:
            breakCount += 1
            if breakCount >= Length:
                return 1
        else:
            break
    if breakCount >= Length:
        return 1
    return 0

#获取X日均价与X日压力位的比值
def GetRatioDayAvg_Up_PressureWindow(NowData:"CalculationDataStruct.StructBaseClass", Length, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    count= 0
    total = 0
    for single in NowData.dataList_240:
        if count >= Length:
            break
        total += single.close
        count += 1

    total = total / count
    pressure = GetUpPressure(NowData, BreakWindowCount, handler)
    return total / pressure

#获取X日均价与X日压力位的比值
def GetRatioDayAvg_Down_PressureWindow(NowData:"CalculationDataStruct.StructBaseClass", Length, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    count= 0
    total = 0
    for single in NowData.dataList_240:
        if count >= Length:
            break
        total += single.close
        count += 1

    total = total / count
    pressure = GetDownPressure(NowData, BreakWindowCount, handler)
    return total / pressure



#获取价值股分数
def GetValueScore(NowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateValueScore(NowData, handler)

#获取成长股分数
def GetGrowScore(NowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateGrowScore(NowData, handler)

#获取价值股分数
def GetValueScore_Now(NowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateValueScore(NowData, handler, True)

#获取成长股分数
def GetGrowScore_Now(NowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateGrowScore(NowData, handler, True)


#获取是否在行业上涨周期
def GetIsInIndustryUp(NowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    now = datetime.now()
    month = now.month
    industry_self = handler.totalComponyIns.GetIndustryStrByCode(NowData.code)
    industryList = handler.main.recordDataCls.industry_Increase_Dic.get(month)
    if industryList == None:
        return 0
    for ind in industryList:
        if ind == industry_self:
            return 1
    return 0


#涨跌幅计算(只算第一天和最后num天)
def GetChange_Ratio(NowData:"CalculationDataStruct.StructBaseClass", num = 1):
    count = 0
    target_Price = 0
    todayPrice = NowData.close
    for val in NowData.dataList_240:
        if count == 0:
            count = count + 1
            continue
        target_Price = val.close
        count = count + 1
        if count >= num:
            break
    res = ((NowData.close - target_Price) / target_Price if target_Price != 0 else 0 ) * 100
    return res

#成交量涨跌幅计算(只算第一天和最后num天)
def GetVolume_Ratio(NowData:"CalculationDataStruct.StructBaseClass", num = 1):
    count = 0
    target_Price = 0
    for val in NowData.dataList_240:
        if count == 0:
            count = count + 1
            continue
        target_Price = val.volume
        count = count + 1
        if count >= num:
            break
    res = ((NowData.volume - target_Price) / target_Price if target_Price != 0 else 0 ) * 100
    return res

#平均振幅计算
def GetAmplitude_Avg(NowData:"CalculationDataStruct.StructBaseClass", num):
    count = 0
    avg1 = 0
    avg1Add = 0
    for val in NowData.dataList_240:
        if count < num:
            avg1 = avg1 + val.amplitude
            avg1Add += 1
        else:
            break
        count = count + 1


    avg1 = avg1 / avg1Add

    return avg1


#成交额涨跌幅计算(只算第一天和最后一天)
def GetVolume_Price(NowData:"CalculationDataStruct.StructBaseClass", num):
    count = 0
    target_Price = 0
    for val in NowData.dataList_240:
        if count == 0:
            count = count + 1
            continue
        target_Price = val.volume_price
        count = count + 1
        if count >= num:
            break
    res = ((NowData.volume_price - target_Price) / target_Price if target_Price != 0 else 0 ) * 100
    return res



def GetAvg_Ratio(NowData:"CalculationDataStruct.StructBaseClass"):
    if len(NowData.dataList_240) <= 1:
        return 0
    lastDay = NowData.dataList_240[1]
    target = (NowData.avg - lastDay.avg) / lastDay.avg if lastDay.avg != 0 else 0 
    #if NowData.code == "002917.SZ":
    #    print("####################################")
    #    print(NowData.trade_date)
    #    print(NowData.close)
    #    print(NowData.avg)
    #    print("--------------")
    #    print(lastDay.trade_date)
    #    print(lastDay.close)
    #    print(lastDay.avg)
    #    print(target)
    #    for cls in NowData.dataList_240:
    #        print(cls.trade_date)
    #    print("####################################")
    return target *100


#量比计算
def GetVolume_5(NowData : "CalculationDataStruct.StructBaseClass"):
    total = 0
    count = 0
    addCount = 0
    if(len(NowData.dataList_240)<=0):
        return 0
    for val in NowData.dataList_240:
        if count == 0:
            count = count + 1
            continue
        total = total + val.volume
        addCount += 1
        count = count + 1
        if(count > 5):
            break
    total = total / addCount if addCount != 0 else 0
    target = NowData.volume / total if total != 0 else 0 
    return target


#换手率涨跌幅计算
def GetTurn_Ratio(NowData : "CalculationDataStruct.StructBaseClass"):
    if len(NowData.dataList_240) <= 1:
        return 0

    lastDay = NowData.dataList_240[1]
    target = (NowData.turn - lastDay.turn) / lastDay.turn if lastDay.turn != 0 else 0 
    return target * 100


#成交动量计算
def GetVolume_Energy(NowData : "CalculationDataStruct.StructBaseClass", dayNum):
    count = 0
    total_Value = 0
    for data in NowData.dataList_240:
        if count == 0:
            count += 1
            continue
        total_Value = total_Value + data.volume_price
        count = count + 1 
        if(count >= dayNum):
            break
    #print(f"平均成交额变换：{(NowData.volume_price / (total_Value / dayNum))}， 涨跌幅{NowData.change_Ratio}")
    target = (NowData.volume_price / (total_Value / dayNum if dayNum != 0 else 0 )) * (NowData.change_Ratio / 100)
    return target


#获取在行业的市值排名
def GetIndustry_Rank_Value(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    CalculateIndustryBase(industryCls, handler)
    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Total_Value, reverse=True)
    )
    count = 0
    targetRank = 100
    for key, val in sorted_dict.items():
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if cls == None or cls.trade_state == 0:
            continue
        cls.total_value_ratio = tempRatio
        cls.total_value_rank_count = count
        #print(f"计算市市值：{val.Code}, {val.Com_name},  市值：{val.Total_Value / 100000000}亿,第几名： {count},行业数量： { len(industryCls.stockList)},结果： {tempRatio}")
        if val.Code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，流通市值 {val.Total_Value / 100000000}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank


    
#获取在行业的市盈率排名
def GetIndustry_Rank_Earn(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    CalculateIndustryBase(industryCls, handler)

    sorted_items = sorted(
        industryCls.stockList.items(),
        key=lambda x: (
            # 第一维度：正数排前面（0），负数排后面（1）
            0 if x[1].Earn > 0 else 1,
            # 第二维度：正数按Earn从小到大，负数按-Earn从小到大（等价于Earn从大到小）
            x[1].Earn if x[1].Earn > 0 else -x[1].Earn
        )
    )
    sorted_dict = dict(sorted_items)

    count = 0
    targetRank = 100
    for key, val in sorted_dict.items():
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if cls == None or cls.trade_state == 0:
            continue
        #print(f"计算市盈率：{val.Code}, {val.Com_name},  市盈率：{val.Earn},第几名： {count},行业数量： { len(industryCls.stockList)},结果： {tempRatio}")
        cls.earn_ratio = tempRatio

        if val.Code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank

#获取在行业的市净率排名
def GetIndustry_Rank_Clean(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    CalculateIndustryBase(industryCls, handler)

    sorted_dict = dict(
        sorted(industryCls.stockList.items(), key=lambda x: x[1].Clean)
    )
    count = 0
    targetRank = 100
    for key, val in sorted_dict.items():
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if cls == None:
            continue
        if val.Clean < 0:
            tempRatio = 100
        cls.clean_ratio = tempRatio
        #print(f"计算市净率：{val.Code}, {val.Com_name},  市净率：{val.Clean},第几名： {count},行业数量： { len(industryCls.stockList)},结果： {tempRatio}")

        if val.Code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank


#获取在行业的市销率排名
def GetIndustry_Rank_Sale(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    CalculateIndustryBase(industryCls, handler)

    sorted_items = sorted(
        industryCls.stockList.items(),
        key=lambda x: (
            0 if x[1].Sale > 0 else 1,
            x[1].Sale if x[1].Sale > 0 else -x[1].Sale
        )
    )
    sorted_dict = dict(sorted_items)
    
    count = 0
    targetRank = 100
    for key, val in sorted_dict.items():
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if cls == None:
            continue
        cls.sale_ratio = tempRatio
        #print(f"计算市销率：{val.Code}, {val.Com_name},  市销率：{val.Sale},第几名： {count},行业数量： { len(industryCls.stockList)},结果： {tempRatio}")

        if val.Code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank

#获取在行业的市现率排名
def GetIndustry_Rank_Cash(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    CalculateIndustryBase(industryCls, handler)

    sorted_items = sorted(
        industryCls.stockList.items(),
        key=lambda x: (
            0 if x[1].Sale > 0 else 1,
            x[1].Sale if x[1].Sale > 0 else -x[1].Sale
        )
    )
    sorted_dict = dict(sorted_items)
    count = 0
    targetRank = 100
    for key, val in sorted_dict.items():
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.cash_ratio = tempRatio
        #print(f"计算市现率：{val.Code}, {val.Com_name},  市现率：{val.Cash},第几名： {count},行业数量： { len(industryCls.stockList)},结果： {tempRatio}")

        if val.Code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank





#获取当日行业成交量排名(前%)
def GetIndustry_Rank_Volume(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.volume_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank





    #获取当日行业成交额排名(前%)
def GetIndustry_Rank_Volume_Price(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_price, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.total_price_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank


#获取当日行业成交额涨跌幅排名(前%)
def GetIndustry_Rank_Price_Ratio(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        temp = dailyCls.volume_price_ratio
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_price_ratio, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.total_price_ratio_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
    return targetRank

#获取当日行业成交量涨跌幅排名(前%)
def GetIndustry_Rank_Volume_Ratio(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        temp = dailyCls.volume_ratio
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.volume_ratio, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.volume_ratio_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank

    
#获取当日涨跌幅排名(前%)
def GetIndustry_Rank_Ratio(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.change_Ratio, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.ratio_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank



#获取当日振幅排名(前%)
def GetIndustry_Rank_Amplitude(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.amplitude, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.amplitude_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank



#获取换手率排名(前%)
def GetIndustry_Rank_Turn(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.turn, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.turn_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank



#获取当日换手率涨跌幅排名(前%)
def GetIndustry_Rank_Turn_Ratio(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        temp = dailyCls.turn_ratio
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.turn_ratio, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        if cls == None:
            continue

        cls.turn_ratio_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank



#获取当日均价涨跌幅排名(前%)
def GetIndustry_Rank_Avg_Ratio(NowData : "CalculationDataStruct.StructBaseClass",handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        temp = dailyCls.avg_ratio
        industryDailyList.append(dailyCls)

    industryDailyList.sort(key=lambda x: x.avg_ratio, reverse=True)
    count = 0
    targetRank = 100
    for val in industryDailyList:
        count = count + 1
        tempRatio = count#(count / len(industryCls.stockList)) * 100
        cls = handler.GetBaseDataClass(val.code, NowData.trade_date, False)
        if cls == None:
            continue

        cls.avg_industry_rank = tempRatio

        if val.code == code:
            targetRank = count#(count / len(industryCls.stockList)) * 100
            #print(f"行业：{industryStr}， 股票代码：{val.Code}, 股票名称{val.Name}，市盈率 {val.Earn}, 排名是：{count} / {len(industryCls.stockList)}")
    return targetRank

##X日均价
def GetAvg(NowData : "CalculationDataStruct.StructBaseClass", num):
    total = 0
    addCount = 0
    count = 0
    temp = 0
    for data in NowData.dataList_240:
        temp = temp + 1
        if temp > 10:
            break
        
    for data in NowData.dataList_240:
        total = total + data.avg
        addCount += 1
        if count >= (num - 1):
            break
        count = count + 1


    total = total / addCount
    return total



#获取成交量状态：1放量， -1缩量， 0平量
def GetVolumeState(NowData : "CalculationDataStruct.StructBaseClass", num):
    # 1. 定义降级优先级：按 num 从大到小，优先用大周期，无值则降级
    priority_map = {
        10: [10, 5, 3, 1],
        5: [5, 3, 1],
        3: [3, 1],
        1: [1]
    }
    # 获取当前num对应的降级序列（比如num=10则检查10→5→3→1）
    check_sequence = priority_map.get(num, [1])  # 兜底默认检查1日
    target = None

    for check_num in check_sequence:
        if check_num == 1:
            current_val = NowData.volume_ratio
        elif check_num == 3:
            current_val = NowData.volume_ratio_3
        elif check_num == 5:
            current_val = NowData.volume_ratio_5_percent
        elif check_num == 10:
            current_val = NowData.volume_ratio_10
        else:
            current_val = None
        
        if current_val is not None:
            target = current_val
            break  # 找到非None值，终止遍历

    if target > ConstVal.volume_boundary:
        return 1
    elif target < -ConstVal.volume_boundary:
        return -1
    return 0

#获取涨跌状态：1涨， -1跌， 0横盘
def GetRatioState(NowData : "CalculationDataStruct.StructBaseClass", num):

    # 1. 定义降级优先级：按 num 从大到小，优先用大周期，无值则降级
    priority_map = {
        10: [10, 5, 3, 1],
        5: [5, 3, 1],
        3: [3, 1],
        1: [1]
    }
    # 获取当前num对应的降级序列（比如num=10则检查10→5→3→1）
    check_sequence = priority_map.get(num, [1])  # 兜底默认检查1日
    target = None

    for check_num in check_sequence:
        if check_num == 1:
            current_val = NowData.change_Ratio
        elif check_num == 3:
            current_val = NowData.change_Ratio_3
        elif check_num == 5:
            current_val = NowData.change_Ratio_5
        elif check_num == 10:
            current_val = NowData.change_Ratio_10
        else:
            current_val = None
        
        if current_val is not None:
            target = current_val
            break  # 找到非None值，终止遍历

    #print(f"涨跌幅状态：{target}， {num}")

    if target > ConstVal.up_down_boundary:
        return 1
    elif target < -ConstVal.up_down_boundary:
        return -1
    return 0

#获取震荡状态：1震荡， -1不震荡
def GetAmplitudeState(NowData : "CalculationDataStruct.StructBaseClass", num):

    # 1. 定义降级优先级：按 num 从大到小，优先用大周期，无值则降级
    priority_map = {
        10: [10, 5, 3, 1],
        5: [5, 3, 1],
        3: [3, 1],
        1: [1]
    }
    # 获取当前num对应的降级序列（比如num=10则检查10→5→3→1）
    check_sequence = priority_map.get(num, [1])  # 兜底默认检查1日
    target = None

    for check_num in check_sequence:
        if check_num == 1:
            current_val = NowData.amplitude
        elif check_num == 3:
            current_val = NowData.amplitude_3
        elif check_num == 5:
            current_val = NowData.amplitude_5
        elif check_num == 10:
            current_val = NowData.amplitude_10
        else:
            current_val = None
        
        if current_val is not None:
            target = current_val
            break  # 找到非None值，终止遍历

    #print(f"振幅状态：{target}， {num}")

    if target > ConstVal.amplitude_boundary:
        return 1
    else:
        return -1



#获取突破上压力位次数
def GetBreakUpCount(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount):
    dataList_240 = NowData.dataList_240
    count = 0
    BreakCount = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
           
            if BreakWindowCount == 20:
                if single.is_break_upper_20 == 1:
                    BreakCount += 1


            if BreakWindowCount == 40:
                if single.is_break_upper_40 == 1:
                    BreakCount += 1

            if BreakWindowCount == 60:
                if single.is_break_upper_60 == 1:
                    BreakCount += 1

            if BreakWindowCount == 120:
                if single.is_break_upper_120 == 1:
                    BreakCount += 1

            if BreakWindowCount == 240:
                if single.is_break_upper_240 == 1:
                    BreakCount += 1

        if count >= ToDayCount:
            break
        count = count + 1
    return BreakCount

def GetBreakUpCount_20(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakUpCount(NowData, StartDayCount, ToDayCount, 20)

def GetBreakUpCount_40(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakUpCount(NowData, StartDayCount, ToDayCount, 40)

def GetBreakUpCount_60(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakUpCount(NowData, StartDayCount, ToDayCount, 60)

def GetBreakUpCount_120(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakUpCount(NowData, StartDayCount, ToDayCount, 120)

def GetBreakUpCount_240(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakUpCount(NowData, StartDayCount, ToDayCount, 240)




#获取突破下压力位次数
def GetBreakDownCount(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount):
    dataList_240 = NowData.dataList_240
    count = 0
    BreakCount = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
        
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
           
            if BreakWindowCount == 20:
                if single.is_break_lower_20 == 1:
                    BreakCount += 1

            if BreakWindowCount == 40:
                if single.is_break_lower_40 == 1:
                    BreakCount += 1

            if BreakWindowCount == 60:
                if single.is_break_lower_60 == 1:
                    BreakCount += 1

            if BreakWindowCount == 120:
                if single.is_break_lower_120 == 1:
                    BreakCount += 1

            if BreakWindowCount == 240:
                if single.is_break_lower_240 == 1:
                    BreakCount += 1

        if count >= ToDayCount:
            break
        count = count + 1
    return BreakCount

def GetBreakDownCount_20(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakDownCount(NowData, StartDayCount, ToDayCount, 20)

def GetBreakDownCount_40(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakDownCount(NowData, StartDayCount, ToDayCount, 40)

def GetBreakDownCount_60(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakDownCount(NowData, StartDayCount, ToDayCount, 60)

def GetBreakDownCount_120(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakDownCount(NowData, StartDayCount, ToDayCount, 120)

def GetBreakDownCount_240(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    return GetBreakDownCount(NowData, StartDayCount, ToDayCount, 240)




#区间平均开盘价与X日上压力位的比
def Get_Open_Break_Up_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_open
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20

    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40

    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60

    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120

    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure == None:
        return 0
    return open / pressure
#区间平均收盘价与X日上压力位的比
def Get_Close_Break_Up_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_close
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均均价与X日上压力位的比
def Get_Avg_Break_Up_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_avg  
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均最高价与X日上压力位的比
def Get_High_Break_Up_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_high
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均最低价与X日上压力位的比
def Get_Low_Break_Up_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_low
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.up_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.up_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.up_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.up_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.up_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均开盘价与X日下压力位的比
def Get_Open_Break_Low_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_open  # 区间平均开盘价
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均收盘价与X日下压力位的比
def Get_Close_Break_Low_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_close
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均均价与X日下压力位的比
def Get_Avg_Break_Low_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_avg 
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均最高价与X日下压力位的比
def Get_High_Break_Low_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_high  
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure

#区间平均最低价与X日下压力位的比
def Get_Low_Break_Low_Ratio(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, BreakWindowCount, handler:"CalculationDataHandle.BaseClass"):
    windowData = handler.GetWindowDataClass(NowData.code, NowData.trade_date, StartDayCount, ToDayCount)
    price = windowData.avg_low  
    pressure = None
    if BreakWindowCount == 20:
        pressure = NowData.down_pressure_20
    if BreakWindowCount == 40:
        pressure = NowData.down_pressure_40
    if BreakWindowCount == 60:
        pressure = NowData.down_pressure_60
    if BreakWindowCount == 120:
        pressure = NowData.down_pressure_120
    if BreakWindowCount == 240:
        pressure = NowData.down_pressure_240

    if pressure is None or pressure == 0:
        return 0
    return price / pressure


def Get_Close_Break_Up_Ratio_20(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Up_Ratio(NowData, StartDayCount, ToDayCount, 20, handler)

def Get_Close_Break_Up_Ratio_40(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Up_Ratio(NowData, StartDayCount, ToDayCount, 40, handler)

def Get_Close_Break_Up_Ratio_60(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Up_Ratio(NowData, StartDayCount, ToDayCount, 60, handler)

def Get_Close_Break_Up_Ratio_120(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Up_Ratio(NowData, StartDayCount, ToDayCount, 120, handler)

def Get_Close_Break_Up_Ratio_240(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Up_Ratio(NowData, StartDayCount, ToDayCount, 240, handler)





def Get_Close_Break_Low_Ratio_20(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Low_Ratio(NowData, StartDayCount, ToDayCount, 20, handler)

def Get_Close_Break_Low_Ratio_40(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Low_Ratio(NowData, StartDayCount, ToDayCount, 40, handler)

def Get_Close_Break_Low_Ratio_60(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Low_Ratio(NowData, StartDayCount, ToDayCount, 60, handler)

def Get_Close_Break_Low_Ratio_120(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Low_Ratio(NowData, StartDayCount, ToDayCount, 120, handler)

def Get_Close_Break_Low_Ratio_240(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return Get_Close_Break_Low_Ratio(NowData, StartDayCount, ToDayCount, 240, handler)

#获取低点趋势
def GetDownPressurePointUpRatio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio(NowData, StartDayCount, ToDayCount, handler)

#获取反弹点后的低点没有跌破反弹点前的高点
def GetDownPressurePointUp_UpTend(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUp_UpTend(NowData, StartDayCount, ToDayCount, handler)



# 获取最近两个低点的涨跌幅
def GetDownPressurePointUpRatio_two_ratio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_two_ratio(NowData, StartDayCount, ToDayCount, handler)

# 获取最近两个反弹点的涨跌幅
def GetDownPressurePointUpRatio_two_back_ratio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_two_back_ratio(NowData, StartDayCount, ToDayCount, handler)

# 获取上一个低点距离当前交易日天数
def GetDownPressurePointUpRatio_tend_days(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_tend_days(NowData, StartDayCount, ToDayCount, handler)

# 获取上一个低点到当前天的涨跌幅
def GetDownPressurePointUpRatio_now_ratio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_now_ratio(NowData, StartDayCount, ToDayCount, handler)

# 获取最近的反弹点到当前天的涨跌幅
def GetDownPressurePointUpRatio_rebound_now_ratio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_rebound_now_ratio(NowData, StartDayCount, ToDayCount, handler)

# 获取最近的反弹点到最近的低点涨跌幅
def GetDownPressurePointUpRatio_rebound_ratio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_rebound_ratio(NowData, StartDayCount, ToDayCount, handler)

# 获取最近的反弹点在低点列表的排名
def GetDownPressurePointUpRatio_rank(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateDownPressurePointUpRatio_rank(NowData, StartDayCount, ToDayCount, handler)


# 获取最近低点的成交量涨跌幅
def CalculateLowPoint_LastLowVolumeRatio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowPoint_LastLowVolumeRatio(NowData, StartDayCount, ToDayCount, handler)

# 获取最近反弹点的成交量涨跌幅
def CalculateLowPoint_LastBackLowVolumeRatio(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowPoint_LastBackLowVolumeRatio(NowData, StartDayCount, ToDayCount, handler)

# 获取低点的平均成交量涨跌幅
def CalculateLowPoint_LowVolumeRatio_Avg(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowPoint_LowVolumeRatio_Avg(NowData, StartDayCount, ToDayCount, handler)

# 获取反弹点的平均成交量涨跌幅
def CalculateLowPoint_BackLowVolumeRatio_Avg(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowPoint_BackLowVolumeRatio_Avg(NowData, StartDayCount, ToDayCount, handler)

# 获取反弹点的平均成交量涨跌幅
def CalculateLowPoint_Tend_Slop(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowPoint_Tend_Slop(NowData, StartDayCount, ToDayCount, handler)

# 获取反弹点的平均成交量涨跌幅
def CalculateLowBack_Tend_Slop(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateLowBack_Tend_Slop(NowData, StartDayCount, ToDayCount, handler)


# 区间是否为上下3的箱体
def CalculateIsCube_3(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 3)

# 区间是否为上下5的箱体
def CalculateIsCube_5(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 5)

# 区间是否为上下10的箱体
def CalculateIsCube_10(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 10)

# 区间是否为上下15的箱体
def CalculateIsCube_15(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 15)

# 区间是否为上下20的箱体
def CalculateIsCube_20(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 20)

# 区间是否为上下30的箱体
def CalculateIsCube_30(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 30)

# 区间是否为上下50的箱体
def CalculateIsCube_50(NowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    return CalculationSpecial.CalculateIsCube(NowData, StartDayCount, ToDayCount, handler, 50)


#获取涨停次数
def GetUpStopCount(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    upStopCount = 0
    target = 0.1
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    if NowData.code.startswith("300") or NowData.code.startswith("688") or NowData.code.startswith("301"):
        target = 0.2
        
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if abs(single.close - (single.last_close + single.last_close * target)) / single.close <= 0.003 :
                upStopCount = upStopCount + 1
                #print(f"前{count}天，这天涨停")
        if count >= ToDayCount:
            break
        count = count + 1
    return upStopCount

#获取跌停次数
def GetDownStopCount(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    upStopCount = 0
    target = 0.1
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    if NowData.code.startswith("300") or NowData.code.startswith("688") or NowData.code.startswith("301"):
        target = 0.2
        
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if abs(single.close - (single.last_close - single.last_close * target)) / single.close <= 0.003 :
                upStopCount = upStopCount + 1
                #print(f"前{count}天，这天涨停")
            #print(f"这是第{count}天, 开盘价：{single.open}，  收盘价：{single.close}  涨停价：{single.last_close + single.last_close * target}，  插值：{abs(single.close - (single.open + single.open * target)) / single.open}")
        if count >= ToDayCount:
            break
        count = count + 1
    return upStopCount

#期间的整体成交量
def GetVolume_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    totalVolume = 0
    dataList_240 = NowData.dataList_240
    count = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
        
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVolume = totalVolume + single.volume
        if count >= ToDayCount:
            break

        count = count + 1
    return totalVolume


#期间的整体成交额
def GetVolume_Price_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    totalVolume = 0
    dataList_240 = NowData.dataList_240
    count = 0
        
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVolume = totalVolume + single.volume_price
        if count >= ToDayCount:
            break

        count = count + 1
    return totalVolume


#期间的整体成交量涨跌幅
def GetVolume_Ratio_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    count = 0
    startVal = 0
    endVal = 0
    full_list = NowData.dataList_240
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (StartDayCount + (ToDayCount - StartDayCount) / 2):
                avg1 += single.volume
                avg1_count += 1
            if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                avg2 += single.volume
                avg2_count += 1
            if count >= ToDayCount or count >= len(full_list) - 1:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio * 100
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.volume
            if count == ToDayCount or count == len(full_list) - 1:
                endVal = single.volume
                break
            count = count + 1
        #if ToDayCount == 3:
        #    print(f"startVal :{startVal / 100},  endVal:  {endVal / 100}")
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0


#期间的整体成交额涨跌幅
def GetVolume_Price_Ratio_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    startVal = 0
    endVal = 0
    full_list = NowData.dataList_240

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    count = 0
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (StartDayCount + (ToDayCount - StartDayCount) / 2):
                avg1 += single.volume_price
                avg1_count += 1
            if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                avg2 += single.volume_price
                avg2_count += 1
            if count >= ToDayCount or count >= len(full_list) - 1:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio * 100
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.volume_price
            if count == ToDayCount or count == len(full_list) - 1:
                endVal = single.volume_price
                break
            count = count + 1
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0
    

#期间的整体换手率涨跌幅
def GetTurn_Ratio_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    startVal = 0
    endVal = 0
    full_list = NowData.dataList_240
    count = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    if ToDayCount - StartDayCount > 3:
        avg1 = 0
        avg2 = 0
        avg1_count = 0
        avg2_count = 0
        for single in full_list:
            if count >= StartDayCount and count <= (StartDayCount + (ToDayCount - StartDayCount) / 2):
                avg1 += single.turn
                avg1_count += 1
            if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                avg2 += single.turn
                avg2_count += 1
            if count >= ToDayCount or count >= len(full_list) - 1:
                avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                return ratio * 100
            count += 1
    else:
        for single in full_list:
            if count == StartDayCount:
                startVal = single.turn
            if count == ToDayCount or count == len(full_list) - 1:
                endVal = single.turn
                break
            count = count + 1
        return (startVal - endVal) * 100/ endVal if endVal != 0 else 0


#期间的涨跌幅
def GetChange_Ratio_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    startVal = 0
    endVal = 0
        
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count == StartDayCount:
            startVal = single.close
            #print("-----------------------------------------------------")
            #print(f"正在算涨跌幅，开始日期是：{single.trade_date}, 涨跌幅开始值是：{startVal}， {StartDayCount}  {ToDayCount}")
        if count == ToDayCount or count == len(dataList_240) - 1:
            endVal = single.close
            #print(f"正在算涨跌幅，结束日期是：{single.trade_date}, 涨跌幅结束值是：{endVal}， {StartDayCount}  {ToDayCount}")
            #print("-----------------------------------------------------")
            break
        count = count + 1
    return (startVal - endVal)*100 / endVal

#期间的整体涨跌幅
def GetChange_Ratio_Total_Window(NowData : "CalculationDataStruct.StructBaseClass",StartDayCount, ToDayCount):
    fullDataList = NowData.dataList_240

    dayCount = 0
    firstVolume = 0
    firstVolumeAddCount = 0
    secondVolume = 0
    secondVolumeAddCount = 0
    ToDayCount = len(fullDataList) if ToDayCount > len(fullDataList) else ToDayCount
    for day in fullDataList:
        if ToDayCount - StartDayCount < 3:
            if dayCount == StartDayCount:
                firstVolume = day.close

            if dayCount == ToDayCount or  dayCount == len(fullDataList) - 1:
                secondVolume = day.close
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            dayCount = dayCount + 1
        else:
            if dayCount >= StartDayCount and dayCount < (StartDayCount + (ToDayCount - StartDayCount) / 2) :
                firstVolume += day.close
                firstVolumeAddCount += 1
            elif dayCount >= (StartDayCount + (ToDayCount - StartDayCount) / 2) and dayCount < ToDayCount:
                secondVolume += day.close
                secondVolumeAddCount += 1

            dayCount = dayCount + 1

            if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1:


                firstVolume = firstVolume / firstVolumeAddCount if firstVolumeAddCount > 0 else 0
                secondVolume = secondVolume / secondVolumeAddCount if secondVolumeAddCount > 0 else 0


                #if ToDayCount == 20:
                #    print(f"20   firstVolume :{firstVolume}  firstVolumeAddCount   {firstVolumeAddCount} secondVolume {secondVolume}   secondVolumeAddCount  {secondVolumeAddCount}   {day.trade_date}")
                #if ToDayCount == 40:
                #    print(f"40   firstVolume :{firstVolume}  firstVolumeAddCount   {firstVolumeAddCount} secondVolume {secondVolume}   secondVolumeAddCount  {secondVolumeAddCount}   {day.trade_date}")
                #if ToDayCount == 60:
                #    print(f"60   firstVolume :{firstVolume}  firstVolumeAddCount   {firstVolumeAddCount} secondVolume {secondVolume}   secondVolumeAddCount  {secondVolumeAddCount}   {day.trade_date}")
                #if ToDayCount == 120:
                #    print(f"120   firstVolume :{firstVolume}  firstVolumeAddCount   {firstVolumeAddCount} secondVolume {secondVolume}   secondVolumeAddCount  {secondVolumeAddCount}   {day.trade_date}")
                #if ToDayCount == 240 or ToDayCount == len(fullDataList):
                #    print(f"240 {len(fullDataList)}  firstVolume :{firstVolume}  firstVolumeAddCount   {firstVolumeAddCount} secondVolume {secondVolume}   secondVolumeAddCount  {secondVolumeAddCount}   {day.trade_date}")
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100


#期间的均价涨跌幅
def GetAvg_Ratio_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    startVal = 0
    endVal = 0
        
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count == StartDayCount:
            startVal = single.avg
        if count == ToDayCount or  count == len(dataList_240) - 1:
            endVal = single.avg
            break
        count = count + 1
    return (startVal - endVal)*100 / endVal if endVal != 0 else 0

#期间的整体均价涨跌幅
def GetAvg_Ratio_Total_Window(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    fullDataList = NowData.dataList_240

    dayCount = 0
    firstVolume = 0
    firstVolumeAddCount = 0
    secondVolume = 0
    secondVolumeAddCount = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for day in fullDataList:
        if ToDayCount - StartDayCount < 3:
            if dayCount == StartDayCount:
                firstVolume = day.avg

            if dayCount == ToDayCount or  dayCount == len(fullDataList) - 1:
                secondVolume = day.avg
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            dayCount = dayCount + 1
        else:
            if dayCount >= StartDayCount and dayCount < (StartDayCount + (ToDayCount - StartDayCount) / 2) :
                firstVolume += day.avg
                firstVolumeAddCount += 1
            elif dayCount >= (StartDayCount + (ToDayCount - StartDayCount) / 2) and dayCount < ToDayCount:
                secondVolume += day.avg
                secondVolumeAddCount += 1

            dayCount = dayCount + 1

            if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1:
                firstVolume = firstVolume / firstVolumeAddCount if firstVolumeAddCount > 0 else 0
                secondVolume = secondVolume / secondVolumeAddCount if secondVolumeAddCount > 0 else 0
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100




#期间的平均开盘价
def GetOpen_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.open
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    #print(f"总共的天数是{num},加了：{num}    total = {totalVal}")
    return totalVal / (num)


#期间的平均收盘价
def GetClose_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:

        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.close
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    #print(f"总共的天数是{num},加了：{num}    total = {totalVal}")
    return totalVal / num if num != 0 else 0 


#期间的平均最高价
def GetHigh_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.high
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 

#期间的平均最低价
def GetLow_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.low
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 


#期间的平均成交量
def GetVolume_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.volume
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 


#期间的平均成交额
def GetVolume_Price_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:

        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.volume_price
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal /  num if num != 0 else 0 



#期间的平均量比
def Get_VolumeRatio_5_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            volume_Ratio_5 = GetVolume_5(single)
            totalVal = totalVal + volume_Ratio_5
            num = num + 1
        if count >= ToDayCount:
            break
        count = count + 1

    return totalVal / num if num != 0 else 0 


def GetTurn_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.turn
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 


def GetChangeRatio_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.change_Ratio
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 

def GetAmplitude_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.amplitude
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 

def GetAvg_Price_Window_Avg(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            totalVal = totalVal + single.avg
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal / num if num != 0 else 0 




#最低开盘价
def GetOpen_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.open:
                totalVal = single.open
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低收盘价
def GetClose_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.close:
                totalVal = single.close
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低昨收价
def GetLastClose_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.last_close:
                totalVal = single.last_close
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低最高价
def GetHigh_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.high:
                totalVal = single.high
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低最低价
def GetLow_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.low:
                totalVal = single.low
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低成交量
def GetVolume_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.volume:
                totalVal = single.volume
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低成交额
def GetVolume_Price_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.volume_price:
                totalVal = single.volume_price
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低量比
def GetVolume_Ratio_5_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            volume_Ratio_5 = GetVolume_5(single)

            if totalVal > volume_Ratio_5:
                totalVal = volume_Ratio_5
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低换手率
def GetTurn_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.turn:
                totalVal = single.turn
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低涨跌幅
def GetChange_Ratio_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.change_Ratio:
                totalVal = single.change_Ratio
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低振幅
def GetAmplitude_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.amplitude:
                totalVal = single.amplitude
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最低均价
def GetAvg_Window_Low(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = float('inf')
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal > single.avg:
                totalVal = single.avg
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal





#最高开盘价
def GetOpen_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.open:
                totalVal = single.open
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高收盘价
def GetClose_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.close:
                totalVal = single.close
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高昨收价
def GetLastClose_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.last_close:
                totalVal = single.last_close
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高最高价
def GetHigh_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.high:
                totalVal = single.high
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高最低价
def GetLow_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.low:
                totalVal = single.low
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高成交量
def GetVolume_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.volume:
                totalVal = single.volume
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高成交额
def GetVolume_Price_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.volume_price:
                totalVal = single.volume_price
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高量比
def GetVolume_Ratio_5_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            volume_Ratio_5 = GetVolume_5(single)

            if totalVal < volume_Ratio_5:
                totalVal = volume_Ratio_5
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高换手率
def GetTurn_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.turn:
                totalVal = single.turn
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高涨跌幅
def GetChange_Ratio_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = -1000
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.change_Ratio:
                totalVal = single.change_Ratio
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高振幅
def GetAmplitude_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.amplitude:
                totalVal = single.amplitude
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal

#最高均价
def GetAvg_Window_High(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount):
    dataList_240 = NowData.dataList_240
    count = 0
    totalVal = 0
    num = 0
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    for single in dataList_240:
        if count >= StartDayCount and count < ToDayCount:
            if totalVal < single.avg:
                totalVal = single.avg
            num = num + 1

        if count >= ToDayCount:
            break
        count = count + 1
    return totalVal


#期间的成交量排名
def GetVolume_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)

    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 
    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue

        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

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
    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        #print(f"行业：{industryStr}， 股票代码：{val["code"]}")
        tempWindowCls.volume_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio


#期间的成交额排名
def GetVolume_Price_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        full_list = val.dataList_240

        if not full_list:
            continue


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

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.total_price_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio



#期间的成交额涨跌幅排名
def GetVolume_Price_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

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
                if count >= StartDayCount and count <= (StartDayCount +(ToDayCount - StartDayCount) / 2):
                    avg1 += single.volume_price
                    avg1_count += 1
                if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                    avg2 += single.volume_price
                    avg2_count += 1
                if count >= ToDayCount or count >= len(full_list) - 1:
                    avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                    avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                    ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count += 1
        else:
            for single in full_list:
                if count == StartDayCount:
                    startPrice = single.volume_price
                if count == ToDayCount or count == len(full_list) - 1:
                    endPrice = single.volume_price
                    ratio = (startPrice - endPrice) / endPrice
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count = count + 1



    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.total_price_ratio_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio

#期间的成交量涨跌幅排名
def GetVolume_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

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
                if count >= StartDayCount and count <= (StartDayCount +(ToDayCount - StartDayCount) / 2):
                    avg1 += single.volume
                    avg1_count += 1
                if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                    avg2 += single.volume
                    avg2_count += 1
                if count >= ToDayCount or count >= len(full_list) - 1:
                    avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                    avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                    ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count += 1
        else:
            for single in full_list:
                if count == StartDayCount:
                    startPrice = single.volume
                if count == ToDayCount or count == len(full_list) - 1:
                    endPrice = single.volume
                    ratio = (startPrice - endPrice) / endPrice
                    tempList.append({
                        "code": val.code,
                        "ratio": ratio
                    })
                    break
                count = count + 1



    tempList.sort(key=lambda x: x["ratio"], reverse=True)

    count = 0

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.volume_ratio_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio

#期间的涨跌幅排名
def GetChange_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        startPrice = 0
        endPrice = 0
        for single in full_list:
            if count == StartDayCount:
                startPrice = single.close
            if count == ToDayCount or count == len(full_list):
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

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.ratio_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio


#期间的振幅排名
def GetAmplitude_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

        if ToDayCount >= len(full_list):
            continue  # 防止越界
        count = 0
        test_count = 0
        total = 0
        for single in full_list:
            if count >= StartDayCount and count < ToDayCount:
                test_count = test_count + 1
                total = total + single.amplitude

            if count >= ToDayCount or count >= len(full_list) - 1:
                ratio = total / test_count if test_count != 0 else 0 
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

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.amplitude_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio



#期间的换手率涨跌幅排名
def GetTurn_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

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
                if count >= StartDayCount and count <= (StartDayCount +(ToDayCount - StartDayCount) / 2):
                    avg1 += single.turn
                    avg1_count += 1
                if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                    avg2 += single.turn
                    avg2_count += 1
                if count >= ToDayCount or count >= len(full_list) - 1:
                    avg1 = avg1 / avg1_count if avg1_count > 0 else 0
                    avg2 = avg2 / avg2_count if avg2_count > 0 else 0
                    ratio = (avg1 - avg2) / avg2 if avg2 != 0 else 0
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
                if count == ToDayCount or count == len(full_list) - 1:
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

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.turn_ratio_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio


#期间的均价涨跌幅排名
def GetAvg_Ratio_Window_Rank(NowData : "CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    code = NowData.code
    industryCls = handler.totalComponyIns.GetIndustryClsByCode(code)
    industryStr = industryCls.industryName
    ToDayCount = len(NowData.dataList_240) if ToDayCount > len(NowData.dataList_240) else ToDayCount 

    industryDailyList : list["CalculationDataStruct.StructBaseClass"] = []
    for key, val in industryCls.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, NowData.trade_date, False)
        if dailyCls == None:
            continue
        industryDailyList.append(dailyCls)

    tempList = []
    index = 0
    for val in industryDailyList:
        index += 1
        #print(f"正在计算股票：{val.code}, 第{index}个，总共有{len(industryDailyList)}个")
        full_list = val.dataList_240

        if not full_list:
            continue

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
                if count >= StartDayCount and count <= (StartDayCount + (ToDayCount - StartDayCount) / 2):
                    avg1 += single.avg
                    avg1_count += 1
                if count > (StartDayCount + (ToDayCount - StartDayCount) / 2) and count < ToDayCount:
                    avg2 += single.avg
                    avg2_count += 1
                if count >= ToDayCount or count >= len(full_list) - 1:
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
                if count == ToDayCount or count == len(full_list) - 1:
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

    rank_Ratio = 100
    for val in tempList:
        count = count + 1
        temp_Ratio = count#(count / len(industryCls.stockList)) * 100
        #name = handler.totalComponyIns.GetComponyInfo(val.code).Name
        #print(f"行业：{industryStr}， 股票代码：{val.code}, 股票名称:{name} 成交量(万手) {val.volume / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
        tempWindowCls = handler.GetWindowDataClass(val["code"], NowData.trade_date, StartDayCount, ToDayCount, True)
        if tempWindowCls == None:
            continue
        tempWindowCls.avg_industry_rank = temp_Ratio
        if val["code"] == code:
            #print(f"行业：{industryStr}， 股票代码：{val['code']}, 股票名称:{handler.totalComponyIns.GetComponyInfo(val['code']).Name} 成交量(万手) {val['volume'] / 1000000}, 排名是：{count} / {len(industryCls.stockList)}")
            rank_Ratio = temp_Ratio
    return rank_Ratio



#获取期间成交量状态：1放量， -1缩量， 0平量
def GetVolume_State_Windows(WindowData : "CalculationDataStruct.StructBaseWindowClass"):
    ratio = WindowData.volume_ratio
    if ratio > ConstVal.volume_boundary:
        return 1
    elif ratio < -ConstVal.volume_boundary:
        return -1
    return 0
    


#获取涨跌状态：1涨， -1跌， 0横盘
def GetChange_Ratio_State_Windows(WindowData : "CalculationDataStruct.StructBaseWindowClass"):
    target = WindowData.change_Ratio_Total
    if target > ConstVal.up_down_boundary:
        return 1
    elif target < -ConstVal.up_down_boundary:
        return -1
    return 0


#获取震荡状态：1震荡， -1不震荡
def GetAmplitude_State_Windows(WindowData : "CalculationDataStruct.StructBaseWindowClass"):
    target = WindowData.avg_amplitude
    if target > ConstVal.amplitude_boundary:
        return 1
    else:
        return -1

#获取行业整体价格
def GetIndustry_Avg_Price(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    totalPrice = ConstVal.NoneValue
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.close:
            if totalPrice == ConstVal.NoneValue:
                totalPrice = 0
            totalPrice += dailyCls.close
    return totalPrice


#获取行业成交量
def GetIndustry_Volume(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    totalVolume = ConstVal.NoneValue
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        
        if dailyCls and dailyCls.volume:
            if totalVolume == ConstVal.NoneValue:
                totalVolume = 0

            totalVolume += dailyCls.volume
    return totalVolume

#获取行业成交额
def GetIndustry_Volume_Price(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    totalVolume = ConstVal.NoneValue
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.volume_price:
            if totalVolume == ConstVal.NoneValue:
                totalVolume = 0
            totalVolume += dailyCls.volume_price
    return totalVolume


#获取行业成交量涨跌幅或与均线的比
def GetIndustry_Volume_Ratio(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, num, handler:"CalculationDataHandle.BaseClass"):
    if num == 1:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 10)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
                lastTotalVolume = GetIndustry_Volume(industryInfo, dataList[1].trade_date, handler)
                #print(f"上一个交易日是：{dataList[0].trade_date}, 上一个交易日的行业成交量是：{lastTotalVolume}, 当前交易日的行业成交量是：{totalVolume}")
                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
            return ratio * 100
    elif num == 3:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 4)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue
                    lastTotalVolume += GetIndustry_Volume(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 5:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 6)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue

                    lastTotalVolume += GetIndustry_Volume(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 10:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 11)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue

                    lastTotalVolume += GetIndustry_Volume(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 20:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 21)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue
                    lastTotalVolume += GetIndustry_Volume(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100


#获取行业成交额涨跌幅或与均线的比
def GetIndustry_Volume_Price_Ratio(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, num, handler:"CalculationDataHandle.BaseClass"):
    if num == 1:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 10)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume_Price(industryInfo, trade_date, handler)
                lastTotalVolume = GetIndustry_Volume_Price(industryInfo, dataList[1].trade_date, handler)
                #print(f"上一个交易日是：{dataList[0].trade_date}, 上一个交易日的行业成交量是：{lastTotalVolume}, 当前交易日的行业成交量是：{totalVolume}")
                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
            return ratio * 100
    elif num == 3:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 4)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume_Price(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue
                    lastTotalVolume += GetIndustry_Volume_Price(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 5:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 5)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume_Price(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue

                    lastTotalVolume += GetIndustry_Volume_Price(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 10:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 11)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume_Price(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue

                    lastTotalVolume += GetIndustry_Volume_Price(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100
    elif num == 20:
        for key, val in industryInfo.stockList.items():
            dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 22)
            if dataList.__len__() > 0:
                totalVolume = GetIndustry_Volume_Price(industryInfo, trade_date, handler)
                lastTotalVolume = 0
                count = 0
                for single in dataList:
                    if count == 0:
                        count += 1
                        continue

                    lastTotalVolume += GetIndustry_Volume_Price(industryInfo, single.trade_date, handler)
                    count += 1

                lastTotalVolume = lastTotalVolume / (count - 1) if (count - 1) != 0 else 0 

                ratio = (totalVolume - lastTotalVolume) / lastTotalVolume if lastTotalVolume != 0 else 0
                return ratio * 100

#获取行业涨跌幅或与均线的比
def GetIndustry_Change_Ratio(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    total = 0
    lastTotal= 0
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.close:
            total += dailyCls.close
        dataList:list["CalculationDataStruct.StructBaseClass"] = handler.GetLastDateDataByNum(val.Code, 20)
        if dataList.__len__() > 0:
            lastDailyCls = dataList[1]
            if lastDailyCls and lastDailyCls.close:
                lastTotal += lastDailyCls.close

    ratio = (total - lastTotal) / lastTotal if lastTotal != 0 else 0
    return ratio * 100


#获取行业上涨股数量
def GetIndustry_Up_Count(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    count = 0
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.change_Ratio and dailyCls.change_Ratio > ConstVal.up_down_boundary:
            #print(f"上涨股票：{val.Code}, {val.Name},  涨幅：{dailyCls.change_Ratio}")
            count += 1
    return count

#获取行业下跌股数量
def GetIndustry_Down_Count(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, handler:"CalculationDataHandle.BaseClass"):
    count = 0
    for key, val in industryInfo.stockList.items():
        dailyCls = handler.GetBaseDataClass(val.Code, trade_date, False)
        if dailyCls and dailyCls.change_Ratio and dailyCls.change_Ratio < -ConstVal.up_down_boundary:
            #print(f"下跌股票：{val.Code},{val.Name},   跌幅：{dailyCls.change_Ratio}")
            count += 1
    return count



#获取期间内行业整体成交量
def GetIndustry_Volume_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
        
    dayCount = 0
    totalVolume = 0
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            vol =  GetIndustry_Volume(industryInfo, day, handler)
            if vol == ConstVal.NoneValue:
                continue
            totalVolume += vol

        dayCount = dayCount + 1
        if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1 :
            return totalVolume


#获取期间内行业整体成交额
def GetIndustry_Volume_Price_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
        
    dayCount = 0
    totalVolume = 0
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            vol = GetIndustry_Volume_Price(industryInfo, day, handler)
            if vol == ConstVal.NoneValue:
                continue
            totalVolume += vol

        dayCount = dayCount + 1
        if dayCount >= ToDayCount  or dayCount >= len(fullDataList) - 1:
            return totalVolume
        

#获取期间内行业平均成交量
def GetIndustry_Volume_Avg_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
        
    dayCount = 0
    addCount = 0
    totalVolume = 0
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            vol =  GetIndustry_Volume(industryInfo, day, handler)
            if vol == ConstVal.NoneValue:
                continue
            totalVolume += vol
            addCount += 1

        dayCount = dayCount + 1
        if dayCount >= ToDayCount  or dayCount >= len(fullDataList) - 1:
            return totalVolume / addCount if addCount > 0 else 0


#获取期间内行业平均成交额
def GetIndustry_Volume_Price_Avg_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList

    dayCount = 0
    addCount = 0
    totalVolume = 0
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            vol =  GetIndustry_Volume_Price(industryInfo, day, handler)
            if vol == ConstVal.NoneValue:
                continue
            totalVolume += vol
            addCount += 1
            #print(f"目标日期：{day}")

        dayCount = dayCount + 1
        if dayCount >= ToDayCount  or dayCount >= len(fullDataList) - 1:
            return totalVolume / addCount if addCount > 0 else 0
        


#获取期间内行业成交量涨跌幅
def GetIndustry_Volume_Ratio_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):

    dayCount = 0
    fullDataList = handler.totalDateList

        
    dayCount = 0
    addCount = 0
    firstVolume = 0
    firstVolumeAddCount = 0
    secondVolume = 0
    secondVolumeAddCount = 0
    for day in fullDataList:
        vol = GetIndustry_Volume(industryInfo, day, handler)
        if vol == ConstVal.NoneValue:
            continue
        if ToDayCount - StartDayCount < 3:
            if dayCount == StartDayCount:
                firstVolume = vol

            if dayCount == ToDayCount or dayCount == len(fullDataList):
                secondVolume = vol

                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            dayCount = dayCount + 1
        else:
            if dayCount >= StartDayCount and dayCount < (StartDayCount + (ToDayCount - StartDayCount) / 2) :
                vol1 = vol

                firstVolume += vol1
                firstVolumeAddCount += 1
            elif dayCount >= (StartDayCount + (ToDayCount - StartDayCount) / 2) and dayCount < ToDayCount:
                vol2 = vol

                secondVolume += vol2
                secondVolumeAddCount += 1

            dayCount = dayCount + 1

            if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1:
                firstVolume = firstVolume / firstVolumeAddCount if firstVolumeAddCount != 0 else 0 
                secondVolume = secondVolume / secondVolumeAddCount if secondVolumeAddCount != 0 else 0 
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100


#获取期间内行业成交额涨跌幅
def GetIndustry_Volume_Price_Ratio_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
        
    dayCount = 0
    addCount = 0
    firstVolume = 0
    firstVolumeAddCount = 0
    secondVolume = 0
    secondVolumeAddCount = 0
    for day in fullDataList:
        vol = GetIndustry_Volume_Price(industryInfo, day, handler)
        if vol == ConstVal.NoneValue:
            continue

        if ToDayCount - StartDayCount < 3:
            if dayCount == StartDayCount:
                firstVolume = vol

            if dayCount == ToDayCount or dayCount == len(fullDataList):
                secondVolume = vol
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            dayCount = dayCount + 1
        else:
            if dayCount >= StartDayCount and dayCount < (StartDayCount + (ToDayCount - StartDayCount) / 2) :
                firstVolume += vol
                firstVolumeAddCount += 1
            elif dayCount >= (StartDayCount + (ToDayCount - StartDayCount) / 2) and dayCount < ToDayCount:
                secondVolume += vol
                secondVolumeAddCount += 1

            dayCount = dayCount + 1

            if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1:
                firstVolume = firstVolume / firstVolumeAddCount if firstVolumeAddCount != 0 else 0 
                secondVolume = secondVolume / secondVolumeAddCount if secondVolumeAddCount != 0 else 0 
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100

#行业涨跌幅
def GetIndustry_Change_Ratio_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
    for day in fullDataList:
        price =  GetIndustry_Avg_Price(industryInfo, day, handler)
        if price == ConstVal.NoneValue:
            continue
        if dayCount == StartDayCount:
            firstPrice = price
        if dayCount == ToDayCount or dayCount == len(fullDataList):
            secondPrice = price
            ratio = (firstPrice - secondPrice) / secondPrice if secondPrice != 0 else 0
            return ratio * 100
        dayCount = dayCount + 1

   

#行业整体涨跌幅
def GetIndustry_Change_Ratio_Total_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    fullDataList = handler.totalDateList
        
    dayCount = 0
    addCount = 0
    firstVolume = 0
    firstVolumeAddCount = 0
    secondVolume = 0
    secondVolumeAddCount = 0
    for day in fullDataList:
        price =  GetIndustry_Avg_Price(industryInfo, day, handler)
        if price == ConstVal.NoneValue:
            continue
        if ToDayCount - StartDayCount < 3:


            if dayCount == StartDayCount:
                firstVolume = price

            if dayCount == ToDayCount or dayCount == len(fullDataList):
                secondVolume = price
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            dayCount = dayCount + 1
        else:
            if dayCount >= StartDayCount and dayCount < (StartDayCount + (ToDayCount - StartDayCount) / 2) :
                firstVolume += price
                firstVolumeAddCount += 1
            elif dayCount >= (StartDayCount + (ToDayCount - StartDayCount) / 2) and dayCount < ToDayCount:
                secondVolume += price
                secondVolumeAddCount += 1

            dayCount = dayCount + 1

            if dayCount >= ToDayCount or dayCount >= len(fullDataList) - 1:
                firstVolume = firstVolume / firstVolumeAddCount if firstVolumeAddCount != 0 else 0 
                secondVolume = secondVolume / secondVolumeAddCount if secondVolumeAddCount != 0 else 0 
                ratio = (firstVolume - secondVolume) / secondVolume if secondVolume != 0 else 0
                return ratio * 100
            

#平均行业上涨股数量
def GetIndustry_Up_Stock_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    addCount = 0
    totalCount = 0
    fullDataList = handler.totalDateList
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            singleCount =  GetIndustry_Up_Count(industryInfo, day, handler)
            totalCount += singleCount
            addCount += 1
            #print(f" 日期：{day}, 行业：{industryInfo.industryName}, 上涨股数量：{count}")
        dayCount = dayCount + 1
        if dayCount >= ToDayCount  or dayCount >= len(fullDataList) - 1:
            return totalCount / addCount if addCount > 0 else 0
#平均行业下跌股数量
def GetIndustry_Down_Stock_Window(industryInfo :"CalculationDataStruct.StructIndustryInfoClass", trade_date, StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    dayCount = 0
    addCount = 0
    totalCount = 0
    fullDataList = handler.totalDateList
    for day in fullDataList:
        if dayCount >= StartDayCount and dayCount < ToDayCount:
            singleCount =  GetIndustry_Down_Count(industryInfo, day, handler)
            totalCount += singleCount
            addCount += 1
            #print(f" 日期：{day}, 行业：{industryInfo.industryName}, 下跌股数量：{count}")
        dayCount = dayCount + 1
        if dayCount >= ToDayCount  or dayCount >= len(fullDataList) - 1:
            return totalCount / addCount if addCount > 0 else 0
