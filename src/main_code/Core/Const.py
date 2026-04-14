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


#dateListLength =340     #缓存的日期长度
#dateList240Length = 280    #缓存的240日期长度

dateListLength = 70    #缓存的日期长度
dateList240Length = 10    #缓存的240日期长度

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




    #这是我的网页，我需要你关注其中的模式匹配页签
    #现在在匹配完毕后，可以查看每个匹配结果的K线图，参数列表
    #我需要你新加一个功能，匹配完毕后，还可以看参数列表中每个参数的散点图，图的横轴是一个一个的匹配，纵轴是该匹配的此参数值，并可以查看这些参数的密集范围在哪个区间
    #你不需要给我完整文件，只需要告诉我哪里修改，并给出前端测试代码


























