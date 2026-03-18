#这里的计算方法是主要因子，其他的都是配合的次要因子
# 1. 先导入TYPE_CHECKING常量
from typing import List, Optional, Callable, Dict, Any, Union,Tuple  
from typing import TYPE_CHECKING
# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core.Calculate import CalculationDataHandle
    from src.main_code.Core.DataStruct.Base import CalculationDataStruct
    from src.main_code.Core import Main

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
# ══════════════════════════════════════════════════════════════════
    # 下压力位（支撑位）计算   nowData=当日数据   windowData=区间聚合数据
    #
    # ATR 计算说明：
    #   TR  = max(当日最高-当日最低, |当日最高-昨收|, |当日最低-昨收|)
    #   ATR = TR 的 14 日均值
    #
    # 本版新增（其余逻辑与原版完全一致）：
    #   1. 所有边界参数统一提到最前方，方便直接修改
    #   2. 每个低点叠加成交量密集度权重：附近换手越密集说明筹码承接越真实
    #   3. 时间权重与成交量权重合并：时间越近 + 量越密集 = 权重越高
    #      （权重仅作用于 3个及以上低点 的加权趋势计算，
    #        原有的1个/2个低点分支、聚合检测逻辑均保持不变）
    # ══════════════════════════════════════════════════════════════════

    # ----------------------------------------------------------------
    # ★ 可调边界参数（统一放在最前方，方便直接修改）
    # ----------------------------------------------------------------

    # 【低波动判定】区间整体涨跌幅低于此值（%），配合换手率/振幅判定为低波动票
    PARAM_LOW_VOL_TOTAL_CHANGE      = 3.0
    # 【低波动判定】区间平均换手率低于此值（%）时参与低波动判定
    PARAM_LOW_VOL_AVG_TURN          = 1.0
    # 【低波动判定】区间平均涨跌幅低于此值（%）时参与低波动判定
    PARAM_LOW_VOL_AVG_CHANGE        = 2.0
    # 【低波动判定】区间平均振幅低于此值（%）时直接判定为低波动
    PARAM_LOW_VOL_AMP               = 1.0

    # 【回调启动条件A】收盘价低于 MA5 - ATR * 此系数，视为下破启动
    PARAM_BREAKDOWN_ATR_FACTOR      = 0.8
    # 【回调启动条件B】单日跌幅绝对值超过此值（%）且超过近5日平均振幅，视为强势下杀
    PARAM_SINGLE_DAY_DOWN_RATIO     = 3.0
    # 【回调启动条件C】3日累计跌幅超过此值（%）且连续两日收跌，视为持续下行趋势
    PARAM_3DAY_DOWN_RATIO           = 3.0

    # 【回调结束】从本段低点反弹超过此比例，视为回调结束（原版固定5%）
    PARAM_REBOUND_END_RATIO         = 0.05
    # 【回调结束】最少持续交易日数，不足此数不结束（防止一日假反弹）
    PARAM_MIN_PULLBACK_DAYS         = 2

    # 【极端点过滤】3日跌幅绝对值超过此值（%）且次日涨幅超过下方阈值，视为恐慌性抛盘
    PARAM_EXTREME_3DAY_DOWN         = 10.0
    # 【极端点过滤】次日涨幅超过此值（%），配合上方阈值判定异常反包
    PARAM_EXTREME_NEXT_UP           = 10.0
    # 【极端点过滤】数据末尾孤立点：3日跌幅绝对值超过此值（%）直接视为异常
    PARAM_EXTREME_TAIL_DOWN         = 15.0
    # 【极端点过滤】低点附近平均振幅超过区间均值 * 此倍数，视为异常波动
    PARAM_EXTREME_AMP_FACTOR        = 2

    # 【near_avg 修正】最近低点距今至少 N 日才做均价修正（太近修正意义不大）
    PARAM_NEAR_AVG_MIN_DAYS         = 5

    # 【趋势推算】相邻低点涨跌幅上下限（防止外推过度）
    PARAM_TREND_RATIO_CAP           = 0.03

    # 【成交量密集度】计算低点附近成交量密集度时，取该点起向后 N 日
    PARAM_VOL_DENSE_WINDOW          = 5
    # 【成交量密集度】附近均量超过区间均量 * 此倍数，视为量密集（承接更真实）
    PARAM_VOL_DENSE_FACTOR          = 1.5
    # 【成交量密集度权重上限】量密集时额外权重最大加成倍数（防止单点异常放量主导结果）
    PARAM_VOL_WEIGHT_MAX            = 2.0

    # 【时间权重】最新低点时间权重最大值（线性递减到最早点为 1.0）
    PARAM_TIME_WEIGHT_MAX           = 3.0

    # ----------------------------------------------------------------
    # 初始化
    # ----------------------------------------------------------------
    todayStr  = nowData.trade_date
    stockCode = nowData.code

    # 获取区间窗口统计数据（StructBaseWindowClass，含均值/极值等聚合字段）
    windowData: CalculationDataStruct.StructBaseWindowClass = handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)
    if nowData == None or windowData == None:
        return None
    print(f"___________________________________开始计算：{stockCode}——————————————————————————————————————————————————————")

    raw_list: list["CalculationDataStruct.StructBaseClass"] = nowData.dataList_240

    use_count    = min(ToDayCount + 1, len(raw_list))
    dataList_asc = list(reversed(raw_list[:use_count]))

    if len(dataList_asc) < 15:
        print("下压力位计算：数据不足,直接返回平均均价下降平均涨跌幅")
        return windowData.avg_low - windowData.avg_low * abs(windowData.change_Ratio_Total)

    avg_turn_window         = windowData.avg_turn              # 区间平均换手率（%）
    avg_change_window       = abs(windowData.avg_change_Ratio) # 区间平均涨跌幅绝对值（%）
    avg_amp_window          = windowData.avg_amplitude         # 区间平均振幅（%）
    avg_price_window        = windowData.avg_avg               # 区间平均均价
    avg_low_price_window        = windowData.avg_low               # 区间平均最低价
    avg_vol_window          = windowData.avg_volume            # 区间日均成交量，用于密集度对比
    avg_change_total_window = abs(windowData.change_Ratio_Total)

    is_low_volatility = (
        (avg_change_total_window < PARAM_LOW_VOL_TOTAL_CHANGE
         and avg_turn_window     < PARAM_LOW_VOL_AVG_TURN
         and avg_change_window   < PARAM_LOW_VOL_AVG_CHANGE)
        or (avg_amp_window < PARAM_LOW_VOL_AMP)
    )

    if is_low_volatility:
        support_price = avg_low_price_window - avg_low_price_window * abs(windowData.change_Ratio_Total) / 100
        print(f"下压力位计算：这是一个低波动：当日价是{nowData.close}，支撑价是：{support_price}，  ")
        return support_price

    # ----------------------------------------------------------------
    # 辅助函数（逻辑与原版完全一致）
    # ----------------------------------------------------------------

    # 计算这个日期的前x日的均价
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

    # 计算这个日期距前x日的涨跌幅
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

    # 计算这个日期附近x天的平均振幅
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

    def calc_vol_dense(trade_date, window=PARAM_VOL_DENSE_WINDOW):
        """
        计算 trade_date 起向后 window 日的平均成交量。
        返回值 / avg_vol_window 即为密集度倍数：
          > PARAM_VOL_DENSE_FACTOR 表示该低点附近筹码承接密集，支撑更真实
        """
        if avg_vol_window <= 0:
            return avg_vol_window
        count, total = 0, 0.0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date or count > 0:
                total += s.volume
                count += 1
                if count >= window:
                    return total / count
        return avg_vol_window

    # ----------------------------------------------------------------
    # 第一步：识别每段回调的低点（逻辑与原版完全一致）
    # ----------------------------------------------------------------
    low_points : list["CalculationDataStruct.StructBaseClass"] = []  # 按时间升序记录每次回调的低点价格

    n = len(dataList_asc)
    i = 1
    while i < n:
        cur  = dataList_asc[i]      # 当天
        prev = dataList_asc[i - 1]  # 昨天

        # 跳过停牌日
        if cur.trade_state != 1:
            i += 1
            continue

        atr_14  = calc_atr(cur.trade_date, 14)
        ma5_cur = calc_avg(cur.trade_date, 5)
        if not ma5_cur:
            i += 1
            continue

        cond_a = cur.close < (ma5_cur - PARAM_BREAKDOWN_ATR_FACTOR * atr_14)

        amplitude_5 = calc_amplitude(cur.trade_date, 5)
        amp5_cur    = amplitude_5 if amplitude_5 else avg_amp_window
        cond_b      = cur.change_Ratio < -PARAM_SINGLE_DAY_DOWN_RATIO and abs(cur.change_Ratio) > amp5_cur

        change_Ratio = calc_changeRatio(cur.trade_date, 3)
        cond_c = change_Ratio < -PARAM_3DAY_DOWN_RATIO and prev.change_Ratio < 0 and cur.change_Ratio < 0

        if not (cond_a or cond_b or cond_c):
            i += 1
            continue
        else:
            print(f"         下压力位开始调整的日期为：{cur.trade_date}:{cond_a}   {cond_b }    {cond_c}")


        low_price_in_pullback = cur
        rebound_idx           = None
        start_pullback_price  = cur.close
        j       = i + 1
        low_num = 0

        while j < n:
            day_j = dataList_asc[j]
            if day_j.trade_state != 1:
                j += 1
                continue

            if day_j.close < low_price_in_pullback.close and day_j.is_down_stop == 0:
                low_price_in_pullback = day_j

            isBack = day_j.close >= start_pullback_price
            isUp_5 = (day_j.close - low_price_in_pullback.close) / low_price_in_pullback.close > PARAM_REBOUND_END_RATIO
            isUpTwo = day_j.change_Ratio > 0 and dataList_asc[j - 1].change_Ratio > 0
            low_num += 1
            #是否接近最近的日期
            isClose = (n - j) <= 3
            if ((isBack or isUp_5) and low_num > PARAM_MIN_PULLBACK_DAYS and isUpTwo) or isClose:
                rebound_idx = j
                break
            j += 1

        if rebound_idx is None:
            break

        low_points.append(low_price_in_pullback)

        # 跳过已处理区间，避免重复识别同一段回调
        i = rebound_idx + 1

    # ----------------------------------------------------------------
    # 无低点：说明区间内单边趋势，用均价 - 整体涨跌幅兜底（原版逻辑）
    # ----------------------------------------------------------------
    if len(low_points) <= 0:
        support_price = avg_low_price_window - avg_low_price_window * abs(windowData.change_Ratio_Total) / 100
        print(f"下压力位计算：这是一个一直维持一个趋势的的：当日价是{nowData.close}，支撑价是：{support_price}，  ")
        return support_price

    print(f"下压力位第一次计算完毕，长度是{len(low_points)}")
    for tempLog in low_points:
        print(f"下压力位日期是{tempLog.trade_date}")

    # ----------------------------------------------------------------
    # 第二步：过滤恐慌性抛盘造成的虚假低点（逻辑与原版完全一致）
    #   3日跌幅过大 且 次日暴力反包 → 恐慌性抛盘 → 非真实支撑 → 过滤
    # ----------------------------------------------------------------
    filtered_low_points = []
    for lp in low_points:
        i = 0
        for single in nowData.dataList_240:
            if single.trade_date == lp.trade_date:
                ampTarget          = calc_amplitude(single.trade_date, 2)
                changeRationTarget = calc_changeRatio(single.trade_date, 3)
                isExtra = False
                if i <= len(nowData.dataList_240) - 2:
                    isExtra = (changeRationTarget < -PARAM_EXTREME_3DAY_DOWN
                               and nowData.dataList_240[i+1].change_Ratio > PARAM_EXTREME_NEXT_UP)
                else:
                    isExtra = changeRationTarget < -PARAM_EXTREME_TAIL_DOWN

                print(f"尝试过滤极端回调点：{ single.trade_date},  {ampTarget}   {(windowData.avg_amplitude) * PARAM_EXTREME_AMP_FACTOR}      {isExtra}")
                if ampTarget < (windowData.avg_amplitude) * PARAM_EXTREME_AMP_FACTOR and isExtra == False:
                    filtered_low_points.append(lp)
            i += 1
    i = 1
    need_Remove = []
    while i < len(filtered_low_points):
        day_new = filtered_low_points[i]
        day_old = filtered_low_points[i - 1]
        day_space = 0
        for single in nowData.dataList_240:
            if single.trade_date == day_new.trade_date or day_space != 0:
                day_space += 1
            if single.trade_date == day_old.trade_date:
                if day_space <= 5:
                    need_Remove.append(day_old)
                day_space = 0
                break
        i = i+1

    for day in need_Remove:
        filtered_low_points.remove(day)

    low_points = filtered_low_points

    if not low_points or len(low_points) <= 0:
        support_price = windowData.avg_low - windowData.avg_low * abs(windowData.change_Ratio_Total) / 100
        print(f"低点全被过滤完了，直接用区间均价乘区间整体涨跌幅,预测的支撑结果是:{support_price}")
        return support_price

    print(f"下压力位第二次过滤完毕，长度是{len(low_points)}")
    for tempLog in low_points:
        print(f"下压力位日期是{tempLog.trade_date},  {tempLog.avg}")

    # ----------------------------------------------------------------
    # 第三步：near_avg 修正（逻辑与原版完全一致）
    # ----------------------------------------------------------------
    near_avg    = 0
    avg_fix_add = 0
    for single in nowData.dataList_240:
        avg_fix_add += 1
        if single.trade_date == low_points[len(low_points) - 1].trade_date:
            if avg_fix_add >= PARAM_NEAR_AVG_MIN_DAYS:
                near_avg = single.avg + (nowData.avg - single.avg) / 2
            else:
                near_avg = 0
            break

    print(f"下压力位第三次过滤完毕，最近的回调均价是：{near_avg}")

    # ----------------------------------------------------------------
    # 辅助：计算单个低点的综合权重
    #   综合权重 = 时间权重 × 成交量密集度权重
    #
    #   时间权重：最新低点 = PARAM_TIME_WEIGHT_MAX，线性递减到最早 = 1.0
    #     时间越近的低点对未来支撑的参考价值越高
    #
    #   成交量密集度权重：低点附近均量 / 区间均量
    #     密集度超过 PARAM_VOL_DENSE_FACTOR 倍才加权，上限 PARAM_VOL_WEIGHT_MAX
    #     低点附近成交量越大，说明该价位有大量筹码承接，支撑越真实
    # ----------------------------------------------------------------
    def calc_point_weight(lp, time_rank, total_points):
        """
        time_rank:    该低点在时间升序中的排名（0=最早，total_points-1=最新）
        total_points: 低点总数
        """
        time_w = time_rank / total_points

        # 成交量密集度权重
        vol_near  = calc_vol_dense(lp.trade_date, PARAM_VOL_DENSE_WINDOW)
        vol_ratio = vol_near / avg_vol_window if avg_vol_window > 0 else 1.0
        # 超过密集阈值才加权，上限防止异常放量单点主导整体结果
        vol_w     = min(max(vol_ratio, 1.0), PARAM_VOL_WEIGHT_MAX) if vol_ratio >= PARAM_VOL_DENSE_FACTOR else 1.0

        combined  = time_w * vol_w
        print(f"  权重计算：{lp.trade_date}  时间权重={time_w:.2f}  量密集度={vol_ratio:.2f}  量权重={vol_w:.2f}  综合={combined:.2f}")
        return combined

    total_lp = len(low_points)

    # ----------------------------------------------------------------
    # 第四步：按低点数量分支计算支撑位
    # ----------------------------------------------------------------

    # —— 仅1个低点（逻辑与原版完全一致）——
    if total_lp == 1:
        low = low_points[0].avg
        if near_avg != 0:
            low = low + (near_avg - low) / 2
        support_price = low
        print(f"低点只剩一个，直接用低点 + 回调价, 预测的支撑结果是:{support_price}")
        return support_price

    support_price = 0
    support_type  = ""

    # —— 2个低点（逻辑与原版完全一致）——
    if total_lp == 2:
        preLow     = low_points[0].avg
        recent_low = low_points[1].avg
        change_ratio_2 = (recent_low - preLow) / preLow
        if change_ratio_2 > PARAM_TREND_RATIO_CAP:
            change_ratio_2 = PARAM_TREND_RATIO_CAP
        if change_ratio_2 < -PARAM_TREND_RATIO_CAP:
            change_ratio_2 = -PARAM_TREND_RATIO_CAP

        targetLow = recent_low
        if near_avg != 0:
            targetLow = recent_low + recent_low * change_ratio_2
            targetLow = targetLow + (near_avg - targetLow) / 2
        else:
            targetLow = recent_low
        support_price = targetLow

        print(f"支撑位只有两个，最后的支撑位是：{support_price}")
        return support_price

    # —— 3个及以上低点 ——
    else:
        recent_3 = []
        count = 0
        low_points.reverse()
        for single in low_points:
            recent_3.append(single.avg)
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
                    return cluster[-1]
            return None

        cluster_price = find_cluster(recent_3, threshold=0.01)
        low_points.reverse()

        # 近3个低点密集聚合：说明该价位多次获得有效承接，是强支撑区（原版逻辑）
        if cluster_price is not None:
            support_price = cluster_price
            if near_avg != 0:
                support_price + (near_avg - support_price) / 2
            print(f"支撑位大于3个，近3个支撑点有支撑点经过了2次及以上承压，支撑位结果是：{support_price}")
            return support_price

        else:
            # ★ 趋势推算：原版使用固定递增权重（addCount / weight_target_total）
            #   本版改为综合权重（时间权重 × 成交量密集度权重），其余计算结构不变
            last_low            = 0
            totalChangeRatio    = 0
            weight_target_total = total_lp - 1
            addCount            = 0
            recent              = low_points[total_lp - 1]
            totalWeight         = 0

            for rank, single in enumerate(low_points):
                if last_low == 0:
                    last_low = low_points[0].avg
                else:
                    addCount += 1
                    # ★ 综合权重替换原版的 addCount / weight_target_total
                    weight            = calc_point_weight(single, addCount, weight_target_total)
                    totalChangeRatio += ((single.close - last_low) / last_low) * weight
                    totalWeight      += weight
                    print(f"正在计算支撑位涨跌幅，日期是{single.trade_date}    权重是：{ weight }, 涨跌：{single.close - last_low}")
                    last_low = single.close

            totalChangeRatio = totalChangeRatio / addCount
            finalChangeRatio = totalChangeRatio * (weight_target_total / totalWeight)
            print(f"不足四个的计算完毕：权重总和：{totalWeight}, 目标总和：{weight_target_total}， 映射因子为：{weight_target_total/totalWeight},涨跌幅：{totalChangeRatio}")

            if finalChangeRatio > PARAM_TREND_RATIO_CAP:
                finalChangeRatio = PARAM_TREND_RATIO_CAP
            if finalChangeRatio < -PARAM_TREND_RATIO_CAP:
                finalChangeRatio = -PARAM_TREND_RATIO_CAP

            targetLow = recent.close + recent.close * finalChangeRatio
            if near_avg != 0:
                targetLow = targetLow + (near_avg - targetLow) / 2

            print(f"最近的回调价：{near_avg}")
            support_price = targetLow
            print(f"支撑位大于2个，支撑点有涨跌，预测的支撑结果是：{support_price}  最近的支撑位日期： {recent.trade_date},  最近的支撑位： {recent.close},   最后的涨跌幅  {finalChangeRatio}")
            support_type  = (
                f"趋势推算支撑（共{total_lp}个低点，"
            )

    return support_price





