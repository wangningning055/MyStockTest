from enum import Enum

class ColumnEnum(Enum):
    Code = 1,                                   #股票代码1
    Date = 2,                                   #交易日期1
    Open_Price = 3,                             #开盘价1
    Close_Price = 4,                            #收盘价1
    High_Price = 5,                             #最高价1
    Low_Price = 6,                               #最低价1
    Exchange_Hand = 7,                           #换手率
    Change_Ratio = 8,                            #涨跌幅（%）1
    Amount = 9,                                  #成交量（股）1
    Amount_Price = 10,                           #成交额（元）1
    Earn_TTM = 11,                               #滚动市盈率（TTM）（市值和近十二个月的公司利润的比值），市盈率越小，公司利润越高，稳定赚钱的公司才有参考价值（公共事业，医疗）
    Clean = 12,                                  #市净率（市值和公司的净资产的比值），重资产的公司指标，（钢铁，煤炭，化工）
    Cash_TTM = 13,                               #滚动市现率（TTM）（市值和近十二个月的公司现金流的比值），现金流充裕的公司才有参考价值（互联网，轻资产公司），市盈率低市现率高说明被人欠债了
    Sale_TTM = 14,                               #滚动市销率（TTM）（市值和公司的营收的比值）（扩张型公司）
    Is_ST = 15,                                   #是否ST股，1是0否
    Is_Trading = 16                               #交易状态 1正常交易， 0停牌
    Last_Close_Price = 17                         #昨收价1
    All_Amount = 18                         #总股本
    Current_Amount = 19                         #流通股本
    Adjst = 20                         #复权因子
    Volume = 21                         #量比
    Average_Price = 22                         #均价
    Amplitude = 23                         #振幅
    
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
        elif enum == ColumnEnum.Exchange_Hand:
            return "REAL"
        elif enum == ColumnEnum.Change_Ratio:
            return "REAL"
        elif enum == ColumnEnum.Amount:
            return "INTEGER"
        elif enum == ColumnEnum.Earn_TTM:
            return "REAL"
        elif enum == ColumnEnum.Clean:
            return "REAL"
        elif enum == ColumnEnum.Cash_TTM:
            return "REAL"
        elif enum == ColumnEnum.Sale_TTM:
            return "REAL"
        elif enum == ColumnEnum.Is_ST:
            return "INTEGER"
        elif enum == ColumnEnum.Is_Trading:
            return "INTEGER"
        elif enum == ColumnEnum.Last_Close_Price:
            return "REAL"
        elif enum == ColumnEnum.Amount_Price:
            return "REAL"
        elif enum == ColumnEnum.All_Amount:
            return "INTEGER"
        elif enum == ColumnEnum.Current_Amount:
            return "INTEGER"
        elif enum == ColumnEnum.Adjst:
            return "REAL"
        elif enum == ColumnEnum.Volume:
            return "REAL"
        elif enum == ColumnEnum.Average_Price:
            return "REAL"
        elif enum == ColumnEnum.Amplitude:
            return "REAL"

    def CreateDic(self):
        self.dic = {
            ColumnEnum.Code : 0,
            ColumnEnum.Date : 0,
            ColumnEnum.Open_Price : 0,
            ColumnEnum.Close_Price : 0,
            ColumnEnum.High_Price : 0,
            ColumnEnum.Low_Price : 0,
            ColumnEnum.Exchange_Hand : 0,
            ColumnEnum.Change_Ratio : 0,
            ColumnEnum.Amount : 0,
            ColumnEnum.Amount_Price : 0,
            ColumnEnum.Earn_TTM : 0,
            ColumnEnum.Clean : 0,
            ColumnEnum.Cash_TTM : 0,
            ColumnEnum.Sale_TTM : 0,
            ColumnEnum.Is_ST : 0,
            ColumnEnum.Is_Trading : 0,
            ColumnEnum.Last_Close_Price : 0,
            ColumnEnum.All_Amount : 0,
            ColumnEnum.Current_Amount : 0, 
            ColumnEnum.Adjst : 0,
            ColumnEnum.Volume : 0,
            ColumnEnum.Average_Price : 0,
            ColumnEnum.Amplitude : 0

        }


    def GetNameByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "ts_code"
        elif enum == ColumnEnum.Date:
            return "trade_date"
        elif enum == ColumnEnum.Open_Price:
            return "open"
        elif enum == ColumnEnum.Close_Price:
            return "close"
        elif enum == ColumnEnum.High_Price:
            return "high"
        elif enum == ColumnEnum.Low_Price:
            return "low"
        elif enum == ColumnEnum.Exchange_Hand:
            return "turn"
        elif enum == ColumnEnum.Change_Ratio:
            return "change_ratio"
        elif enum == ColumnEnum.Amount:
            return "amount"
        elif enum == ColumnEnum.Amount_Price:
            return "amount_price"
        elif enum == ColumnEnum.Earn_TTM:
            return "earn_TTM"
        elif enum == ColumnEnum.Clean:
            return "Clean"
        elif enum == ColumnEnum.Cash_TTM:
            return "cash_TTM"
        elif enum == ColumnEnum.Sale_TTM:
            return "sale_TTM"
        elif enum == ColumnEnum.Is_ST:
            return "is_st"
        elif enum == ColumnEnum.Is_Trading:
            return "is_trading"
        elif enum == ColumnEnum.Last_Close_Price:
            return "last_close_Price"
        elif enum == ColumnEnum.All_Amount:
            return "all_amount"
        elif enum == ColumnEnum.Current_Amount:
            return "current_amount"
        elif enum == ColumnEnum.Adjst:
            return "adjst"
        elif enum == ColumnEnum.Volume:
            return "volume"
        elif enum == ColumnEnum.Average_Price:
            return "average_price"
        elif enum == ColumnEnum.Amplitude:
            return "amplitude"

    def GetDiscByEnum(self, enum):
        pass

    def GetValueByEnum(self, enum):
        return self.dic[enum]
    

    def SetValueByEnum(self, enum, val):
        self.dic[enum] = val



    def LogData(self):
        logstr = ""
        for k, v in self.dic.items():
            logstr += f"key={k}, val={v}, name= {self.GetNameByEnum(k)}, disc = {self.GetDiscByEnum(k)}\n"
        print(logstr)