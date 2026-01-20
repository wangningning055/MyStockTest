from enum import Enum

class ColumnEnum(Enum):
    Code = 1,                                   #股票代码
    Date = 2,                                   #交易日期
    Open_Price = 3,                             #开盘价
    Close_Price = 4,                            #收盘价
    High_Price = 5,                             #最高价
    Low_Price = 6,                               #最低价
    Change_Num = 7,                              #涨跌额
    Change_Ratio = 8,                             #涨跌幅（%）
    Amount = 9,                                  #成交量（手）
    Amount_Price = 10,                           #成交额（千元）
    Last_Close_Price = 11,                        #昨日收盘价

class DailyDBStructClass:
    def __init__(self):
        self.CreateDic()

    def GetDBTypeByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "TEXT"
        elif enum == ColumnEnum.Date:
            return "TEXT"
        elif enum == ColumnEnum.Open_Price:
            return "REAL"
        elif enum == ColumnEnum.Close_Price:
            return "REAL"
        elif enum == ColumnEnum.High_Price:
            return "REAL"
        elif enum == ColumnEnum.Low_Price:
            return "REAL"
        elif enum == ColumnEnum.Change_Num:
            return "REAL"
        elif enum == ColumnEnum.Change_Ratio:
            return "REAL"
        elif enum == ColumnEnum.Amount:
            return "INTEGER"
        elif enum == ColumnEnum.Amount_Price:
            return "REAL"
        elif enum == ColumnEnum.Last_Close_Price:
            return "REAL"

    def CreateDic(self):
        self.dic = {
            ColumnEnum.Code : 0,
            ColumnEnum.Date : 0,
            ColumnEnum.Open_Price : 0,
            ColumnEnum.Close_Price : 0,
            ColumnEnum.High_Price : 0,
            ColumnEnum.Low_Price : 0,
            ColumnEnum.Change_Num : 0,
            ColumnEnum.Change_Ratio : 0,
            ColumnEnum.Amount : 0,
            ColumnEnum.Amount_Price : 0,
            ColumnEnum.Last_Close_Price : 0
        }


    def GetNameByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "code"
        elif enum == ColumnEnum.Date:
            return "date"
        elif enum == ColumnEnum.Open_Price:
            return "open_price"
        elif enum == ColumnEnum.Close_Price:
            return "close_price"
        elif enum == ColumnEnum.High_Price:
            return "high_price"
        elif enum == ColumnEnum.Low_Price:
            return "low_price"
        elif enum == ColumnEnum.Change_Num:
            return "change_num"
        elif enum == ColumnEnum.Change_Ratio:
            return "change_ratio"
        elif enum == ColumnEnum.Amount:
            return "amount"
        elif enum == ColumnEnum.Amount_Price:
            return "amount_price"
        elif enum == ColumnEnum.Last_Close_Price:
            return "last_close_price"

    def GetDiscByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "股票代码"
        elif enum == ColumnEnum.Date:
            return "交易日期"
        elif enum == ColumnEnum.Open_Price:
            return "开盘价"
        elif enum == ColumnEnum.Close_Price:
            return "收盘价"
        elif enum == ColumnEnum.High_Price:
            return "最高价"
        elif enum == ColumnEnum.Low_Price:
            return "最低价"
        elif enum == ColumnEnum.Change_Num:
            return "涨跌额"
        elif enum == ColumnEnum.Change_Ratio:
            return "涨跌幅（%）"
        elif enum == ColumnEnum.Amount:
            return "成交量（手）"
        elif enum == ColumnEnum.Amount_Price:
            return "成交额（千元）"
        elif enum == ColumnEnum.Last_Close_Price:
            return "昨收价"

    def GetValueByEnum(self, enum):
        return self.dic[enum]
    

    def SetValueByEnum(self, enum, val):
        self.dic[enum] = val



    def LogData(self):
        logstr = ""
        for k, v in self.dic.items():
            logstr += f"key={k}, val={v}, name= {self.GetNameByEnum(k)}, disc = {self.GetDiscByEnum(k)}\n"
        print(logstr)