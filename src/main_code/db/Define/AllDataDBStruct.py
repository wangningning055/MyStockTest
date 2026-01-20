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
    Total_Market_Price = 22,                     #总市值（万元）
    Flow_Market_Price = 23,                      #流通市值（万元
    Name =24,                                       #股票名


class DBStructClass :
    def __init__(self):
        self.CreateDic()

    def GetDBTypeByEnum(self, enum):
        return "TEXT"

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
            ColumnEnum.Hand : 0,
            ColumnEnum.Hand_All : 0,
            ColumnEnum.Volume_Ratio : 0,
            ColumnEnum.Earn_Static : 0,
            ColumnEnum.Earn_TTM : 0,
            ColumnEnum.Clean : 0,
            ColumnEnum.Sale : 0,
            ColumnEnum.Sale_TTM : 0,
            ColumnEnum.All_Hand : 0,
            ColumnEnum.Flow_Hand : 0,
            ColumnEnum.Free_Flow_Hand : 0,
            ColumnEnum.Total_Market_Price : 0,
            ColumnEnum.Flow_Market_Price : 0,
            ColumnEnum.Name : 0,
        }

    #通过枚举获得字段名
    def GetNameByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "Code"
        elif columnEnum == ColumnEnum.Date :
            return "Date" 
        elif columnEnum == ColumnEnum.Open_Price :
            return "Open_Price"
        elif columnEnum == ColumnEnum.Close_Price :
            return "Close_Price"
        elif columnEnum == ColumnEnum.High_Price :
            return "High_Price"
        elif columnEnum == ColumnEnum.Low_Price :
            return "Low_Price"
        elif columnEnum == ColumnEnum.Change_Num :
            return "Change_Num"
        elif columnEnum == ColumnEnum.Change_Ratio :
            return "Change_Ratio"
        elif columnEnum == ColumnEnum.Amount :
            return "Amount"
        elif columnEnum == ColumnEnum.Amount_Price :
            return "Amount_Price"
        elif columnEnum == ColumnEnum.Hand :
            return "Hand"
        elif columnEnum == ColumnEnum.Hand_All :
            return "Hand_All"
        elif columnEnum == ColumnEnum.Volume_Ratio :
            return "Volume_Ratio"
        elif columnEnum == ColumnEnum.Earn_Static :
            return "Earn_Static"
        elif columnEnum == ColumnEnum.Earn_TTM :
            return "Earn_TTM"
        elif columnEnum == ColumnEnum.Clean :
            return "Clean"
        elif columnEnum == ColumnEnum.Sale :
            return "Sale"
        elif columnEnum == ColumnEnum.Sale_TTM :
            return "Sale_TTM"
        elif columnEnum == ColumnEnum.All_Hand:
            return "All_Hand"
        elif columnEnum == ColumnEnum.Flow_Hand :
            return "Flow_Hand"
        elif columnEnum == ColumnEnum.Free_Flow_Hand :
            return "Free_Flow_Hand"
        elif columnEnum == ColumnEnum.Total_Market_Price :
            return "Total_Market_Price"
        elif columnEnum == ColumnEnum.Flow_Market_Price :
            return "Flow_Market_Price"
        elif columnEnum == ColumnEnum.Name :
            return "Name"

    #通过枚举获得字段名
    def GetEnumByName(self, name):
        if name == "Code" :
            return ColumnEnum.Code
        elif name == "Date" :
            return ColumnEnum.Date 
        elif name == "Open_Price" :
            return ColumnEnum.Open_Price
        elif name == "Close_Price" :
            return ColumnEnum.Close_Price
        elif name == "High_Price" :
            return ColumnEnum.High_Price
        elif name == "Low_Price" :
            return ColumnEnum.Low_Price
        elif name == "Change_Num" :
            return ColumnEnum.Change_Num
        elif name == "Change_Ratio" :
            return ColumnEnum.Change_Ratio
        elif name == "Amount" :
            return ColumnEnum.Amount
        elif name == "Amount_Price" :
            return ColumnEnum.Amount_Price
        elif name == "Hand" :
            return ColumnEnum.Hand
        elif name == "Hand_All" :
            return ColumnEnum.Hand_All
        elif name == "Volume_Ratio" :
            return ColumnEnum.Volume_Ratio
        elif name == "Earn_Static" :
            return ColumnEnum.Earn_Static
        elif name == "Earn_TTM" :
            return ColumnEnum.Earn_TTM
        elif name == "Clean" :
            return ColumnEnum.Clean
        elif name == "Sale" :
            return ColumnEnum.Sale
        elif name == "Sale_TTM" :
            return ColumnEnum.Sale_TTM
        elif name == "All_Hand":
            return ColumnEnum.All_Hand
        elif name == "Flow_Hand" :
            return ColumnEnum.Flow_Hand
        elif name == "Free_Flow_Hand" :
            return ColumnEnum.Free_Flow_Hand
        elif name == "Total_Market_Price" :
            return ColumnEnum.Total_Market_Price
        elif name == "Flow_Market_Price" :
            return ColumnEnum.Flow_Market_Price
        elif name == "Name" :
            return ColumnEnum.Name


    #通过枚举获取说明
    def GetDiscByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "股票代码"
        elif columnEnum == ColumnEnum.Date :
            return "交易日期" 
        elif columnEnum == ColumnEnum.Open_Price :
            return "开盘价"
        elif columnEnum == ColumnEnum.Close_Price :
            return "收盘价"
        elif columnEnum == ColumnEnum.High_Price :
            return "最高价"
        elif columnEnum == ColumnEnum.Low_Price :
            return "最低价"
        elif columnEnum == ColumnEnum.Change_Num :
            return "涨跌额"
        elif columnEnum == ColumnEnum.Change_Ratio :
            return "涨跌幅（%）"
        elif columnEnum == ColumnEnum.Amount :
            return "成交量（手）"
        elif columnEnum == ColumnEnum.Amount_Price :
            return "成交额（千元）"
        elif columnEnum == ColumnEnum.Hand :
            return "换手率（%）"
        elif columnEnum == ColumnEnum.Hand_All :
            return "换手率（%），总股本口径"
        elif columnEnum == ColumnEnum.Volume_Ratio :
            return "量比（按日线口径，Tushare 提供日均量比）"
        elif columnEnum == ColumnEnum.Earn_Static :
            return "市盈率（静态）"
        elif columnEnum == ColumnEnum.Earn_TTM :
            return "市盈率（TTM）"
        elif columnEnum == ColumnEnum.Clean :
            return "市净率"
        elif columnEnum == ColumnEnum.Sale :
            return "市销率"
        elif columnEnum == ColumnEnum.Sale_TTM :
            return "市销率（TTM）"
        elif columnEnum == ColumnEnum.All_Hand :
            return "总股本（万股）"
        elif columnEnum == ColumnEnum.Flow_Hand :
            return "流通股本（万股）"
        elif columnEnum == ColumnEnum.Free_Flow_Hand :
            return "自由流通股本（万股）"
        elif columnEnum == ColumnEnum.Total_Market_Price :
            return "总市值（万元）"
        elif columnEnum == ColumnEnum.Flow_Market_Price :
            return "流通市值（万元"
        elif columnEnum == ColumnEnum.Name :
            return "股票名"
        

    #通过枚举获取内容
    def GetValueByEnum(self, columnEnum):
        if(columnEnum == ColumnEnum.Code ):
            return self.dic[ColumnEnum.Code]
        elif(columnEnum == ColumnEnum.Date ):
            return self.dic[ColumnEnum.Date]
        elif(columnEnum == ColumnEnum.Open_Price ):
            return self.dic[ColumnEnum.Open_Price]
        elif(columnEnum == ColumnEnum.Close_Price ):
            return self.dic[ColumnEnum.Close_Price]
        elif(columnEnum == ColumnEnum.High_Price ):
            return self.dic[ColumnEnum.High_Price]
        elif(columnEnum == ColumnEnum.Low_Price ):
            return self.dic[ColumnEnum.Low_Price]
        elif(columnEnum == ColumnEnum.Change_Num ):
            return self.dic[ColumnEnum.Change_Num]
        elif(columnEnum == ColumnEnum.Change_Ratio ):
            return self.dic[ColumnEnum.Change_Ratio]
        elif(columnEnum == ColumnEnum.Amount ):
            return self.dic[ColumnEnum.Amount]
        elif(columnEnum == ColumnEnum.Amount_Price ):
            return self.dic[ColumnEnum.Amount_Price]
        elif(columnEnum == ColumnEnum.Hand ):
            return self.dic[ColumnEnum.Hand]
        elif(columnEnum == ColumnEnum.Hand_All ):
            return self.dic[ColumnEnum.Hand_All]
        elif(columnEnum == ColumnEnum.Volume_Ratio ):
            return self.dic[ColumnEnum.Volume_Ratio]
        elif(columnEnum == ColumnEnum.Earn_Static ):
            return self.dic[ColumnEnum.Earn_Static]
        elif(columnEnum == ColumnEnum.Earn_TTM ):
            return self.dic[ColumnEnum.Earn_TTM]
        elif(columnEnum == ColumnEnum.Clean ):
            return self.dic[ColumnEnum.Clean]
        elif(columnEnum == ColumnEnum.Sale ):
            return self.dic[ColumnEnum.Sale]
        elif(columnEnum == ColumnEnum.Sale_TTM ):
            return self.dic[ColumnEnum.Sale_TTM]
        elif(columnEnum == ColumnEnum.All_Hand):
            return self.dic[ColumnEnum.All_Hand]
        elif(columnEnum == ColumnEnum.Flow_Hand ):
            return self.dic[ColumnEnum.Flow_Hand]
        elif(columnEnum == ColumnEnum.Free_Flow_Hand ):
            return self.dic[ColumnEnum.Free_Flow_Hand]
        elif(columnEnum == ColumnEnum.Total_Market_Price ):
            return self.dic[ColumnEnum.Total_Market_Price]
        elif(columnEnum == ColumnEnum.Flow_Market_Price ):
            return self.dic[ColumnEnum.Flow_Market_Price]
        elif(columnEnum == ColumnEnum.Name ):
            return self.dic[ColumnEnum.Name]
        
    def SetValueByEnum(self, columnEnum, value):
        self.dic[columnEnum] = value