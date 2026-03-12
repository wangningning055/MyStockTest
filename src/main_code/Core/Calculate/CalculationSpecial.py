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

    #正式计算：
    #如果整个区间换手率低于1% 且平均涨跌幅低于2%，或平均振幅小于2 那支撑价就是区间的平均均价
    #否则进行下面的计算：
    #收盘价跌到十日均价 - ATR（14日）以下，且跌幅超过五日平均振幅，且累积跌幅超过 3% 且连续两天收跌：认为是开始回调
    #然后从开始回调开始，到收盘价在十日均价以上为止，找到这个日期区间的最低点，这一天就是股价低点
    #如此遍历区间，获得一个低点价位的列表，遍历列表，剔除低点当日振幅超过三倍的20日平均振幅的低点
    #寻找近5个支撑位，如果有三个支撑位几乎相同（差别在1%以内），支撑价直接就是这个价，否则按下面的算支撑位
    # 再遍历剩余列表计算这些低点价位的平均涨跌幅（涨跌幅限制在5个点以内，防止主升浪影响），按这个涨跌幅算出下一个支撑位低点的价格，
    #最后判断今天和昨天是否跌破支撑位或者处在支撑位
    todayStr  = nowData.trade_date
    stockCode = nowData.code

    # 获取区间窗口统计数据（StructBaseWindowClass，含均值/极值等聚合字段）
    windowData: CalculationDataStruct.StructBaseWindowClass = handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)

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
    for tempLog in dataList_asc:
        print(f"下压力位计算：准备计算的天数遍历：{tempLog.trade_date}， 长度：{len(dataList_asc)}")
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

    # ------------------------------------------------------------------ #
    # 1. 判断是否为"低波动区间"——若是则直接用区间均价作为支撑位
    #    条件：整个区间换手率 < 1% 且平均涨跌幅绝对值 < 2%，
    #          或者平均振幅 < 2
    # ------------------------------------------------------------------ #
    avg_turn_window   = windowData.avg_turn              # 区间平均换手率（%）
    avg_change_window = abs(windowData.avg_change_Ratio) # 区间平均涨跌幅绝对值（%）
    avg_amp_window    = windowData.avg_amplitude         # 区间平均振幅（%）
    avg_price_window  = windowData.avg_avg               # 区间平均均价

    is_low_volatility = (
        (avg_turn_window < 1.0 and avg_change_window < 2.0)
        or (avg_amp_window < 2.0)
    )

    if is_low_volatility:
        # 低波动区间，直接以区间均价作为支撑位
        support_price    = avg_price_window
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
    #def calc_atr(asc_seq, period=14):
    #    """在升序序列上计算末端 ATR(period)，自动跳过停牌日"""
    #    tr_list = []
    #    for i in range(1, len(asc_seq)):
    #        cur  = asc_seq[i]
    #        prev = asc_seq[i - 1]
    #        if cur.trade_state != 1 or prev.trade_state != 1:
    #            continue  # 跳过停牌日
    #        tr = max(
    #            cur.high - cur.low,
    #            abs(cur.high - prev.close),
    #            abs(cur.low  - prev.close)
    #        )
    #        tr_list.append(tr)
    #    if len(tr_list) < period:
    #        return None
    #    return sum(tr_list[-period:]) / period  # 最近 period 条 TR 的均值
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

    #atr_14 = calc_atr(dataList_asc, period=14)
    #if atr_14 is None:
    #    # 兜底：振幅（%）× 昨收估算绝对波幅
    #    atr_14 = nowData.amplitude * nowData.last_close / 100
    
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
                if count > num:
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
        #tr_list = []
        #for i in range(1, len(asc_seq)):
        #    cur  = asc_seq[i]
        #    prev = asc_seq[i - 1]
        #    if cur.trade_state != 1 or prev.trade_state != 1:
        #        continue  # 跳过停牌日
        #    tr = max(
        #        cur.high - cur.low,
        #        abs(cur.high - prev.close),
        #        abs(cur.low  - prev.close)
        #    )
        #    tr_list.append(tr)
        #if len(tr_list) < period:
        #    return None
        #return sum(tr_list[-period:]) / period  # 最近 period 条 TR 的均值
    # ------------------------------------------------------------------ #
    # 3. 遍历升序序列，识别回调区间并提取每次回调最低收盘价（低点）
    #
    #    回调触发条件（四项同时满足）：
    #      a) 收盘价 < 五日均价 - ATR(14)
    #      b) 当日跌幅绝对值 > 五日平均振幅
    #      c) 近5日最高收盘至今累积跌幅 > 3%
    #      d) 连续两天收跌（今天和昨天 change_Ratio 均 < 0）
    #
    #    触发后向后找收盘重新站上十日均价的位置作为回调结束，
    #    该区间内收盘最低的一天即为"低点"。
    # ------------------------------------------------------------------ #
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
        # ---- a) 收盘价跌破 五日均价 - ATR ----
        atr_14 = calc_atr(cur.trade_date, 14)
        ma5_cur = calc_avg(cur.trade_date, 5)
        if not ma5_cur:
            i += 1
            continue
        cond_a = cur.close < (ma5_cur - atr_14)
        #print(f"    判断1中：{cur.trade_date}    {cur.close}   {ma5_cur - atr_14}   {ma5_cur}   {atr_14}")
        # ---- b) 当日跌幅绝对值 > 五日平均振幅 ----
        amplitude_5 = calc_amplitude(cur.trade_date, 5)
        amp5_cur = amplitude_5 if amplitude_5 else avg_amp_window
        cond_b   = cur.change_Ratio < 0 and abs(cur.change_Ratio) > amp5_cur
        #print(f"    判断2中：{cur.trade_date}    {cur.change_Ratio}  {amp5_cur} ")

        # ---- c) 近5日（不含今日）最高收盘到今日累积跌幅 > 3% ----
        change_Ratio = calc_changeRatio(cur.trade_date, 3)
        cond_c = change_Ratio < 5 and prev.change_Ratio < 0 and cur.change_Ratio < 0
        #print(f"    判断3中：{cur.trade_date}    {change_Ratio} ")

        # ---- d) 连续两天收跌 ----
        #cond_d = (cur.change_Ratio < 0) and (prev.change_Ratio < 0)

        if not (cond_a or cond_b or cond_c):
            print(f"判断未通过：{cur.trade_date}   a:{cond_a}，b： {cond_b},c: {cond_c} ")
            i += 1
            continue
        else:
            print(f"判断通过：{cur.trade_date}, 这一天回调开始, a:{cond_a}，b： {cond_b},c {cond_c}")

        # ---- 向后找回调区间最低收盘价 ----
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
            # 更新区间最低收盘
            if day_j.close < low_price_in_pullback.close and day_j.is_down_stop == 0:
                low_price_in_pullback = day_j
            
            # 收盘回到回调点 或者 当前收盘价涨幅相对于最低点大于 5%
            isTwoUp = pre_day_j.change_Ratio > 0 and day_j.change_Ratio > 0
            isBack = day_j.close >= start_pullback_price
            isUp_5 = (day_j.close - low_price_in_pullback.close) / low_price_in_pullback.close > 0.05 
            low_num += 1
            print(f"{day_j.trade_date}  正在低谷, {day_j.close} ")
            if (isBack or isUp_5) and low_num > 3:
                print(f"{day_j.trade_date}  回调结束， 最低价是：{low_price_in_pullback.close}, 所属日期是：{low_price_in_pullback.trade_date}, 回调时长{low_num} ")
                rebound_idx = j
                break
            j += 1

        # 若一直未反弹，以数据末尾作为回调结束
        if rebound_idx is None:
            rebound_idx = n - 1
        #print(f"下压力位第一次计算：正在加入低点：日期是：{cur.trade_date}，  价格是：{cur.close}")
        low_points.append(low_price_in_pullback)

        # 跳过已处理区间，避免重复识别同一段回调
        i = rebound_idx + 1
    
    
    if len(low_points) <= 1:
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
        
    # ------------------------------------------------------------------ #
    # 4. 剔除异常低点
    #    低点前三日振幅 > 区间平均振幅的三倍 的低点视为异常（如闪崩）
    #    低点前三日涨跌幅 <  -20
    
            #cur_change = calc_changeRatio(day_j.trade_date, 3) > -18

    # ------------------------------------------------------------------ #
    filtered_low_points = []
    for lp in low_points:
        for single in nowData.dataList_240:
            if single.trade_date == lp.trade_date:
                ampTarget = calc_amplitude(single.trade_date, 3)
                changeRationTarget = calc_changeRatio(single.trade_date, 3)
                if ampTarget < (windowData.avg_amplitude) * 3 and changeRationTarget > -20:
                    filtered_low_points.append(lp)



    low_points = filtered_low_points

    # 若无有效低点，兜底用区间最低价
    if not low_points:
        support_price   = windowData.min_low
        yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close
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
        print(f"下压力位日期是{tempLog.trade_date},  {tempLog.close}")

    avg_fix_add = 0
    avg_fix_add2 = 0
    for single in nowData.dataList_240:
        avg_fix_add +=1
        if single.trade_date == low_points[len(low_points) - 1].trade_date:
            break
    for single in nowData.dataList_240:
        avg_fix_add2 +=1
        if avg_fix_add2 >= avg_fix_add / 2:
            low_points.append(single)
            break

    print(f"下压力位第三次过滤完毕，长度是{len(low_points)}")
    for tempLog in low_points:
        print(f"下压力位日期是{tempLog.trade_date},  {tempLog.close}")

    # ------------------------------------------------------------------ #
    # 5. 计算支撑位
    #
    #    取 low_points 末尾最近5个低点（时间最近）：
    #      - 若 ≥3 个价格彼此差距 ≤ 1% → 簇均值直接作为支撑位
    #      - 否则 → 计算相邻低点间涨跌幅（限 ±5%），
    #               取均值后从最后一个低点外推下一支撑位
    # ------------------------------------------------------------------ #
    # low_points 按时间升序，末尾为最近低点
    support_price = 0
    support_type = ""
    if len(low_points) <= 3:
        #直接计算
        last_low = 0
        totalChangeRatio = 0
        addCount = 0
        for single in low_points:
            if last_low == 0:
                last_low = single.close
            else:
                change = (single.close - last_low) / last_low
                if change > 5:
                    change = 5
                if change < -5:
                    change = -5
                totalChangeRatio += change
                addCount += 1
                last_low = single.close

        finalChangeRatio = totalChangeRatio / addCount
        if(finalChangeRatio > 0.03):
            finalChangeRatio = 0.03
        if(finalChangeRatio < -0.03):
            finalChangeRatio = -0.03

        finalTarget = last_low + last_low * finalChangeRatio

        print(f"支撑位少于3个，最后的支撑位是：{finalTarget},  {last_low}      {totalChangeRatio / addCount}")
    else:
        recent_5 = []
        count = 0
        for single in low_points:
            recent_5.append(single.close)
            count += 1
            if count >= 5:
                break

        def find_cluster(prices, threshold=0.01):
            """寻找 prices 中 ≥3 个价格彼此差距 ≤ threshold 的簇，返回簇均值；无则返回 None"""
            for base in prices:
                if base == 0:
                    continue
                cluster = [p for p in prices if abs(p - base) / base <= threshold]
                if len(cluster) >= 3:
                    return sum(cluster) / len(cluster)
            return None

        cluster_price = find_cluster(recent_5, threshold=0.01)

        if cluster_price is not None:
            # 多个低点密集聚合，直接用簇均值
            support_price = cluster_price
            support_type  = "近5低点聚集支撑（≥3个低点价格密集，取簇均值）"
            print(f"支撑位大于3个，近五个支撑点有支撑点经过了多次承压，支撑位结果是：{support_price}")
        else:
            #直接计算
            last_low = 0
            totalChangeRatio = 0
            addCount = 0
            for single in low_points:
                if last_low == 0:
                    last_low = single.close
                else:
                    change = (single.close - last_low) / last_low
                    if change > 5:
                        change = 5
                    if change < -5:
                        change = -5
                    totalChangeRatio += change
                    addCount += 1
                    last_low = single.close
            finalChangeRatio = totalChangeRatio / addCount
            if(finalChangeRatio > 0.03):
                finalChangeRatio = 0.03
            if(finalChangeRatio < -0.03):
                finalChangeRatio = -0.03
            finalTarget = last_low + last_low * finalChangeRatio
            support_price = finalTarget
            print(f"支撑位大于3个，支撑点有涨跌，预测的支撑结果是：{support_price}   {last_low},     {totalChangeRatio / addCount}")
            support_type  = (
                f"趋势推算支撑（共{len(low_points)}个低点，"
                f"平均低点涨跌幅{finalTarget:.2f}%）"
            )

    # ------------------------------------------------------------------ #
    # 6. 判断今日与昨日是否跌破支撑位，或处于支撑位附近（±1%以内）
    #    今天 = raw_list[0] = nowData
    #    昨天 = raw_list[1]
    # ------------------------------------------------------------------ #
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
    """
    计算股票上压力位（阻力位），并判断今日/昨日是否突破或接近压力位。

    与 CalculateDownPressure 完全对称：
      下压力位 → 识别"回调低点"列表 → 推算支撑价
      上压力位 → 识别"反弹高点"列表 → 推算阻力价

    参数说明：
        nowData       : 当日数据（StructBaseClass）
                        nowData.dataList_240 为最近240天日线列表，
                        [0] = 今天，[1] = 昨天，索引越大日期越早
        StartDayCount : 回溯区间起始天数（从今天往前数，如 60）
        ToDayCount    : 回溯区间结束天数（通常为 0，即截止到今天）
        handler       : 数据处理器，用于获取窗口统计数据

    返回值（dict）：
        pressure_price        : 最终计算出的压力价格，None 表示无法计算
        is_break_pressure     : 今日收盘是否向上突破压力位（bool）
        is_near_pressure      : 今日收盘是否处于压力位附近（±1%以内）（bool）
        yesterday_break       : 昨日收盘是否向上突破压力位（bool）
        pressure_type         : 压力位计算方式说明（str）
    """

    todayStr  = nowData.trade_date
    stockCode = nowData.code

    # 获取区间窗口统计数据（StructBaseWindowClass，含均值/极值等聚合字段）
    windowData: CalculationDataStruct.StructBaseWindowClass = \
        handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)

    # ------------------------------------------------------------------ #
    # 0. 准备历史日线升序序列
    #    raw_list = nowData.dataList_240：[0]=今天，[1]=昨天，索引越大越早
    #    截取所需天数后反转为升序 dataList_asc：[0]=最早，[-1]=今天
    # ------------------------------------------------------------------ #
    raw_list: list["CalculationDataStruct.StructBaseClass"] = nowData.dataList_240

    # 截取 StartDayCount+1 条（今天 + 往前N天），不超过实际数据长度
    use_count    = min(StartDayCount + 1, len(raw_list))
    # raw_list[:use_count] => [今天, 昨天, ..., 最早]，反转后升序
    dataList_asc = list(reversed(raw_list[:use_count]))

    # 数据量不足时直接返回空结果
    if len(dataList_asc) < 15:
        return {
            "pressure_price":    None,
            "is_break_pressure": False,
            "is_near_pressure":  False,
            "yesterday_break":   False,
            "pressure_type":     "数据不足"
        }

    # ------------------------------------------------------------------ #
    # 1. 判断是否为"低波动区间"——若是则直接用区间均价作为压力位
    #    与下压力位逻辑相同：低波动时价格在均价附近震荡，
    #    均价既是支撑也是压力。
    #    条件：整个区间换手率 < 1% 且平均涨跌幅绝对值 < 2%，
    #          或者平均振幅 < 2
    # ------------------------------------------------------------------ #
    avg_turn_window   = windowData.avg_turn              # 区间平均换手率（%）
    avg_change_window = abs(windowData.avg_change_Ratio) # 区间平均涨跌幅绝对值（%）
    avg_amp_window    = windowData.avg_amplitude         # 区间平均振幅（%）
    avg_price_window  = windowData.avg_avg               # 区间平均均价

    is_low_volatility = (
        (avg_turn_window < 1.0 and avg_change_window < 2.0)
        or (avg_amp_window < 2.0)
    )

    if is_low_volatility:
        # 低波动区间，直接以区间均价作为压力位
        pressure_price    = avg_price_window
        pressure_type     = "低波动区间均价压力"
        # 今日收盘高于压力位 → 视为向上突破
        is_break_pressure = nowData.close > pressure_price
        is_near_pressure  = abs(nowData.close - pressure_price) / pressure_price <= 0.01
        # 昨天 = raw_list[1]
        yesterday_break   = (raw_list[1].close > pressure_price) if len(raw_list) >= 2 else False
        return {
            "pressure_price":    pressure_price,
            "is_break_pressure": is_break_pressure,
            "is_near_pressure":  is_near_pressure,
            "yesterday_break":   yesterday_break,
            "pressure_type":     pressure_type
        }

    # ------------------------------------------------------------------ #
    # 2. 计算 ATR（14日平均真实波幅）——与下压力位完全相同
    #    TR  = max(当日最高-当日最低, |当日最高-昨日收盘|, |当日最低-昨日收盘|)
    #    ATR = TR 的 14 日简单移动平均（取末端最近14条TR）
    # ------------------------------------------------------------------ #
    def calc_atr(asc_seq, period=14):
        """在升序序列上计算末端 ATR(period)，自动跳过停牌日"""
        tr_list = []
        for i in range(1, len(asc_seq)):
            cur  = asc_seq[i]
            prev = asc_seq[i - 1]
            if cur.trade_state != 1 or prev.trade_state != 1:
                continue  # 跳过停牌日
            tr = max(
                cur.high - cur.low,
                abs(cur.high - prev.close),
                abs(cur.low  - prev.close)
            )
            tr_list.append(tr)
        if len(tr_list) < period:
            return None
        return sum(tr_list[-period:]) / period  # 最近 period 条 TR 的均值

    atr_14 = calc_atr(dataList_asc, period=14)
    if atr_14 is None:
        # 兜底：振幅（%）× 昨收估算绝对波幅
        atr_14 = nowData.amplitude * nowData.last_close / 100

    # ------------------------------------------------------------------ #
    # 3. 遍历升序序列，识别反弹区间并提取每次反弹的最高收盘价（高点）
    #
    #    【与下压力位完全对称，方向相反】
    #    下压力位：收盘跌破 MA10 - ATR → 识别回调 → 找最低收盘（低点）
    #    上压力位：收盘涨破 MA10 + ATR → 识别反弹 → 找最高收盘（高点）
    #
    #    反弹触发条件（四项同时满足）：
    #      a) 收盘价 > 十日均价 + ATR(14)          ← 对称：< MA10 - ATR
    #      b) 当日涨幅绝对值 > 五日平均振幅         ← 对称：跌幅绝对值 > 五日均振幅
    #      c) 近5日最低收盘至今累积涨幅 > 3%        ← 对称：最高收盘至今累积跌幅 > 3%
    #      d) 连续两天收涨（change_Ratio 均 > 0）   ← 对称：连续两天收跌
    #
    #    触发后向后找收盘重新跌回十日均价以下的位置作为反弹结束，
    #    该区间内收盘最高的一天即为"高点"。
    # ------------------------------------------------------------------ #
    high_points = []  # 按时间升序记录每次反弹的高点价格

    n = len(dataList_asc)
    i = 2  # 至少需要 i-1（昨天）判断连续两天收涨

    while i < n:
        cur  = dataList_asc[i]      # 当天
        prev = dataList_asc[i - 1]  # 昨天

        # 跳过停牌日
        if cur.trade_state != 1:
            i += 1
            continue

        # ---- a) 收盘价突破 十日均价 + ATR（对称：跌破 MA10 - ATR）----
        ma10_cur = cur.avg_10
        if not ma10_cur:
            i += 1
            continue
        cond_a = cur.close > (ma10_cur + atr_14)

        # ---- b) 当日涨幅绝对值 > 五日平均振幅（对称：跌幅绝对值 > 五日均振幅）----
        amp5_cur = cur.amplitude_5 if cur.amplitude_5 else avg_amp_window
        cond_b   = abs(cur.change_Ratio) > amp5_cur

        # ---- c) 近5日（不含今日）最低收盘到今日累积涨幅 > 3%
        #         （对称：最高收盘到今日累积跌幅 > 3%）----
        look_back        = min(5, i)
        recent_low_close = min(d.close for d in dataList_asc[i - look_back: i])
        cum_rise         = (cur.close - recent_low_close) / recent_low_close * 100
        cond_c           = cum_rise > 3.0

        # ---- d) 连续两天收涨（对称：连续两天收跌）----
        cond_d = (cur.change_Ratio > 0) and (prev.change_Ratio > 0)

        if not (cond_a and cond_b and cond_c and cond_d):
            i += 1
            continue

        # ---- 向后找反弹区间最高收盘价 ----
        # 从触发当天开始向后滑动，直到收盘重新跌回十日均价以下（反弹结束）
        # （对称：下压力位是收盘重新站上十日均价 → 回调结束）
        high_price_in_rally = cur.close
        pullback_idx        = None

        j = i + 1
        while j < n:
            day_j = dataList_asc[j]
            if day_j.trade_state != 1:
                j += 1
                continue
            # 更新区间最高收盘（对称：更新最低收盘）
            if day_j.close > high_price_in_rally:
                high_price_in_rally = day_j.close
            # 收盘跌回十日均价以下，反弹结束（对称：收盘站上十日均价 → 回调结束）
            ma10_j = day_j.avg_10
            if ma10_j and day_j.close < ma10_j:
                pullback_idx = j
                break
            j += 1

        # 若一直未回落，以数据末尾作为反弹结束
        if pullback_idx is None:
            pullback_idx = n - 1

        high_points.append(high_price_in_rally)

        # 跳过已处理区间，避免重复识别同一段反弹
        i = pullback_idx + 1

    # ------------------------------------------------------------------ #
    # 4. 剔除异常高点
    #    高点当日振幅 > 20日平均振幅 × 3 的高点视为异常（如暴拉/巨量冲高）予以剔除
    #    （对称：下压力位剔除闪崩低点）
    # ------------------------------------------------------------------ #
    filtered_high_points = []
    for hp in high_points:
        # 在升序序列中找收盘价与高点最接近的交易日
        match_day = min(
            (d for d in dataList_asc if d.trade_state == 1),
            key=lambda d: abs(d.close - hp),
            default=None
        )
        if match_day is None:
            filtered_high_points.append(hp)
            continue
        # 用该日20日平均振幅作为基准（amplitude_10兜底用区间均值）
        amp20_ref = match_day.amplitude_10 if match_day.amplitude_10 else avg_amp_window
        if match_day.amplitude <= amp20_ref * 3:
            filtered_high_points.append(hp)

    high_points = filtered_high_points

    # 若无有效高点，兜底用区间最高价（对称：下压力位兜底用区间最低价）
    if not high_points:
        pressure_price  = windowData.max_high
        yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close
        return {
            "pressure_price":    pressure_price,
            "is_break_pressure": nowData.close > pressure_price,
            "is_near_pressure":  abs(nowData.close - pressure_price) / pressure_price <= 0.01,
            "yesterday_break":   yesterday_close > pressure_price,
            "pressure_type":     "无有效高点，使用区间最高价"
        }

    # ------------------------------------------------------------------ #
    # 5. 计算压力位
    #    与下压力位完全对称，取近5个高点：
    #      - 若 ≥3 个价格彼此差距 ≤ 1% → 簇均值直接作为压力位
    #      - 否则 → 计算相邻高点间涨跌幅（限 ±5%），
    #               取均值后从最后一个高点外推下一压力位
    # ------------------------------------------------------------------ #
    # high_points 按时间升序，末尾为最近高点
    recent_5 = high_points[-5:] if len(high_points) >= 5 else high_points[:]

    def find_cluster(prices, threshold=0.01):
        """寻找 prices 中 ≥3 个价格彼此差距 ≤ threshold 的簇，返回簇均值；无则返回 None"""
        for base in prices:
            if base == 0:
                continue
            cluster = [p for p in prices if abs(p - base) / base <= threshold]
            if len(cluster) >= 3:
                return sum(cluster) / len(cluster)
        return None

    cluster_price = find_cluster(recent_5, threshold=0.01)

    if cluster_price is not None:
        # 多个高点密集聚合，直接用簇均值作为压力位
        pressure_price = cluster_price
        pressure_type  = "近5高点聚集压力（≥3个高点价格密集，取簇均值）"
    else:
        # 计算相邻高点间涨跌幅，限制 ±5% 防止主升浪/主跌浪干扰
        # （对称：下压力位用相邻低点涨跌幅推算下一支撑）
        pct_changes = []
        for k in range(1, len(high_points)):
            prev_hp = high_points[k - 1]
            cur_hp  = high_points[k]
            if prev_hp == 0:
                continue
            pct = (cur_hp - prev_hp) / prev_hp * 100
            pct = max(-5.0, min(5.0, pct))  # 截断到 ±5%
            pct_changes.append(pct)

        avg_pct_change = sum(pct_changes) / len(pct_changes) if pct_changes else 0.0

        # 从最后一个高点按均值涨跌幅外推下一压力位
        last_high      = high_points[-1]
        pressure_price = last_high * (1 + avg_pct_change / 100)
        pressure_type  = (
            f"趋势推算压力（共{len(high_points)}个高点，"
            f"平均高点涨跌幅{avg_pct_change:.2f}%）"
        )

    # ------------------------------------------------------------------ #
    # 6. 判断今日与昨日是否向上突破压力位，或处于压力位附近（±1%以内）
    #    今天收盘 > 压力位 → 向上突破（对称：今天收盘 < 支撑位 → 跌破）
    #    今天 = raw_list[0] = nowData
    #    昨天 = raw_list[1]
    # ------------------------------------------------------------------ #
    yesterday_close = raw_list[1].close if len(raw_list) >= 2 else nowData.close

    if pressure_price and pressure_price > 0:
        is_break_pressure = nowData.close > pressure_price   # 今日向上突破压力位
        is_near_pressure  = abs(nowData.close - pressure_price) / pressure_price <= 0.01
        yesterday_break   = yesterday_close > pressure_price  # 昨日是否已突破压力位
    else:
        is_break_pressure = False
        is_near_pressure  = False
        yesterday_break   = False

    return {
        "pressure_price":    round(pressure_price, 3) if pressure_price else None,
        "is_break_pressure": is_break_pressure,   # 今日收盘是否向上突破压力位
        "is_near_pressure":  is_near_pressure,    # 今日收盘是否在压力位附近（±1%）
        "yesterday_break":   yesterday_break,     # 昨日收盘是否向上突破压力位
        "pressure_type":     pressure_type        # 压力位计算方式说明
    }





#计算是否处在行业上涨周期，用于板块轮动买入判断


#计算是否是套娃周期的低点，用于长期震荡周期买入判断
#计算是否是套娃周期的高点，用于长期震荡周期卖出判断



#计算是否价值股，用于长线买入判断



#计算是否成长股，用于长线买入判断







#这两个后续考虑吧

#计算是否是M顶图形， 下行M为卖出判断，上行M为买入判断


#计算是否是W低图形， 上行W为买入判断，下行W为卖出判断