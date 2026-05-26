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

#dateListLength = 70    #数据预热缓存的日期长度（剔除周末）
#dateList240Length = 50    #数据预热缓存的240日期长度（剔除非交易日及停牌日）


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

#小盘：流通在20-50， 幅度在20以内
#标准箱体在1-4周， 箱体最长3个月， 两周以下为轻仓，一个月以上为重仓

#中盘 流通在50-200， 幅度在15以内
#标准箱体在1-3个月，箱体最短两周，最长6个月，一个月左右中度控盘，两个月以上且带有大缩量为重仓


#大盘 流通在200以上， 幅度在10以内
#标准箱体在3-6个月，箱体最短一个月，最长12个月，没有控盘，多为合力

#重仓的换手在箱体初期起码要在3以上，末期高控盘缩量换手需要在1-2之间
#清仓的换手会很高，5-10之间，并不确定







