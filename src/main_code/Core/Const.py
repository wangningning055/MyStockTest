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


dateListLength = 280     #缓存的日期长度


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




    #行业趋势列表 后端接入

    #股票查询页签 后端接入

    #选股页签
    #这是我的网页，我需要你专注于选股页签，对这个页签进行重构，
    # 1.保留这个页签的原功能不变，但剔除掉查看选股结果和K线图，
    # 2.当收到选股结果时，在执行筛选的按钮下出现按钮：查看结果
    # 3.点击查看结果，可以是弹窗或者另一个页签的子页签，展示出选股结果列表（支持返回），列表横向条目有，股票代码，股票名称，筛选得分，行业， 流通市值，3日，5日，10日，20日，40日，60日，120日，240日涨跌幅，且列表支持纵向滚动
    # 4.列表支持通过筛选得分，流通市值和涨跌幅进行排序
    # 5.点击列表中的某一条，弹出这天个股票的240日K线图，以及一个详细参数列表，预计参数量会有上百个，这个你组织好界面即可，参数我自行定义
    # 6.考虑到K线图数据量极大，我后端使用的python的fastCore，给我一个流式传输的示例好让我传输选股结果数据
    # 7.最后给我选股结果后端接入所需要的数据结构，以及前端选股结果功能的测试用例


    #回测页签


    #一个月或者三个月之类的爆发性增长的股票筛选，寻找爆发前的特色， 这给做成个页签吧
