#计算上压力位，用于买在趋势突破的判断
def CalculateUpPressure(nowData:"CalculationDataStruct.StructBaseClass", StartDayCount, ToDayCount, handler:"CalculationDataHandle.BaseClass"):
# ══════════════════════════════════════════════════════════════════
    # 上压力位计算   nowData=当日数据   windowData=区间聚合数据
    #
    # ATR 计算说明：
    #   TR  = max(当日最高-当日最低, |当日最高-昨收|, |当日最低-昨收|)
    #   ATR = TR 的 14 日均值
    #
    # 与下支撑位的核心差异（市场非对称性修正）：
    #   1. 涨停日【保留】更新高点——涨停本身就是当日最强压力体现
    #   2. 反弹结束阈值从 5% 改为 ATR 动态阈值，避免把正常洗盘误判为反弹结束
    #   3. near_avg 修正加方向判断：当前价低于高点时不向下拉低压力位
    #   4. 震荡市下权重正负交替时退化为简单均值，避免预测值乱跳
    #   5. 每个高点叠加成交量密集度权重（越密集抛压越真实）
    #   6. 时间权重与成交量权重合并计算，时间越近 + 量越密集 = 权重越高
    # ══════════════════════════════════════════════════════════════════

    # ----------------------------------------------------------------
    # ★ 可调边界参数（统一放在最前方，方便直接修改）
    # ----------------------------------------------------------------

    # 【低波动判定】区间整体涨跌幅低于此值（%），配合换手率/振幅判定为低波动票
    PARAM_LOW_VOL_TOTAL_CHANGE      = 3.0
    # 【低波动判定】区间平均换手率低于此值（%）时参与低波动判定
    PARAM_LOW_VOL_AVG_TURN          = 1.0
    # 【低波动判定】区间平均涨跌幅低于此值（%）时参与低波动判定
    PARAM_LOW_VOL_AVG_CHANGE        = 2.0
    # 【低波动判定】区间平均振幅低于此值（%）时直接判定为低波动
    PARAM_LOW_VOL_AMP               = 1.0

    # 【反弹启动条件A】收盘价超过 MA5 + ATR * 此系数，视为突破启动
    PARAM_BREAKOUT_ATR_FACTOR       = 0.8
    # 【反弹启动条件B】单日涨幅超过此值（%）且超过近5日平均振幅，视为强势拉升
    PARAM_SINGLE_DAY_UP_RATIO       = 3.0
    # 【反弹启动条件C】3日累计涨幅超过此值（%）且连续两日收涨，视为持续上攻
    PARAM_3DAY_UP_RATIO             = 3.0

    # 【反弹结束】从本段高点回落超过 ATR * 此系数，视为反弹结束（动态阈值，替代固定5%）
    PARAM_PULLBACK_END_ATR_FACTOR   = 1.5
    # 【反弹结束】最少持续交易日数，不足此数不结束（防止一日假回落）
    PARAM_MIN_REBOUND_DAYS          = 2

    # 【极端点过滤】3日涨幅超过此值（%）且次日跌幅超过下方阈值，视为情绪性抢筹
    PARAM_EXTREME_3DAY_UP           = 10.0
    # 【极端点过滤】次日跌幅绝对值超过此值（%），配合上方阈值判定异常
    PARAM_EXTREME_NEXT_DOWN         = 10.0
    # 【极端点过滤】数据末尾孤立点：3日涨幅超过此值（%）直接视为异常
    PARAM_EXTREME_TAIL_UP           = 15.0
    # 【极端点过滤】高点附近平均振幅超过区间均值 * 此倍数，视为异常波动
    PARAM_EXTREME_AMP_FACTOR        = 2

    # 【near_avg 修正】最近高点距今至少 N 日才做均价修正（太近修正意义不大）
    PARAM_NEAR_AVG_MIN_DAYS         = 5

    # 【成交量密集度】计算高点附近成交量密集度时，前后各取 N 日
    PARAM_VOL_DENSE_WINDOW          = 5
    # 【成交量密集度】附近成交量超过区间均量 * 此倍数，视为量密集（抛压更真实）
    PARAM_VOL_DENSE_FACTOR          = 1.5
    # 【成交量密集度权重上限】量密集时额外权重最大加成倍数（防止单点量异常主导结果）
    PARAM_VOL_WEIGHT_MAX            = 2.0

    # 【时间权重】最新高点时间权重基础值（线性递减到最早点为 1.0）
    PARAM_TIME_WEIGHT_MAX           = 3.0

    # 【趋势推算】相邻高点涨跌幅上限（防止外推过度）
    PARAM_TREND_RATIO_CAP           = 0.03

    # 【震荡市退化】权重计算中正负交替次数超过此值，退化为简单均值
    PARAM_OSCILLATION_FLIP_MAX      = 2

    # ----------------------------------------------------------------
    # 初始化
    # ----------------------------------------------------------------
    todayStr  = nowData.trade_date
    stockCode = nowData.code

    windowData: CalculationDataStruct.StructBaseWindowClass = handler.GetWindowDataClass(stockCode, todayStr, StartDayCount, ToDayCount)
    if nowData is None or windowData is None:
        return None

    print(f"___________________________________开始计算：{stockCode}——————————————————————————————————————————————————————")

    raw_list: list["CalculationDataStruct.StructBaseClass"] = nowData.dataList_240
    use_count    = min(ToDayCount + 1, len(raw_list))
    dataList_asc = list(reversed(raw_list[:use_count]))  # 转为时间升序

    if len(dataList_asc) < 15:
        print("上压力位计算：数据不足，直接返回平均均价上涨平均涨跌幅")
        return windowData.avg_high + windowData.avg_high * abs(windowData.change_Ratio_Total) / 100

    avg_turn_window         = windowData.avg_turn
    avg_change_window       = abs(windowData.avg_change_Ratio)
    avg_amp_window          = windowData.avg_amplitude
    avg_price_window        = windowData.avg_high
    avg_vol_window          = windowData.avg_volume   # 区间日均成交量，用于密集度对比
    avg_change_total_window = abs(windowData.change_Ratio_Total)

    # 低波动判定：波动极小的票直接用均价 + 区间整体涨跌幅估算
    is_low_volatility = (
        (avg_change_total_window < PARAM_LOW_VOL_TOTAL_CHANGE
         and avg_turn_window     < PARAM_LOW_VOL_AVG_TURN
         and avg_change_window   < PARAM_LOW_VOL_AVG_CHANGE)
        or (avg_amp_window < PARAM_LOW_VOL_AMP)
    )
    if is_low_volatility:
        resistance_price = avg_price_window + avg_price_window * avg_change_total_window / 100
        print(f"上压力位：低波动票，当日价={nowData.close}，阻力价={resistance_price}")
        return resistance_price

    # ----------------------------------------------------------------
    # 辅助函数
    # ----------------------------------------------------------------

    def calc_avg(trade_date, num=5):
        """计算 trade_date 起向后 num 日的收盘均价（MA）"""
        count, total = 0, 0.0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date or count > 0:
                count += 1
                total += s.close
                if count >= num:
                    return total / count
        return windowData.avg_close

    def calc_changeRatio(trade_date, num=5):
        """计算 trade_date 相对于其前 num 日收盘的涨跌幅（%）"""
        count, nowVal = 0, 0.0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date:
                nowVal = s.close
            if nowVal != 0:
                count += 1
                if count > num:
                    return (nowVal - s.close) * 100 / s.close
        return windowData.avg_change_Ratio

    def calc_amplitude(trade_date, num=5):
        """计算 trade_date 起向后 num 日的平均振幅（%）"""
        count, total = 0, 0.0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date or count > 0:
                total += s.amplitude
                count += 1
                if count >= num:
                    return total / count
        return windowData.avg_amplitude

    def calc_atr(trade_date, num=14):
        """计算 trade_date 起向后 num 日的 ATR"""
        tr, count = 0.0, 0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date or count > 0:
                tr += max(
                    s.high - s.low,
                    abs(s.high - s.last_close),
                    abs(s.low  - s.last_close)
                )
                count += 1
                if count >= num:
                    return tr / count
        return avg_amp_window * windowData.avg_close / 100

    def calc_vol_dense(trade_date, window=PARAM_VOL_DENSE_WINDOW):
        """
        计算 trade_date 附近 window 日的平均成交量。
        返回值 / avg_vol_window 即为密集度倍数：
          > PARAM_VOL_DENSE_FACTOR 表示该高点附近筹码换手密集，抛压更真实
        """
        if avg_vol_window <= 0:
            return avg_vol_window
        count, total = 0, 0.0
        for s in nowData.dataList_240:
            if s.trade_date == trade_date or count > 0:
                total += s.volume
                count += 1
                if count >= window:
                    return total / count
        return avg_vol_window

    # ----------------------------------------------------------------
    # 第一步：识别每段反弹的高点
    # ----------------------------------------------------------------
    high_points: list["CalculationDataStruct.StructBaseClass"] = []

    n = len(dataList_asc)
    i = 1
    while i < n:
        cur  = dataList_asc[i]
        prev = dataList_asc[i - 1]

        if cur.trade_state != 1:   # 跳过停牌日
            i += 1
            continue

        atr_14  = calc_atr(cur.trade_date, 14)
        ma5_cur = calc_avg(cur.trade_date, 5)
        if not ma5_cur:
            i += 1
            continue

        # 条件A：收盘突破 MA5 上方超过 0.5 * ATR → 趋势性突破启动
        cond_a = cur.close > (ma5_cur + PARAM_BREAKOUT_ATR_FACTOR * atr_14)

        amp5_cur = calc_amplitude(cur.trade_date, 5) or avg_amp_window
        # 条件B：单日涨幅 > 阈值 且超过近期平均振幅 → 强势单日拉升
        cond_b = cur.change_Ratio > PARAM_SINGLE_DAY_UP_RATIO and abs(cur.change_Ratio) > amp5_cur

        change_3 = calc_changeRatio(cur.trade_date, 3)
        # 条件C：3日累计涨幅 > 阈值 且连续两日收涨 → 持续上攻趋势
        cond_c = change_3 > PARAM_3DAY_UP_RATIO and prev.change_Ratio > 0 and cur.change_Ratio > 0

        if not (cond_a or cond_b or cond_c):
            i += 1
            continue
        else:
            print(f"         上压力位开始调整的日期为：{cur.trade_date}:{cond_a}   {cond_b }    {cond_c}")

        # 追踪本段反弹，寻找高点
        high_in_rebound   = cur
        pullback_idx      = None
        start_price       = cur.close
        j                 = i + 1
        rebound_day_count = 0

        while j < n:
            day_j = dataList_asc[j]
            if day_j.trade_state != 1:
                j += 1
                continue

            # ★ 涨停日【保留】更新高点：涨停是当日最强压力体现，不应跳过
            if day_j.close > high_in_rebound.close:
                high_in_rebound = day_j

            # 反弹结束判定：
            #   1. 回落到反弹起点以下（彻底回吐）
            #   2. 从高点回落超过 ATR * 系数（动态阈值，比固定5%更合理）
            atr_j    = calc_atr(day_j.trade_date, 14)
            isBack   = day_j.close <= start_price
            isDown   = (high_in_rebound.close - day_j.close) > PARAM_PULLBACK_END_ATR_FACTOR * atr_j
            rebound_day_count += 1
            isLowTwo = day_j.change_Ratio < 0 and dataList_asc[j - 1].change_Ratio < 0
            #是否接近最近的日期
            isClose = (n - j) <= 3
            if ((isBack or isDown) and rebound_day_count > PARAM_MIN_REBOUND_DAYS and isLowTwo) or isClose:
                pullback_idx = j
                break
            j += 1

        if pullback_idx is None:
            print(f"         上压力位开始调整的日期被抛弃：{cur.trade_date}")
            break

        high_points.append(high_in_rebound)
        i = pullback_idx + 1

    # ----------------------------------------------------------------
    # 无高点：说明区间内单边趋势，用均价 + 整体涨跌幅兜底
    # ----------------------------------------------------------------
    if not high_points:
        resistance_price = avg_price_window + avg_price_window * avg_change_total_window / 100
        print(f"上压力位：区间内无明显反弹高点，当日价={nowData.close}，阻力价={resistance_price}")
        return resistance_price

    print(f"上压力位第一次识别完毕，共{len(high_points)}个高点")
    for t in high_points:
        print(f"  完全识别完后的上压力位日期={t.trade_date}")

    # ----------------------------------------------------------------
    # 第二步：过滤情绪性抢筹造成的虚假高点
    #   判定逻辑与下支撑位过滤恐慌性抛盘完全对称：
    #   暴涨后次日暴跌 → 情绪性抢筹 → 该高点不具备真实压力代表性 → 过滤
    # ----------------------------------------------------------------
    filtered_high_points = []
    for hp in high_points:
        idx = 0
        for single in nowData.dataList_240:
            if single.trade_date == hp.trade_date:
                amp_near      = calc_amplitude(single.trade_date, 2)
                change_3day   = calc_changeRatio(single.trade_date, 3)
                isExtra       = False

                if idx <= len(nowData.dataList_240) - 2:
                    # 3日涨幅过大 且 次日暴跌 → 情绪性抢筹，非真实压力
                    isExtra = (change_3day   >  PARAM_EXTREME_3DAY_UP
                               and nowData.dataList_240[idx + 1].change_Ratio < -PARAM_EXTREME_NEXT_DOWN)
                else:
                    # 数据末尾孤立点：3日涨幅极大 → 视为异常
                    isExtra = change_3day > PARAM_EXTREME_TAIL_UP

                print(f"过滤检查：{single.trade_date}  近2日振幅={amp_near:.2f}  阈值={avg_amp_window * PARAM_EXTREME_AMP_FACTOR:.2f}  极端={isExtra}")
                if amp_near < avg_amp_window * PARAM_EXTREME_AMP_FACTOR and not isExtra:
                    filtered_high_points.append(hp)
            idx += 1


    i = 1
    need_Remove = []
    while i < len(filtered_high_points):
        day_new = filtered_high_points[i]
        day_old = filtered_high_points[i - 1]
        day_space = 0
        for single in nowData.dataList_240:
            if single.trade_date == day_new.trade_date or day_space != 0:
                day_space += 1
            if single.trade_date == day_old.trade_date:
                if day_space <= 5:
                    need_Remove.append(day_old)
                day_space = 0
                break
        i += 1

    for day in need_Remove:
        filtered_high_points.remove(day)

    high_points = filtered_high_points

    if not high_points:
        resistance_price = windowData.avg_high + windowData.avg_high * avg_change_total_window / 100
        print(f"上压力位：高点全部被过滤，用区间均价兜底，阻力价={resistance_price}")
        return resistance_price

    print(f"上压力位第二次过滤完毕，共{len(high_points)}个高点")
    for t in high_points:
        print(f"  高点日期={t.trade_date}  均价={t.avg}")

    # ----------------------------------------------------------------
    # 第三步：near_avg 修正（加方向判断，避免压力位被当前弱势价格拖低）
    #   仅当当前均价 >= 最近高点均价时才做向上修正
    #   如果当前价已低于最近高点，说明价格还没到那里，不修正
    # ----------------------------------------------------------------
    near_avg    = 0
    avg_fix_add = 0
    for single in nowData.dataList_240:
        avg_fix_add += 1
        if single.trade_date == high_points[len(high_points) - 1].trade_date:
            if avg_fix_add >= PARAM_NEAR_AVG_MIN_DAYS:
                near_avg = single.avg + (nowData.avg - single.avg) / 2
            else:
                near_avg = 0
            break
    print(f"上压力位 near_avg 修正值={near_avg}（0表示不修正）")

    # ----------------------------------------------------------------
    # 第四步：计算每个高点的综合权重
    #   综合权重 = 时间权重 × 成交量密集度权重
    #
    #   时间权重：最新高点 = PARAM_TIME_WEIGHT_MAX，线性递减到最早 = 1.0
    #   成交量密集度权重：附近均量 / 区间均量，上限 PARAM_VOL_WEIGHT_MAX
    #     密集度高 → 该价位筹码换手充分 → 抛压来源真实 → 权重更高
    # ----------------------------------------------------------------
    def calc_point_weight(hp, time_rank, total_points):
        """
        time_rank:    该高点在时间升序中的排名（0=最早，total_points-1=最新）
        total_points: 高点总数
        """
        time_w = time_rank / total_points

        # 成交量密集度权重
        vol_near  = calc_vol_dense(hp.trade_date, PARAM_VOL_DENSE_WINDOW)
        if avg_vol_window > 0:
            vol_ratio = vol_near / avg_vol_window
        else:
            vol_ratio = 1.0
        # 超过密集阈值才加权，上限防止异常放量单点主导
        vol_w = min(max(vol_ratio, 1.0), PARAM_VOL_WEIGHT_MAX) if vol_ratio >= PARAM_VOL_DENSE_FACTOR else 1.0

        combined = time_w * vol_w
        print(f"  权重计算：{hp.trade_date}  时间权重={time_w:.2f}  量密集度={vol_ratio:.2f}  量权重={vol_w:.2f}  综合={combined:.2f}")
        return combined

    total_hp = len(high_points)

    # ----------------------------------------------------------------
    # 第五步：按高点数量分支计算阻力位
    # ----------------------------------------------------------------

    # —— 仅1个高点 ——
    if total_hp == 1:
        base = high_points[0].avg
        if near_avg != 0:
            base = base + (near_avg - base) / 2
        print(f"上压力位：仅1个高点，阻力价={base}")
        return base

    # —— 2个高点 ——
    if total_hp == 2:
        w0 = calc_point_weight(high_points[0], 0, 2)
        w1 = calc_point_weight(high_points[1], 1, 2)

        pre_high    = high_points[0].avg
        recent_high = high_points[1].avg
        change_r    = (recent_high - pre_high) / pre_high
        change_r    = max(min(change_r, PARAM_TREND_RATIO_CAP), -PARAM_TREND_RATIO_CAP)

        # 用权重加权两个高点均价得基础阻力，再叠加趋势外推
        base_price  = (pre_high * w0 + recent_high * w1) / (w0 + w1)
        target_high = base_price + recent_high * change_r
        if near_avg != 0:
            target_high = target_high + (near_avg - target_high) / 2

        print(f"上压力位：2个高点，阻力价={target_high}")
        return target_high

    # —— 3个及以上高点 ——

    # 先检查近3个高点是否密集聚合（≤2% 价差）→ 强阻力区，直接用加权均值
    recent_3    = list(reversed(high_points))[:3]   # 最近3个，时间降序
    recent_3_prices = [hp.avg for hp in recent_3]

    def find_cluster(prices, threshold=0.02):
        """寻找 prices 中 ≥2 个价格彼此差距 ≤ threshold 的簇，返回簇均值；无则返回 None"""
        for base in prices:
            if base == 0:
                continue
            cluster = [p for p in prices if p != 0 and abs(p - base) / base <= threshold]
            if len(cluster) >= 2:
                return cluster[-1]
        return None

    cluster_price = find_cluster(recent_3_prices, threshold=0.01)
    if cluster_price is not None:
        # 多次在同一价位受阻，是强阻力区，直接返回聚合均值（已是自然的量价加权位置）
        if near_avg != 0:
            cluster_price + (near_avg - cluster_price) / 2

        print(f"上压力位：近3高点密集聚合，强阻力区={cluster_price}")
        return cluster_price


    # ★ 趋势推算：原版使用固定递增权重（addCount / weight_target_total）
    #   本版改为综合权重（时间权重 × 成交量密集度权重），其余计算结构不变
    total_hp = len(high_points)
    last_low            = 0
    totalChangeRatio    = 0
    weight_target_total = total_hp - 1
    addCount            = 0
    recent              = high_points[total_hp - 1]
    totalWeight         = 0

    for rank, single in enumerate(high_points):
        if last_low == 0:
            last_low = high_points[0].avg
        else:
            addCount += 1
            # ★ 综合权重替换原版的 addCount / weight_target_total
            weight            = calc_point_weight(single, addCount, weight_target_total)
            totalChangeRatio += ((single.close - last_low) / last_low) * weight
            totalWeight      += weight
            print(f"正在计算支撑位涨跌幅，日期是{single.trade_date}    权重是：{ weight }, 涨跌：{single.close - last_low}")
            last_low = single.close

    totalChangeRatio = totalChangeRatio / addCount
    finalChangeRatio = totalChangeRatio * (weight_target_total / totalWeight)
    print(f"不足四个的计算完毕：权重总和：{totalWeight}, 目标总和：{weight_target_total}， 映射因子为：{weight_target_total/totalWeight},涨跌幅：{totalChangeRatio}")

    if finalChangeRatio > PARAM_TREND_RATIO_CAP:
        finalChangeRatio = PARAM_TREND_RATIO_CAP
    if finalChangeRatio < -PARAM_TREND_RATIO_CAP:
        finalChangeRatio = -PARAM_TREND_RATIO_CAP

    targetLow = recent.close + recent.close * finalChangeRatio
    if near_avg != 0:
        targetLow = targetLow + (near_avg - targetLow) / 2

    print(f"最近的回调价：{near_avg}")
    support_price = targetLow
    print(f"支撑位大于2个，支撑点有涨跌，预测的支撑结果是：{support_price}  最近的支撑位日期： {recent.trade_date},  最近的支撑位： {recent.close},   最后的涨跌幅  {finalChangeRatio}")
    support_type  = (
        f"趋势推算支撑（共{total_hp}个高点，"
    )
    return support_price






