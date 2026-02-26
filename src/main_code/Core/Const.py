from enum import Enum


    #token = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
    #token = "323752147f60806f5823e0209c317ce5aa507863fa9184b3cd7d5839"
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

#判断是否涨跌的边界（%）
up_down_boundary = 1

#判断是否震荡的边界（%，振幅）
amplitude_boundary = 4

#判断是否放量缩量的边界(%)
volume_boundary = 2

#备忘
#记得添加资金流通率（成交额 / 流通市值）
#记得添加股票估值计算



#pe: 市盈率（TTM，数值型）
#pb: 市净率（数值型）
#pcf: 市现率（经营现金流口径，数值型）
#ps: 市销率（TTM，数值型


#这些需要重新拉
#roe：净资产收益率      有
#净利润同比增长率       有
#资产负债率             有

#已经拉的：
#日线， 
# 复权数据





#指标	边界	逻辑
#高价值股筛选逻辑
#PE	0~35	必须盈利（PE>0），且估值不高估，排除亏损 / 泡沫股
#PB	0~6	资产端有安全垫，排除资产泡沫的公司
#PCF	0~30	现金流为正（PCF>0），确保是 “真赚钱” 而非账面利润
#PS	0~10	营收端也不贵，避免 “盈利但营收不值钱” 的公司
#ROE > 10%
#资产负债率 < 50%

#高成长股筛选逻辑
#PS	0~15	成长股核心指标，PS≤15 避免估值泡沫，是筛选的核心门槛
#PE	-100~100	允许亏损（PE<0）或高 PE，仅排除极端值（比如 PE 上千）
#PB	0~20	允许轻资产成长股的高 PB（比如科技股 PB15），仅排除极端值
#PCF	-100~50	允许现金流为负（比如烧钱扩规模），仅排除极端值

#PEG = PE / 净利润增长率 < 1.2
#资产负债率 < 70%






#核心买入：放量上涨（资金进场）+ 震荡上行（趋势向上）
#次优买入：平量上涨（无资金出逃）+ 震荡上行（趋势向上）
#抄底：缩量下跌（抛压耗尽）+ 股价低位

#核心卖出 放量下跌（资金出逃）+ 震荡下行（趋势向下）
#次优卖出 缩量上涨（无资金支撑）+股价高位
#阴跌：平量下跌（阴跌）+ 震荡下行 + 股价高位






#选股指标：
#量价（放量，缩量，涨跌，横盘）
#流动性（换手率和资金流动性）日均换手率：3%–15% 且 日均成交额 / 流通市值：>1%
#估值（盈，销，现，净）成长股或高价值股
#均价（股价位置）


