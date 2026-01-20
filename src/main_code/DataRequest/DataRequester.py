import tushare as ts
import pandas as pd
from db.Define import BasicDBStruct
from db.Define import DailyDBStruct

class DataRequesterClass:
    token = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
    def __init__(self):
        self.InitShare()

    def InitShare(self):
        ts.set_token(self.token)
        self.pro = ts.pro_api()

    #获取股票的交易日历
    def GetStockTradeDaily(self, start_date, end_date):
        start = "2025-01-01"
        end = "2026-01-19"

        # 生成工作日（周一到周五）
        calendar = pd.bdate_range(start=start, end=end)

        # 转成 DataFrame 并格式化为 YYYYMMDD
        df = pd.DataFrame(calendar, columns=["date"])
        df["date"] = df["date"].dt.strftime("%Y%m%d")  # 转为 20250103 格式
        df.to_csv("trading_days_local.csv", index=False)
        return df

    #获取股票的基本数据
    def GetStockBasicData(self):
        df = self.pro.stock_basic(
            exchange='',       # 空表示所有交易所
            list_status='L',   # L = 上市中
            fields=''
        )
        print(df.head())
        print(print(df.tail()))
        #self.LogTxt(df)


    #获取股票的日线行情
    def GetStockDailyData(self):
        df = self.pro.daily(
            ts_code="000001.SZ",
            start_date="20260115",
            end_date="20260119"
        )
        dataClassList = []
        for _, row in df.iterrows():
            testClass = DailyDBStruct.DailyDBStructClass()
            testClass.dic[DailyDBStruct.ColumnEnum.Code] = row['ts_code']
            testClass.dic[DailyDBStruct.ColumnEnum.Date] = row['trade_date']
            testClass.dic[DailyDBStruct.ColumnEnum.Open_Price] = row['open']
            testClass.dic[DailyDBStruct.ColumnEnum.Close_Price] = row['close']
            testClass.dic[DailyDBStruct.ColumnEnum.High_Price] = row['high']
            testClass.dic[DailyDBStruct.ColumnEnum.Low_Price] = row['low']
            testClass.dic[DailyDBStruct.ColumnEnum.Change_Num] = row['change']
            testClass.dic[DailyDBStruct.ColumnEnum.Change_Ratio] = row['pct_chg']
            testClass.dic[DailyDBStruct.ColumnEnum.Amount] = row['vol']
            testClass.dic[DailyDBStruct.ColumnEnum.Amount_Price] = row['amount']
            testClass.dic[DailyDBStruct.ColumnEnum.Last_Close_Price] = row['pre_close']
            dataClassList.append(testClass)
        return dataClassList

    def LogTxt(self, msg):
        txt_file_path = "output.txt"
        # 写入文件，使用 utf-8 编码
        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(msg)

        print(f"write Success {txt_file_path}")