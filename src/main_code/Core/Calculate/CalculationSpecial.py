#这里的计算方法是主要因子，其他的都是配合的次要因子
# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING
# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core.Calculate import CalculationDataHandle
    from src.main_code.Core.DataStruct.Base import CalculationDataStruct

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
def CalculateDownPressure(nowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    #压力位计算  当日数据为 nowData， 区间数据为windowData
    #提前说明：ATR的计算：
    # TR = max(
        #当日最高 - 当日最低,
        #abs(当日最高 - 昨日收盘),
        #abs(当日最低 - 昨日收盘)
    #)
    #ATR = TR 的 14 日平均

    todayStr  = nowData.trade_date
    stockCode = nowData.code

    # 获取区间窗口统计数据（StructBaseWindowClass，含均值/极值等聚合字段）
    windowData: CalculationDataStruct.StructBaseWindowClass = handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)
    if nowData == None or windowData == None:
        return None
    print(f"___________________________________开始计算：{stockCode}——————————————————————————————————————————————————————")
    # ------------------------------------------------------------------ #
    # 0. 准备历史日线序列
    #    raw_list = nowData.dataList_240：[0]=今天，[1]=昨天，索引越大越早
    #    为便于时序遍历，截取所需天数后反转为升序：dataList_asc[-1]=今天，[0]=最早
    # ------------------------------------------------------------------ #
    raw_list: list["CalculationDataStruct.StructBaseClass"] = nowData.dataList_240

    # 截取 StartDayCount+1 条（今天 + 往前N天），不超过实际数据长度
    use_count    = min(ToDayCount + 1, len(raw_list))
    # raw_list[:use_count] => [今天, 昨天, ..., 最早]，反转后升序
    dataList_asc = list(reversed(raw_list[:use_count]))
    #for tempLog in dataList_asc:
    #    print(f"下压力位计算：准备计算的天数遍历：{tempLog.trade_date}， 长度：{len(dataList_asc)}")
    # 数据量不足时直接返回空结果
    if len(dataList_asc) < 15:
        print("下压力位计算：数据不足")
        return {
            "support_price":    None,
            "is_break_support": False,
            "is_near_support":  False,
            "yesterday_break":  False,
            "support_type":     "数据不足"
        }

    avg_turn_window   = windowData.avg_turn              # 区间平均换手率（%）
    avg_change_window = abs(windowData.avg_change_Ratio) # 区间平均涨跌幅绝对值（%）
    avg_amp_window    = windowData.avg_amplitude         # 区间平均振幅（%）
    avg_price_window  = windowData.avg_avg               # 区间平均均价
    avg_change_total_window = abs(windowData.change_Ratio_Total)
    is_low_volatility = (
        (avg_change_total_window < 3 and  avg_turn_window < 1.0 and avg_change_window < 2.0)
        or (avg_amp_window < 1.0)
    )

    if is_low_volatility:
        # 低波动区间，直接以区间均价作为支撑位
        support_price    = avg_price_window + avg_price_window * windowData.change_Ratio_Total
        support_type     = "低波动区间均价支撑"
        is_break_support = nowData.close < support_price
        is_near_support  = abs(nowData.close - support_price) / support_price <= avg_change_window
        # 昨天 = raw_list[1]
        yesterday_break  = (raw_list[1].close < support_price) if len(raw_list) >= 2 else False
        print(f"下压力位计算：这是一个低波动：当日价是{nowData.close}，支撑价是：{support_price}，  是否处在支撑价下：{is_break_support}， 是否接近支撑价：{is_near_support}")
        return {
            "support_price":    support_price,
            "is_break_support": is_break_support,
            "is_near_support":  is_near_support,
            "yesterday_break":  yesterday_break,
            "support_type":     support_type
        }

    # ------------------------------------------------------------------ #
    # 2. 计算 ATR（14日平均真实波幅）
    #    TR  = max(当日最高-当日最低, |当日最高-昨日收盘|, |当日最低-昨日收盘|)
    #    ATR = TR 的 14 日简单移动平均（取末端最近14条TR）
    #    dataList_asc 升序：asc[i-1]=前一天，asc[i]=当天
    # ------------------------------------------------------------------ #
    #计算这个日期的前x日的均价
    def calc_avg(trade_date, num = 5):
        count = 0
        totalVal = 0
        for single in nowData.dataList_240:
            if trade_date == single.trade_date or count > 0:
                count = count + 1
                totalVal += single.close
                if count >= num:
                    return totalVal / count
        return windowData.avg_close

    
    #计算这个日期距前x日的涨跌幅
    def calc_changeRatio(trade_date, num = 5):
        count = 0
        nowVal = 0
        for single in nowData.dataList_240:
            if trade_date == single.trade_date:
                nowVal = single.close
            if nowVal != 0:
                count += 1
                if count > num:
                    endVal = single.close
                    return (nowVal - endVal) * 100 / endVal
        return windowData.avg_change_Ratio
    #计算这个日期附件x天的平均振幅
    def calc_amplitude(trade_date, num = 5):
        count = 0
        nowVal = 0
        for single in nowData.dataList_240:
            if trade_date == single.trade_date or count > 0:
                nowVal += single.amplitude
                count += 1
                if count >= num:
                    return nowVal/ count
        return windowData.avg_amplitude
    
    # TR = max(
        #当日最高 - 当日最低,
        #abs(当日最高 - 昨日收盘),
        #abs(当日最低 - 昨日收盘)
    #)
    #ATR = TR 的 14 日平均
    def calc_atr(trade_date, num = 14):
        tr = 0
        count = 0
        for single in nowData.dataList_240:
            if trade_date == single.trade_date or count > 0:
                maxtarget = max(
                    single.high - single.low,
                    abs(single.high - single.last_close),
                    abs(single.low - single.last_close)
                )
                tr += maxtarget
                count += 1
                if count >= num:
                    return tr / count
        return windowData.avg_amplitude * windowData.avg_close / 100

    low_points : list["CalculationDataStruct.StructBaseClass"] = []  # 按时间升序记录每次回调的低点价格

    n = len(dataList_asc)
    i = 1  # 至少需要 i-1（昨天）判断连续两天收跌
    while i < n:
        cur  = dataList_asc[i]      # 当天
        prev = dataList_asc[i - 1]  # 昨天

        # 跳过停牌日
        if cur.trade_state != 1:
            i += 1
            continue
        atr_14 = calc_atr(cur.trade_date, 14)
        ma5_cur = calc_avg(cur.trade_date, 5)
        if not ma5_cur:
            i += 1
            continue
        cond_a = cur.close < (ma5_cur - atr_14)
        #print(f"    判断1中：{cur.trade_date}    {cur.close}   {ma5_cur - atr_14}   {ma5_cur}   {atr_14}")
        amplitude_5 = calc_amplitude(cur.trade_date, 5)
        amp5_cur = amplitude_5 if amplitude_5 else avg_amp_window
        cond_b   = cur.change_Ratio < -3 and abs(cur.change_Ratio) > amp5_cur
        #print(f"    判断2中：{cur.trade_date}    {cur.change_Ratio}  {amp5_cur} ")

        change_Ratio = calc_changeRatio(cur.trade_date, 3)
        cond_c = change_Ratio < -3 and prev.change_Ratio < 0 and cur.change_Ratio < 0
        #print(f"    判断3中：{cur.trade_date}    {change_Ratio} ")

        if not (cond_a or cond_b or cond_c):
            #print(f"判断未通过：{cur.trade_date}   a:{cond_a}，b： {cond_b},c: {cond_c} ")
            i += 1
            continue
        else:
            pass
            #print(f"判断通过：{cur.trade_date}, 这一天回调开始, a:{cond_a}，b： {cond_b},c {cond_c}")

        low_price_in_pullback = cur
        rebound_idx = None
        start_pullback_price = cur.close
        j = i + 1
        low_num = 0
        while j < n:
            day_j = dataList_asc[j]
            pre_day_j = dataList_asc[j - 1]
            if day_j.trade_state != 1:
                j += 1
                continue
            if day_j.close < low_price_in_pullback.close and day_j.is_down_stop == 0:
                low_price_in_pullback = day_j
            
            isTwoUp = pre_day_j.change_Ratio > 0 and day_j.change_Ratio > 0
            isBack = day_j.close >= start_pullback_price
            isUp_5 = (day_j.close - low_price_in_pullback.close) / low_price_in_pullback.close > 0.05 
            low_num += 1
            #print(f"{day_j.trade_date}  正在低谷, {day_j.close} ")
            if (isBack or isUp_5) and low_num > 4:
                #print(f"{day_j.trade_date}  回调结束， 最低价是：{low_price_in_pullback.close}, 所属日期是：{low_price_in_pullback.trade_date}, 回调时长{low_num} ")
                rebound_idx = j
                break
            j += 1

        if rebound_idx is None:
            break
        #print(f"下压力位第一次计算：正在加入低点：日期是：{cur.trade_date}，  价格是：{cur.close}")
        low_points.append(low_price_in_pullback)

        # 跳过已处理区间，避免重复识别同一段回调
        i = rebound_idx + 1
    
    
    if len(low_points) <= 0:
        # 低波动区间，直接以区间均价作为支撑位
        support_price    = avg_price_window
        support_type     = "低波动区间均价支撑"
        is_break_support = nowData.close < support_price
        is_near_support  = abs(nowData.close - support_price) / support_price <= avg_change_window
        # 昨天 = raw_list[1]
        yesterday_break  = (raw_list[1].close < support_price) if len(raw_list) >= 2 else False
        print(f"下压力位计算：这是一个一直维持一个趋势的的：当日价是{nowData.close}，支撑价是：{support_price}，  是否处在支撑价下：{is_break_support}， 是否接近支撑价：{is_near_support}")
        return {
            "support_price":    support_price,
            "is_break_support": is_break_support,
            "is_near_support":  is_near_support,
            "yesterday_break":  yesterday_break,
            "support_type":     support_type
        }
    print(f"下压力位第一次计算完毕，长度是{len(low_points)}")
    for tempLog in low_points:
        print(f"下压力位日期是{tempLog.trade_date}")
        

    filtered_low_points = []
    for lp in low_points:
        i = 0
        for single in nowData.dataList_240:
            if single.trade_date == lp.trade_date:
                ampTarget = calc_amplitude(single.trade_date, 4)
                changeRationTarget = calc_changeRatio(single.trade_date, 3)
                isExtra = False
                if i <= len(nowData.dataList_240) - 2:
                    isExtra = changeRationTarget < -8 and nowData.dataList_240[i+1].change_Ratio > 8
                    
                else:
                    isExtra = changeRationTarget < -13


                print(f"尝试过滤极端回调点：{ single.trade_date},  {ampTarget}   {(windowData.avg_amplitude) * 2}      {isExtra}")
                if ampTarget < (windowData.avg_amplitude) * 2 and isExtra == False:
                    filtered_low_points.append(lp)
            i+=1



    low_points = filtered_low_points

    if not low_points or len(low_points) <= 0:
        support_price   = windowData.avg_avg +  windowData.avg_avg * windowData.change_Ratio_Total / 100
        yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close
        print(f"低点全被过滤完了，直接用区间均价乘区间整体涨跌幅,预测的支撑结果是:{support_price}")
        return {
            "support_price":    support_price,
            "is_break_support": nowData.close < support_price,
            "is_near_support":  abs(nowData.close - support_price) / support_price <= 0.01,
            "yesterday_break":  yesterday_close < support_price,
            "support_type":     "无有效低点，使用区间最低价"
        }
    #low_points.reverse()
    print(f"下压力位第二次过滤完毕，长度是{len(low_points)}")
    for tempLog in low_points:
        print(f"下压力位日期是{tempLog.trade_date},  {tempLog.avg}")

    near_avg = 0
    avg_fix_add = 0
    for single in nowData.dataList_240:
        near_avg += single.avg
        avg_fix_add +=1
        if single.trade_date == low_points[len(low_points) - 1].trade_date:
            if avg_fix_add >= 5:
                near_avg = single.close + (nowData.close - single.close) / 2
            else:
                near_avg = 0
            break

    print(f"下压力位第三次过滤完毕，最近的回调均价是：{near_avg}")

    if len(low_points) == 1:
        low = low_points[0].avg
        if near_avg != 0:
            low = low + (near_avg - low) / 2
        support_price   = low
        yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close
        print(f"低点只剩一个，直接用低点 + 回调价, 预测的支撑结果是:{support_price}")
        return {
            "support_price":    support_price,
            "is_break_support": nowData.close < support_price,
            "is_near_support":  abs(nowData.close - support_price) / support_price <= 0.01,
            "yesterday_break":  yesterday_close < support_price,
            "support_type":     "无有效低点，使用区间最低价"
        }

    support_price = 0
    support_type = ""
    if len(low_points) == 2:
        #直接计算
        last_low = 0
        totalChangeRatio = 0
        addCount = 0

        preLow = low_points[0].avg
        recent_low = low_points[1].avg
        change_ratio_2 = (recent_low - preLow) / preLow
        if change_ratio_2 > 0.02:
            change_ratio_2 = 0.02
        if change_ratio_2 < -0.02:
            change_ratio_2 = -0.02

        targetLow = recent_low
        if near_avg != 0:
            targetLow = recent_low + recent_low * change_ratio_2
            targetLow = targetLow + (near_avg - targetLow) / 2
        else:
            targetLow = recent_low
        finalTarget = targetLow


        print(f"支撑位只有两个，最后的支撑位是：{finalTarget}")
    else:
        recent_3 = []
        count = 0
        low_points.reverse()
        for single in low_points:
            recent_3.append(single.close)
            count += 1
            if count >= 3:
                break

        def find_cluster(prices, threshold=0.02):
            """寻找 prices 中 ≥2 个价格彼此差距 ≤ threshold 的簇，返回簇均值；无则返回 None"""
            for base in prices:
                if base == 0:
                    continue
                cluster = [p for p in prices if abs(p - base) / base <= threshold]
                if len(cluster) >= 2:
                    return sum(cluster) / len(cluster)
            return None
        
        cluster_price = find_cluster(recent_3, threshold=0.02)
        low_points.reverse()
        
        if cluster_price is not None:
            # 多个低点密集聚合，直接用簇均值
            support_price = cluster_price
            support_type  = "近5低点聚集支撑（≥3个低点价格密集，取簇均值）"
            print(f"支撑位大于3个，近五个支撑点有支撑点经过了2次及以上承压，支撑位结果是：{support_price}")
        else:
            #直接计算
            last_low = 0
            totalChangeRatio = 0
            weight_target_total = len(low_points) - 1
            addCount = 0
            recent = low_points[len(low_points) - 1]
            totalWeight = 0
            for single in low_points:
                if last_low == 0:
                    last_low = low_points[0].avg
                else:
                    addCount += 1
                    weight = addCount / weight_target_total
                    totalChangeRatio += ((single.close - last_low) / last_low) * weight
                    totalWeight += weight
                    print(f"正在计算支撑位涨跌幅，日期是{single.trade_date}    权重是：{ weight }, 涨跌：{single.close - last_low}")
                    last_low = single.close

            totalChangeRatio = totalChangeRatio / addCount
            finalChangeRatio = totalChangeRatio * (weight_target_total / totalWeight)
            print(f"不足四个的计算完毕：权重总和：{totalWeight}, 目标总和：{weight_target_total}， 映射因子为：{weight_target_total/totalWeight},涨跌幅：{totalChangeRatio}")
            if(finalChangeRatio > 0.02):
                finalChangeRatio = 0.02
            if(finalChangeRatio < -0.02):
                finalChangeRatio = -0.02

            targetLow = recent.close + recent.close * finalChangeRatio
            if near_avg != 0:
                targetLow = targetLow + (near_avg - targetLow) / 2

            print(f"最近的回调价：{near_avg}")
            support_price = targetLow
            print(f"支撑位大于2个，支撑点有涨跌，预测的支撑结果是：{support_price}  最近的支撑位日期： {recent.trade_date},  最近的支撑位： {recent.close},   最后的涨跌幅  {finalChangeRatio}")
            support_type  = (
                f"趋势推算支撑（共{len(low_points)}个低点，"
            )


    yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close

    if support_price and support_price > 0:
        is_break_support = nowData.close < support_price
        is_near_support  = abs(nowData.close - support_price) / support_price <= 0.01
        yesterday_break  = yesterday_close < support_price
    else:
        is_break_support = False
        is_near_support  = False
        yesterday_break  = False

    return {
        "support_price":    round(support_price, 3) if support_price else None,
        "is_break_support": is_break_support,   # 今日收盘是否跌破支撑位
        "is_near_support":  is_near_support,    # 今日收盘是否在支撑位附近（±1%）
        "yesterday_break":  yesterday_break,    # 昨日收盘是否跌破支撑位
        "support_type":     support_type        # 支撑位计算方式说明
    }



#计算上压力位，用于买在趋势突破的判断
def CalculateUpPressure(nowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
    pass




#计算是否处在行业上涨周期，用于板块轮动买入判断


#计算是否是套娃周期的低点，用于长期震荡周期买入判断
#计算是否是套娃周期的高点，用于长期震荡周期卖出判断



#计算是否价值股，用于长线买入判断



#计算是否成长股，用于长线买入判断







#这两个后续考虑吧

#计算是否是M顶图形， 下行M为卖出判断，上行M为买入判断


#计算是否是W低图形， 上行W为买入判断，下行W为卖出判断