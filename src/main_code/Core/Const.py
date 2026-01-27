from enum import Enum


    #token = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
    #token = "323752147f60806f5823e0209c317ce5aa507863fa9184b3cd7d5839"
##tushare的私钥
token1 = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
token2 = "323752147f60806f5823e0209c317ce5aa507863fa9184b3cd7d5839"


first_Data = "20200101"


##临时文件相关
TempFileFolderPath = "../TempFile"
TempBasicFilePath = "../TempFile/BasicData/"
TempAdjustFilePath = "../TempFile/AdjustData/"
TempDailyFilePath = "../TempFile/DailyData/"

TempBasicFileName = "Basic_"
TempAdjustFileName = "Adjust_"
TempDailyFileName = "Daily_"


DBPath = "../DB/StockData.db"
DBBasicTableName = "Basic"
DBDailyTableName = "Daily"
DBAdjustTableName = "Adjust"

TradeNameSZSE = "SZSE"
TradeNameSSE = "SSE"
TradeNameBSE = "BSE"

Request_Data_rec_FileName = "../TempFile/RequestRecorderData.txt"

IndexHtmlPath = "Web/index.html"

class MessageType(str, Enum):
    CS_UPDATE_DATA = "cs_update_data"               #客户端请求拉取数据
    CS_SELECT_STOCKS = "cs_select_stocks"           #客户端请求执行股票筛选
    CS_BACK_TEST = "cs_back_test"                   #客户端请求执行回测
    CS_DIAGNOSE = "cs_diagnose"                     #客户端请求出仓判断
    CS_SEND_LAST_UPDATE_DATA = "sc_last_update_data"#服务器发送上次更新日期