#高价值股筛选逻辑， 我需要你按下面的注释，拿着现有的字段参数，完成下面注释的逻辑，注意注释清晰明确，边界尽量都放到上面的字段中，方便设置
def CalculateValueScore(nowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    if nowData.isST == 1:
        return 0
    componyInfo = handler.totalComponyIns.GetComponyInfo(nowData.code)
    earn = nowData.earn                  # 市盈率
    clean = nowData.clean                # 市净率
    cash = nowData.cash                  # 市现率
    sale = nowData.sale                  # 市销率
    roe_year = componyInfo.Roe_Year      # 净资产收益率（年度）
    yoyni_year = componyInfo.YOYNi_Year  # 净利润同比增长率（年度）
    liabilityTo_year = componyInfo.LiabilityTo_Year  # 资产负债率（年度）
    yoyEquity_year = componyInfo.YOYEquity_Year      # 净资产同比增长率（年度）
    yoyLiability_year = componyInfo.YOYLiability_Year  # 负债同比增长率（年度）

    roe_quarter = componyInfo.Roe        # 净资产收益率（季度）
    yoyni_quarter = componyInfo.YOYNi    # 净利润同比增长率（季度）
    liabilityTo_quarter = componyInfo.LiabilityTo    # 资产负债率（季度）
    yoyEquity_quarter = componyInfo.YOYEquity        # 净资产同比增长率（季度）
    yoyLiability_quarter = componyInfo.YOYLiability  # 负债同比增长率（季度）
    value = nowData.total_value                     #总市值
    #print("=" * 50)
    #print(f"【估值指标】{nowData.code}")
    #print(f"市盈率（PE）：{earn}")
    #print(f"市净率（PB）：{clean}")
    #print(f"市现率（PCF）：{cash}")
    #print(f"市销率（PS）：{sale}")

    #print("\n【年度财务指标】")
    #print(f"净资产收益率（ROE）：{roe_year}%")
    #print(f"净利润同比增长率：{yoyni_year}%")
    #print(f"资产负债率：{liabilityTo_year}%")
    #print(f"净资产同比增长率：{yoyEquity_year}%")
    #print(f"负债同比增长率：{yoyLiability_year}%")

    #print("\n【季度财务指标】")
    #print(f"净资产收益率（ROE）：{roe_quarter}%")
    #print(f"净利润同比增长率：{yoyni_quarter}%")
    #print(f"资产负债率：{liabilityTo_quarter}%")
    #print(f"净资产同比增长率：{yoyEquity_quarter}%")
    #print(f"负债同比增长率：{yoyLiability_quarter}%")
    #print("=" * 50)

    # ==================== 一票否决边界 ====================
    veto_earn_max           = 0     # 市盈率       ≤ 此值：一票否决
    veto_cash_max           = 0     # 市现率       ≤ 此值：一票否决
    veto_clean_max          = 0     # 市净率       ≤ 此值：一票否决
    veto_roe_year_max       = 4     # 年度ROE      ≤ 此值(%): 一票否决
    veto_yoyni_year_min     = -20   # 年度净利润增长率 ≤ 此值(%): 一票否决
    veto_liability_year_max = 70    # 年度资产负债率  ≥ 此值(%): 一票否决
    total_value_min = 50            # 小盘股，一票否决

    # ==================== 打分边界 ====================
    # 市盈率（满16 半8 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 零
    earn_b1 = 18
    earn_b2 = 30

    # 市现率（满9 半4 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 零
    cash_b1 = 10
    cash_b2 = 18

    # 市销率（满5 半2 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 零
    sale_b1 = 1.5
    sale_b2 = 3

    # 市净率（满10 半5 零0）：[b1, b2] 满 | (b2, b3] 半 | 其余 零
    clean_b1 = 0.6
    clean_b2 = 2
    clean_b3 = 3

    # 年度净资产收益率（满14 半7 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    roe_year_b1 = 14
    roe_year_b2 = 8

    # 年度净利润同比增长率（满4 半2 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    yoyni_year_b1 = 5
    yoyni_year_b2 = -10

    # 年度资产负债率（满6 半3 零0）：≤b1 满 | (b1, b2] 半 | >b2 零
    liability_year_b1 = 65
    liability_year_b2 = 85

    # 年度净资产同比增长率（满3 半1 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    equity_year_b1 = 5
    equity_year_b2 = 0

    # 年度负债同比增长率（满3 半1 零0）：≤b1 满 | (b1, b2] 半 | >b2 零
    yoyliab_year_b1 = 15
    yoyliab_year_b2 = 30

    # 季度净资产收益率（满6 半3 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    roe_qtr_b1 = 2.5
    roe_qtr_b2 = 1

    # 季度净利润同比增长率（满5 半2 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    yoyni_qtr_b1 = 0
    yoyni_qtr_b2 = -10

    # 季度资产负债率（满3 半1 零0）：≤b1 满 | (b1, b2] 半 | >b2 零
    liability_qtr_b1 = 70
    liability_qtr_b2 = 90

    # 季度净资产同比增长率（满4 半2 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    equity_qtr_b1 = 3
    equity_qtr_b2 = -3

    # 季度负债同比增长率（满2 半1 零0）：≤b1 满 | (b1, b2] 半 | >b2 零
    yoyliab_qtr_b1 = 15
    yoyliab_qtr_b2 = 25

    value_b1 = 100
    value_b2 = 300
    value_b3 = 600
    value_b4 = 1000


    #市盈率 ≤0（净利润亏损，无估值可言）
    #市现率 ≤0（无真实经营现金流，纸面利润陷阱）
    #市净率 ≤0（资不抵债，退市高风险）
    #年度净资产收益率 ≤4%（盈利能力跑不赢无风险利率，看似低估实则只值这个价）
    #年度净利润同比增长率 ≤-20%（盈利出现不可逆崩盘，不是低估是基本面恶化）
    #年度资产负债率 ≥95%（接近资不抵债，极端财务风险）
    # ==================== 一票否决判断 ====================
    if earn             < veto_earn_max:           return 0
    if cash             < veto_cash_max:           return 0
    if clean            < veto_clean_max:          return 0
    if roe_year         < veto_roe_year_max:       return 0
    if yoyni_year       < veto_yoyni_year_min:     return 0
    if liabilityTo_year >= veto_liability_year_max: return 0
    if roe_quarter         < veto_roe_year_max:       return 0
    if yoyni_quarter       < veto_yoyni_year_min:     return 0
    if liabilityTo_quarter >= veto_liability_year_max: return 0

    if value            < total_value_min:          return 0
    if cash > earn * 2: return 0
    # ==================== 打分逻辑 ====================
    # 指标完全为 0 视为无数据，该指标直接得 0 分
    score = 0

    # ---------- 市盈率 ----------
    if earn == 0:               score += 0
    elif earn <= earn_b1:       score += 16
    elif earn <= earn_b2:       score += 8
    else:                       score += 0

    # ---------- 市现率 ----------
    if cash == 0:               score += 0
    elif cash <= cash_b1:       score += 9
    elif cash <= cash_b2:       score += 4
    else:                       score += 0

    # ---------- 市销率 ----------
    if sale == 0:               score += 0
    elif sale <= sale_b1:       score += 5
    elif sale <= sale_b2:       score += 2
    else:                       score += 0

    # ---------- 市净率 ----------
    if clean == 0:                              score += 0
    elif clean_b1 <= clean <= clean_b2:         score += 10
    elif clean <= clean_b3:                     score += 5
    else:                                       score += 0

    # ---------- 年度净资产收益率 ----------
    if roe_year == 0:               score += 0
    elif roe_year >= roe_year_b1:   score += 14
    elif roe_year >= roe_year_b2:   score += 7
    else:                           score += 0

    # ---------- 年度净利润同比增长率 ----------
    if yoyni_year == 0:                 score += 0
    elif yoyni_year >= yoyni_year_b1:   score += 4
    elif yoyni_year >= yoyni_year_b2:   score += 2
    else:                               score += 0
    # ---------- 年度资产负债率 ----------
    if liabilityTo_year == 0:                       score += 0
    elif liabilityTo_year <= liability_year_b1:     score += 6
    elif liabilityTo_year <= liability_year_b2:     score += 3
    else:                                           score += 0

    # ---------- 年度净资产同比增长率 ----------
    if yoyEquity_year == 0:                 score += 0
    elif yoyEquity_year >= equity_year_b1:  score += 3
    elif yoyEquity_year >= equity_year_b2:  score += 1
    else:                                   score += 0

    # ---------- 年度负债同比增长率 ----------
    if yoyLiability_year == 0:                      score += 0
    elif yoyLiability_year <= yoyliab_year_b1:      score += 3
    elif yoyLiability_year <= yoyliab_year_b2:      score += 1
    else:                                           score += 0

    # ---------- 季度净资产收益率 ----------
    if roe_quarter == 0:                score += 0
    elif roe_quarter >= roe_qtr_b1:     score += 6
    elif roe_quarter >= roe_qtr_b2:     score += 3
    else:                               score += 0

    # ---------- 季度净利润同比增长率 ----------
    if yoyni_quarter == 0:                  score += 0
    elif yoyni_quarter >= yoyni_qtr_b1:     score += 5
    elif yoyni_quarter >= yoyni_qtr_b2:     score += 2
    else:                                   score += 0

    # ---------- 季度资产负债率 ----------
    if liabilityTo_quarter == 0:                        score += 0
    elif liabilityTo_quarter <= liability_qtr_b1:       score += 3
    elif liabilityTo_quarter <= liability_qtr_b2:       score += 1
    else:                                               score += 0

    # ---------- 季度净资产同比增长率 ----------
    if yoyEquity_quarter == 0:                  score += 0
    elif yoyEquity_quarter >= equity_qtr_b1:    score += 4
    elif yoyEquity_quarter >= equity_qtr_b2:    score += 2
    else:                                       score += 0

    # ---------- 季度负债同比增长率 ----------
    if yoyLiability_quarter == 0:                       score += 0
    elif yoyLiability_quarter <= yoyliab_qtr_b1:        score += 2
    elif yoyLiability_quarter <= yoyliab_qtr_b2:        score += 1
    else:                                               score += 0



    value_b1 = 100
    value_b2 = 300
    value_b3 = 600
    value_b4 = 1000
    if value == 0:                                                score +=0
    if value < value_b1:                                          score +=5
    if value >= value_b1 and value < value_b2:                    score +=10
    if value >= value_b2 and value < value_b3 :                    score +=8
    if value >= value_b3 and value < value_b4:                    score +=7
    if value >= value_b4:                                          score +=5
    removeList = [
        "证券", 
        "银行",
        "全国地产",
        "房产服务",
        "保险"
    ]

    if removeList.__contains__(componyInfo.Industry):
        score -= 5
    return round(score, 2)

#价值股筛选打分逻辑：


#计算是否成长股，用于买入判断
def CalculateGrowScore(nowData:"CalculationDataStruct.StructBaseClass", handler:"CalculationDataHandle.BaseClass"):
    if nowData.isST == 1:
        return 0
    componyInfo = handler.totalComponyIns.GetComponyInfo(nowData.code)



    earn = nowData.earn                  # 市盈率
    clean = nowData.clean                # 市净率
    cash = nowData.cash                  # 市现率
    sale = nowData.sale                  # 市销率
    roe_year = componyInfo.Roe_Year      # 净资产收益率（年度）
    yoyni_year = componyInfo.YOYNi_Year  # 净利润同比增长率（年度）
    liabilityTo_year = componyInfo.LiabilityTo_Year  # 资产负债率（年度）
    yoyEquity_year = componyInfo.YOYEquity_Year      # 净资产同比增长率（年度）
    yoyLiability_year = componyInfo.YOYLiability_Year  # 负债同比增长率（年度）

    roe_quarter = componyInfo.Roe        # 净资产收益率（季度）
    yoyni_quarter = componyInfo.YOYNi    # 净利润同比增长率（季度）
    liabilityTo_quarter = componyInfo.LiabilityTo    # 资产负债率（季度）
    yoyEquity_quarter = componyInfo.YOYEquity        # 净资产同比增长率（季度）
    yoyLiability_quarter = componyInfo.YOYLiability  # 负债同比增长率（季度）
    value = nowData.total_value                     #总市值



    # ==================== 一票否决边界 ====================
    veto_earn_max            = 0    # 市盈率 ≤ 此值：一票否决
    veto_earn_min            = 150  # 市盈率 > 此值：一票否决（极端泡沫）
    veto_cash_max            = 0    # 市现率 ≤ 此值：一票否决
    veto_cash_pe_ratio       = 4    # 市现率 > 市盈率 × 此倍数：一票否决（伪成长）
    veto_yoyni_min           = 12   # 年度且季度净利润增长率 < 此值(%): 一票否决
    veto_roe_min             = 8    # 年度且季度ROE < 此值(%): 一票否决
    veto_liability_max       = 75   # 年度且季度资产负债率 > 此值(%): 一票否决
    veto_equity_year_min     = 0    # 年度净资产增长率 < 此值(%): 一票否决
    total_value_min = 50            # 小盘股，一票否决

    # ==================== 打分边界 ====================
    # 市盈率（满6 半3 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 或 ≤0 零
    earn_b1 = 70
    earn_b2 = 120

    # 市现率（满4 半2 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 或 ≤0 零
    cash_b1 = 32
    cash_b2 = 55

    # 市销率（满3 半1 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 零
    sale_b1 = 6
    sale_b2 = 10

    # 市净率（满2 半1 零0）：(0, b1] 满 | (b1, b2] 半 | >b2 零
    clean_b1 = 6
    clean_b2 = 8

    # 年度ROE（满7 半3 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    roe_year_b1 = 20
    roe_year_b2 = 12

    # 年度净利润增长率（满9 半4 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    yoyni_year_b1 = 40
    yoyni_year_b2 = 20

    # 年度资产负债率（满4 半2 零0）：≤b1 满 | (b1, b2] 半 | >b2 零
    liability_year_b1 = 55
    liability_year_b2 = 70

    # 年度净资产增长率（满7 半3 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    equity_year_b1 = 25
    equity_year_b2 = 15

    # 年度负债增长率（满3 半1 零0）：≤年度净资产增长率 满 | (净资产增长率, b1) 半 | ≥b1 零
    yoyliab_year_b1 = 25   # 负债增长率 ≥ 此值(%) 得 0 分

    # 季度ROE（满10 半5 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    roe_qtr_b1 = 4.5
    roe_qtr_b2 = 2.5

    # 季度净利润增长率（满19 半9 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    yoyni_qtr_b1 = 40
    yoyni_qtr_b2 = 25

    # 季度资产负债率变化（满4 半2 零0）：≤年度值或上升≤b1 满 | 上升(b1, b2] 半 | 上升>b2 零
    liability_qtr_rise_b1 = 2   # 季度较年度上升幅度(%) ≤ 此值 得满分
    liability_qtr_rise_b2 = 4   # 季度较年度上升幅度(%) ≤ 此值 得半分；> 此值 得 0 分

    # 季度净资产增长率（满14 半7 零0）：≥b1 满 | [b2, b1) 半 | <b2 零
    equity_qtr_b1 = 28
    equity_qtr_b2 = 18

    # 季度负债增长率（满4 半2 零0）：≤季度净资产增长率 满 | (净资产增长率, b1) 半 | ≥b1 零
    yoyliab_qtr_b1 = 28   # 负债增长率 ≥ 此值(%) 得 0 分


    # 市盈率 PE-TTM ≤0 或 ＞150（亏损或极端泡沫）
    # 市现率 PCF-TTM ≤0 或 PCF ＞ PE ×4（现金流严重不足，伪成长）
    # 年度或季度净利润同比增长率 ＜12%（成长失速）
    # 年度或季度 ROE ＜8%（盈利质量不足）
    # 企业年度或季度资产负债率 ＞75%（高杠杆不可持续）
    # 年度净资产同比增长率 ＜0%（股东权益萎缩）
    # ==================== 一票否决判断 ====================
    # 市盈率 ≤0 或 >150
    if earn <= veto_earn_max or earn > veto_earn_min:           return 0
    # 市现率 ≤0 或 > PE × 4（现金流严重不足，伪成长）
    if cash <= veto_cash_max or cash > earn * veto_cash_pe_ratio: return 0
    # 年度净利润增长率 < 12%
    if yoyni_year < veto_yoyni_min:                             return 0
    # 季度净利润增长率 < 12%
    if yoyni_quarter < veto_yoyni_min:                          return 0
    # 年度ROE < 8%
    if roe_year < veto_roe_min:                                 return 0
    # 季度ROE < 8%
    if roe_quarter < veto_roe_min:                              return 0
    # 年度资产负债率 > 75%
    if liabilityTo_year > veto_liability_max:                   return 0
    # 季度资产负债率 > 75%
    if liabilityTo_quarter > veto_liability_max:                return 0
    # 年度净资产增长率 < 0%
    if yoyEquity_year < veto_equity_year_min:                   return 0
    # 季度净资产增长率 < 0%
    if yoyEquity_quarter < veto_equity_year_min:                   return 0
    if value < total_value_min:                                  return 0
    
    # ==================== 打分逻辑 ====================
    # 指标完全为 0 视为无数据，该指标直接得 0 分
    score = 0

    #1 市盈率（PE）
    #0-70        得 6
    #70-110      得 3
    #>110 或 ≤0  得 0
    # ---------- 市盈率 ----------
    if earn == 0:               score += 0
    elif earn <= earn_b1:       score += 6
    elif earn <= earn_b2:       score += 3
    else:                       score += 0


    #2 市现率（PCF）
    #0-32        得 4
    #32-48       得 2
    #>48 或 ≤0   得 0
    # ---------- 市现率 ----------
    if cash == 0:               score += 0
    elif cash <= cash_b1:       score += 4
    elif cash <= cash_b2:       score += 2
    else:                       score += 0


    #3 市销率（PS）
    #0-6         得 3
    #6-9         得 1
    #>9          得 0
    # ---------- 市销率 ----------
    if sale == 0:               score += 0
    elif sale <= sale_b1:       score += 3
    elif sale <= sale_b2:       score += 1
    else:                       score += 0

    #4 市净率（PB）
    #0-6         得 2
    #6-8         得 1
    #>8          得 0
    # ---------- 市净率 ----------
    if clean == 0:              score += 0
    elif clean <= clean_b1:     score += 2
    elif clean <= clean_b2:     score += 1
    else:                       score += 0

    #5 年度ROE
    #≥20%        得 7
    #12%-20%     得 3
    #<12%        得 0
    # ---------- 年度ROE ----------
    if roe_year == 0:               score += 0
    elif roe_year >= roe_year_b1:   score += 7
    elif roe_year >= roe_year_b2:   score += 3
    else:                           score += 0


    #6 年度净利润增长率
    #≥40%        得 9
    #20%-40%     得 4
    #<20%        得 0
    # ---------- 年度净利润增长率 ----------
    if yoyni_year == 0:                 score += 0
    elif yoyni_year >= yoyni_year_b1:   score += 9
    elif yoyni_year >= yoyni_year_b2:   score += 4
    else:                               score += 0

    #7 年度资产负债率
    #≤55%        得 4
    #55%-70%     得 2
    #>70%        得 0
    # ---------- 年度资产负债率 ----------
    if liabilityTo_year == 0:                       score += 0
    elif liabilityTo_year <= liability_year_b1:     score += 4
    elif liabilityTo_year <= liability_year_b2:     score += 2
    else:                                           score += 0
    
    #8 年度净资产增长率
    #≥25%        得 7
    #15%-25%     得 3
    #<15%        得 0
    # ---------- 年度净资产增长率 ----------
    if yoyEquity_year == 0:                 score += 0
    elif yoyEquity_year >= equity_year_b1:  score += 7
    elif yoyEquity_year >= equity_year_b2:  score += 3
    else:                                   score += 0


    #9 年度负债增长率
    #≤净资产增长率         得 3
    #>净资产增长 且 <25%    得 1
    #≥25%                  得 0
    # ---------- 年度负债增长率（与年度净资产增长率对比） ----------
    if yoyLiability_year == 0:                                      score += 0
    elif yoyLiability_year <= yoyEquity_year:                       score += 3
    elif yoyLiability_year < yoyliab_year_b1:                       score += 1
    else:                                                           score += 0



    #10 季度ROE
    #≥5%         得 10
    #2.5%-5%     得 5
    #<2.5%       得 0
    # ---------- 季度ROE ----------
    if roe_quarter == 0:                score += 0
    elif roe_quarter >= roe_qtr_b1:     score += 10
    elif roe_quarter >= roe_qtr_b2:     score += 5
    else:                               score += 0


    #11 季度净利润增长率（核心指标）
    #≥45%        得 19
    #25%-45%     得 9
    #<25%        得 0
    # ---------- 季度净利润增长率 ----------
    if yoyni_quarter == 0:                  score += 0
    elif yoyni_quarter >= yoyni_qtr_b1:     score += 19
    elif yoyni_quarter >= yoyni_qtr_b2:     score += 9
    else:                                   score += 0

    #12 季度资产负债率变化
    #≤年度值 或 上升≤2%      得 4
    #上升 2%-4%             得 2
    #上升 >4%               得 0
    # ---------- 季度资产负债率变化（与年度值对比） ----------
    if liabilityTo_quarter == 0:            score += 0
    else:
        qtr_rise = liabilityTo_quarter - liabilityTo_year  # 季度较年度上升幅度
        if qtr_rise <= liability_qtr_rise_b1:   score += 4
        elif qtr_rise <= liability_qtr_rise_b2: score += 2
        else:                                   score += 0

    #13 季度净资产增长率
    #≥30%        得 14
    #18%-30%     得 7
    #<18%        得 0
    # ---------- 季度净资产增长率 ----------
    if yoyEquity_quarter == 0:                  score += 0
    elif yoyEquity_quarter >= equity_qtr_b1:    score += 14
    elif yoyEquity_quarter >= equity_qtr_b2:    score += 7
    else:                                       score += 0

    #14 季度负债增长率
    #≤净资产增长率        得 4
    #>净资产增长 且 <28%   得 2
    #≥28%                 得 0
    # ---------- 季度负债增长率（与季度净资产增长率对比） ----------
    if yoyLiability_quarter == 0:                                   score += 0
    elif yoyLiability_quarter <= yoyEquity_quarter:                 score += 4
    elif yoyLiability_quarter < yoyliab_qtr_b1:                     score += 2
    else:                                                           score += 0



    value_b1 = 100
    value_b2 = 300
    value_b3 = 600
    value_b4 = 1000
    if value == 0:                                                score +=0
    if value < value_b1:                                          score +=5
    if value >= value_b1 and value < value_b2:                    score +=10
    if value >= value_b2 and value < value_b3 :                    score +=8
    if value >= value_b3 and value < value_b4:                    score +=7
    if value >= value_b4:                                          score +=5
    removeList = [
        "证券", 
        "银行",
        "全国地产",
        "房产服务",
        "保险",
        "机场",
        "港口",
        "火力发电",
        "水运",
        "煤炭开采",
        "航空",
        "焦炭加工",
        "钢加工",
        "公共交通",
        "公路",
    ]
    # 满分 106 分，归一化到 100
    if removeList.__contains__(componyInfo.Industry):
        score -= 15
    return round(score * 100 / 106, 2)










#计算是否处在行业上涨周期，用于板块轮动买入判断
def CalculateIndustryInfo(main:"Main.processor", dayStr, Length):

    




    #handler = main.InitCalculationDataHandle()
    #handler.Init(main)
    #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    #print("计算模块初始化完毕")
    #totalDateList = handler.InitDateList(dayStr, Length)
    #handler.totalDateList = totalDateList
    #totalDbList = handler.main.dbHandler.GetDailyRowByCodeListAndDateList(handler.totalStockList, totalDateList)
    #handler.totalDbList = totalDbList

    #handler.InitAllBaseDataClsList(totalDateList, totalDbList)

    #count = 0
    #upIndustry = []
    #for key, indusCls in handler.totalComponyIns.industryList.items():
    #    count += 1
    #    windowData = handler.GetIndustryWindowDataByCls("20210201", 0, 20, indusCls)
    #    if windowData is None:
    #        print(f"数据不存在：{indusCls.industryName}")
    #        continue
    #    if windowData.change_Ratio_Total is None:
    #        print(f"数据222222不存在：{indusCls.industryName}")
    #        continue
    #    print(f"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa数据存在：{indusCls.industryName}")

    #    if windowData.change_Ratio_Total > 5 and not (upIndustry.__contains__(indusCls)):
    #        upIndustry.append(indusCls) 

    #for ind in upIndustry:
    #    print(f"总结完毕，行业数量：{count}，  2021年一月上涨的行业是：{ind.industryName}")
    #print("###########################行业总结完毕")
    #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    #handler.ClearDic()
    pass
    
def CalculateIndustryInfoTotal(main:"Main.processor"):
    CalculateIndustryInfo(main, "20210129", 40)
    #CalculateIndustryInfo(main, "20210301", 40)
    #CalculateIndustryInfo(main, "20210331", 40)
    #CalculateIndustryInfo(main, "20210430", 40)
    #CalculateIndustryInfo(main, "20210531", 40)
    #CalculateIndustryInfo(main, "20210630", 40)
    #CalculateIndustryInfo(main, "20210730", 40)
    #CalculateIndustryInfo(main, "20210831", 40)
    #CalculateIndustryInfo(main, "20210930", 40)
    #CalculateIndustryInfo(main, "20211029", 40)
    #CalculateIndustryInfo(main, "20211130", 40)
    #CalculateIndustryInfo(main, "20211231", 40)


    #CalculateIndustryInfo(main, "20220128", 40)
    #CalculateIndustryInfo(main, "20220228", 40)
    #CalculateIndustryInfo(main, "20220331", 40)
    #CalculateIndustryInfo(main, "20220429", 40)
    #CalculateIndustryInfo(main, "20220531", 40)
    #CalculateIndustryInfo(main, "20220630", 40)
    #CalculateIndustryInfo(main, "20220729", 40)
    #CalculateIndustryInfo(main, "20220831", 40)
    #CalculateIndustryInfo(main, "20220930", 40)
    #CalculateIndustryInfo(main, "20221031", 40)
    #CalculateIndustryInfo(main, "20221130", 40)
    #CalculateIndustryInfo(main, "20221230", 40)



    #CalculateIndustryInfo(main, "20230131", 40)
    #CalculateIndustryInfo(main, "20230228", 40)
    #CalculateIndustryInfo(main, "20230331", 40)
    #CalculateIndustryInfo(main, "20230428", 40)
    #CalculateIndustryInfo(main, "20230531", 40)
    #CalculateIndustryInfo(main, "20230630", 40)
    #CalculateIndustryInfo(main, "20230731", 40)
    #CalculateIndustryInfo(main, "20230831", 40)
    #CalculateIndustryInfo(main, "20230928", 40)
    #CalculateIndustryInfo(main, "20231031", 40)
    #CalculateIndustryInfo(main, "20231130", 40)
    #CalculateIndustryInfo(main, "20231229", 40)



    #CalculateIndustryInfo(main, "20240131", 40)
    #CalculateIndustryInfo(main, "20240229", 40)
    #CalculateIndustryInfo(main, "20240329", 40)
    #CalculateIndustryInfo(main, "20240430", 40)
    #CalculateIndustryInfo(main, "20240531", 40)
    #CalculateIndustryInfo(main, "20240628", 40)
    #CalculateIndustryInfo(main, "20240731", 40)
    #CalculateIndustryInfo(main, "20240830", 40)
    #CalculateIndustryInfo(main, "20240930", 40)
    #CalculateIndustryInfo(main, "20241031", 40)
    #CalculateIndustryInfo(main, "20241129", 40)
    #CalculateIndustryInfo(main, "20241231", 40)



    #CalculateIndustryInfo(main, "20250127", 40)
    #CalculateIndustryInfo(main, "20250228", 40)
    #CalculateIndustryInfo(main, "20250331", 40)
    #CalculateIndustryInfo(main, "20250430", 40)
    #CalculateIndustryInfo(main, "20250530", 40)
    #CalculateIndustryInfo(main, "20250630", 40)
    #CalculateIndustryInfo(main, "20250731", 40)
    #CalculateIndustryInfo(main, "20250829", 40)
    #CalculateIndustryInfo(main, "20250930", 40)
    #CalculateIndustryInfo(main, "20251031", 40)
    #CalculateIndustryInfo(main, "20251128", 40)
    #CalculateIndustryInfo(main, "20251231", 40)



