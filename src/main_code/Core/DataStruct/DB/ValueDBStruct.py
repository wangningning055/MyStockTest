from enum import Enum

class ColumnEnum(Enum):
    Code = 0           #股票代码
    Year = 1           #年份
    Quarter = 2        #季度
    Roe = 3            #roe：净资产收益率      有
    YOYNi = 4            #净利润同比增长率       有
    LiabilityTo = 5            #资产负债率             有
    YOYEquity = 6            #净资产同比增长率       有
    YOYLiability = 7            #负债同比增长率       有

class DBStructClass :
    def __init__(self):
        self.CreateDic()

    def GetDBTypeByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "TEXT"
        elif enum == ColumnEnum.Year:
            return "INTEGER"
        elif enum == ColumnEnum.Quarter:
            return "INTEGER"
        elif enum == ColumnEnum.Roe:
            return "REAL"
        elif enum == ColumnEnum.YOYNi:
            return "REAL"
        elif enum == ColumnEnum.LiabilityTo:
            return "REAL"
        elif enum == ColumnEnum.YOYEquity:
            return "REAL"
        elif enum == ColumnEnum.YOYLiability:
            return "REAL"

    def CreateDic(self):
        self.dic = {
            ColumnEnum.Code : "",
            ColumnEnum.Year : 0,
            ColumnEnum.Quarter : 0,
            ColumnEnum.Roe : 0,
            ColumnEnum.YOYNi : 0,
            ColumnEnum.LiabilityTo : 0,
            ColumnEnum.YOYEquity : 0,
            ColumnEnum.YOYLiability : 0
        }

    #通过枚举获得字段名
    def GetNameByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "Code"
        elif columnEnum == ColumnEnum.Year :
            return "Year"
        elif columnEnum == ColumnEnum.Quarter :
            return "Quarter"
        elif columnEnum == ColumnEnum.Roe :
            return "Roe"
        elif columnEnum == ColumnEnum.YOYNi :
            return "YOYNi" 
        elif columnEnum == ColumnEnum.LiabilityTo :
            return "LiabilityTo"
        elif columnEnum == ColumnEnum.YOYEquity :
            return "YOYEquity"
        elif columnEnum == ColumnEnum.YOYLiability :
            return "YOYLiability"

    #通过枚举获得字段名
    def GetEnumByName(self, name):
        if name == "Code" :
            return ColumnEnum.Code
        elif name == "Year" :
            return ColumnEnum.Year
        elif name == "Quarter" :
            return ColumnEnum.Quarter
        elif name == "Roe" :
            return ColumnEnum.Roe
        elif name == "YOYNi" :
            return ColumnEnum.YOYNi
        elif name == "LiabilityTo" :
            return ColumnEnum.LiabilityTo
        elif name == "YOYEquity" :
            return ColumnEnum.YOYEquity
        elif name == "YOYLiability" :
            return ColumnEnum.YOYLiability



    #通过枚举获取说明
    def GetDiscByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "股票代码"
        elif columnEnum == ColumnEnum.Year :
            return "年份"
        elif columnEnum == ColumnEnum.Quarter :
            return "季度"
        elif columnEnum == ColumnEnum.Roe :
            return "净资产收益率"
        elif columnEnum == ColumnEnum.YOYNi :
            return "净利润同比增长率" 
        elif columnEnum == ColumnEnum.LiabilityTo :
            return "资产负债率"
        elif columnEnum == ColumnEnum.YOYEquity :
            return "净资产同比增长率"
        elif columnEnum == ColumnEnum.YOYLiability :
            return "负债同比增长率"



    #通过枚举获取内容
    def GetValueByEnum(self, columnEnum):
        return self.dic[columnEnum]

        
    def SetValueByEnum(self, columnEnum, value):
        self.dic[columnEnum] = value