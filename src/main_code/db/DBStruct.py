from enum import Enum

class ColumnEnum(Enum):
    Code = 1,                                   #股票代码
    Date = 2,                                   #交易日期
    Open_Price = 3,                             #开盘价
    close_Price = 4,                            #收盘价
    High_Price = 5,                             #最高价
    Low_Price = 6,                               #最低价
    Change_Num = 7,                              #涨跌额
    Change_Ratio = 8,                             #涨跌幅（%）
    Amount = 9,                                  #成交量（手）
    Amount_Price = 10,                           #成交额（千元）
    Hand = 11,                                   #换手率（%）
    Hand_All = 12,                               #换手率（%），总股本口径
    Volume_Ratio = 13,                           #量比（按日线口径，Tushare 提供日均量比）
    Earn_Static = 14,                           #市盈率（静态）
    Earn_TTM = 15,                               #市盈率（TTM）
    Clean = 16,                                  #市净率
    Sale = 17,                                   #市销率
    Sale_TTM = 18,                               #市销率（TTM）
    All_Hand = 19,                              #总股本（万股）
    Flow_Hand = 20,                              #流通股本（万股）
    Free_Flow_Hand = 21,                         #自由流通股本（万股）
    Total_Market_Price = 22,                           #总市值（万元）
    Flow_Market_Price = 23,                      #流通市值（万元


