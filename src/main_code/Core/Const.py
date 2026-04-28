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

TempJsonFilePath = "../TempFile/JsonData/"


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



dateListLength = 340    #数据预热缓存的日期长度（剔除周末）
dateList240Length = 280    #数据预热缓存的240日期长度（剔除非交易日及停牌日）

#dateListLength = 100    #数据预热缓存的日期长度（剔除周末）
#dateList240Length = 70    #数据预热缓存的240日期长度（剔除非交易日及停牌日）


dateListLength_BackTest = 380    #回测缓存的日期长度(前后各这么长)
dateList240Length_BackTest = 280    #回测缓存的240日期长度
dateListRefreshLength_BackTest = 200              #回测需要刷新的长度

#dateListLength_BackTest = 38    #回测缓存的日期长度(前后各这么长)
#dateList240Length_BackTest = 28    #回测缓存的240日期长度
#dateListRefreshLength_BackTest = 20              #回测需要刷新的长度


dateListLength_PatternMatch =380     #模式匹配缓存的日期长度(前后各这么长)
dateList240Length_PatternMatch = 280              #模式匹配缓存的240日期长度
dateListRefreshLength_PatternMatch = 200              #模式匹配需要刷新的长度


#dateListLength_PatternMatch =38     #模式匹配缓存的日期长度(前后各这么长)
#dateList240Length_PatternMatch = 28              #模式匹配缓存的240日期长度
#dateListRefreshLength_PatternMatch = 20              #模式匹配需要刷新的长度


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


#拉长持仓天数
#买入时跌幅放大些
#近日回踩可以选两天而不是三天，甚至一天
#策略应该长期走高，但短期走低
#6个月往上走，近三个月往下走，近五天回调， 但限制幅度，长期大跌不买，长期大涨不买














#//          小微盘股，流通市值在10 - 80亿
#            //前120到前240，涨幅在10以上30以下，整体涨幅在0以上，20以下
#            //前40到前120 涨幅涨幅在10以上30以下，整体涨幅在0以上，20以下
#            //前20到前40  涨幅在0以上，在5以下，整体涨幅在0以上，5以下
#            //前3到前20  涨幅在0以下，在-10以上，整体涨跌幅在0以下，-8以上
#            //近3个交易日涨幅在8以上
#            //当日涨幅大于5

#            前3到前20，整体成交量涨跌幅 0以下
#            前6日成交量整体涨跌幅 80以上
#            当日成交量涨跌幅小于0







