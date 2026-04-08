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


dateListLength = 30     #缓存的日期长度


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




    #这是我的网页，我需要你新添加一个页签
    #我在这个页签上可以设置开始时间和匹配参数，匹配参数示例：30天内 + 涨幅大于100%， 匹配参数的这两个参数可以单独设置互相组合
    #参数设置完后，可以点击“进行匹配”按钮，向服务器发送匹配消息，进入匹配中的状态，等待服务器返回
    #服务器返回结果后，取消匹配中状态，出现按钮查看匹配结果
    #点击查看匹配结果，新的页面上会有一个列表，逐个列出匹配的结果，列表条目：代码， 名称， 匹配开始时间，匹配结束时间
    #匹配结果列表支持点击查看K线，查看K线时，K线上会标注出匹配开始时间点和匹配结束时间点，
    # 查看K线时，旁边显示出参数列表，参数列表条目我会自行添加，留下添加位置即可
    # 具体K线以及参数列表你可以参考已有的K线显示逻辑（参考selectionResultManager），但这个区别是数据已有，而不是打开才请求
    #支持将整个匹配结果导出为json，并可以从页签上重新从json再导入
    #查看结果页面除了匹配结果列表外，有多个按钮，分别是导出参数均值，导出参数中位数，导出参数聚合数等等（后续可能还会加）
    #在我点击导出参数均值，导出参数中位数等后，发送消息给服务器，等待服务器返回
    #服务器返回参数导出结果后，直接生成json保存，并出现按钮查看参数导出结果，点击后出现弹窗可以查看最终的参数列表
    #给我完整的python后端接入的数据结构，注意要确保前后端使用字段一致，并告诉我大致python后端怎么接入
    #给我完整的前端测试代码，并告诉我怎么测试
























