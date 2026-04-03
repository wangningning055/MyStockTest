from enum import Enum


##tushare的私钥
token1 = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
token2 = "323752147f60806f5823e0209c317ce5aa507863fa9184b3cd7d5839"


first_Data = "20200101"
start_BackTestingDate = "20210104"


##临时文件相关
TempFileFolderPath = "../TempFile"
TempBasicFilePath = "../TempFile/BasicData/"
TempAdjustFilePath = "../TempFile/AdjustData/"
TempDailyFilePath = "../TempFile/DailyData/"


TempRecordFilePath = "../TempFile/RecordData/"
TempRecord_Industry_Result_FileName = "Industry_Result.json"


TempBasicFileName = "Basic_"
TempAdjustFileName = "Adjust_"
TempDailyFileName = "Daily_"




DBPath = "../DB/StockData.db"
DBBasicTableName = "Basic"
DBDailyTableName = "Daily"
DBAdjustTableName = "Adjust"
DBValueTableName = "Value"

TradeNameSZSE = "SZSE"
TradeNameSSE = "SSE"
TradeNameBSE = "BSE"


IndexHtmlPath = "Web/index.html"

FactorsJsonPath = "Web/factors.json"

#判断是否涨跌的边界（%）
up_down_boundary = 1

#判断是否震荡的边界（%，振幅）
amplitude_boundary = 4

#判断是否放量缩量的边界(%)
volume_boundary = 2


NoneValue = -999999     #指标计算的无效值

progress_interval_preheat = 1     #预热阶段的进度间隔
progress_interval_pull = 20     #拉取数据阶段的进度间隔
progress_interval_backTesting = 1     #回测阶段的进度间隔


dateListLength = 20     #缓存的日期长度


def GetIsCy(stockCode):
    if stockCode.startswith("300") or stockCode.startswith("301"):
        return True
    return False

def GetIsKC(stockCode):
    if stockCode.startswith("688"):
        return True
    return False

def GetIsBJ(stockCode):
    if stockCode.startswith("920"):
        return True
    return False

#获取涨跌幅幅度主板 10， 创业板科创板 20
def GetStopRatio(stockCode):
    if stockCode.startswith("300") or stockCode.startswith("688") or stockCode.startswith("301"):
        return 19.99
    else:
        return 9.99




    #行业趋势列表 等待后端接入

    #股票查询页签 等待后端接入

    #选股页签， 等待后端接入

    #K线图，等待后端接入

    #回测页签

    #这是我的网页，我需要你关注其中的回测页签，并对这个页签进行重构
    # 1、保留分仓配置和执行回测以及剔除逻辑，点击开始回测并回测完毕后，出现按钮：查看回测结果
    # 2、点击查看回测结果，查看结果页面可以根据选择总仓或者某个分仓，来展示该仓位的各种信息
    # 3、需要展示当前选择仓位的：分仓仓位名（总仓直接叫总仓），初始仓价，当前仓价，总收益率，胜率， 平均年化收益率，年化波动率，平均月化收益率， 月化波动率
    # 4、需要展示当前选择仓位的：收益率曲线图，支持放大缩小，鼠标悬停显示该天的买入卖出（如果有的话），当前仓价，涨跌幅，当前持仓等
    # 5、需要展示当前选择仓位的成交列表，列表每条是一个成交，包含了买入时间，卖出时间，持仓天数，股票代码，股票名，买入价，卖出价，盈利（%）  盈利（元），可以按这些参数来排序， 可以点击单个成交进入K线图查看买点和卖点
    # 6、给出完整的后端接入需要的数据结构，以及python后端该如何接入
    # 7、给出完整的前端测试用例，用以测试前端逻辑是否正确


    #一个月或者三个月之类的爆发性增长的股票筛选，寻找爆发前的特色， 这给做成个页签吧
























