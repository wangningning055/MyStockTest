from enum import Enum

class ColumnEnum(Enum):
    Code = 1,                                   #股票代码
    Date = 2,                                   #除权除息日期
    For_Adjust = 3,                             #前复权因子
    Back_Adjust = 4,                            #后复权因子


class DBStructClass :
    def __init__(self):
        self.CreateDic()

    def GetDBTypeByEnum(self, enum):
        if enum == ColumnEnum.Code:
            return "TEXT"
        elif enum == ColumnEnum.Date:
            return "TEXT"
        elif enum == ColumnEnum.For_Adjust:
            return "REAL"
        elif enum == ColumnEnum.Back_Adjust:
            return "REAL"

    def CreateDic(self):
        self.dic = {
            ColumnEnum.Code : 0,
            ColumnEnum.Date : 0,
            ColumnEnum.For_Adjust : 0,
            ColumnEnum.Back_Adjust : 0,
        }

    #通过枚举获得字段名
    def GetNameByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "Code"
        elif columnEnum == ColumnEnum.Date :
            return "Date" 
        elif columnEnum == ColumnEnum.For_Adjust :
            return "Open_Price"
        elif columnEnum == ColumnEnum.Back_Adjust :
            return "Close_Price"

    #通过枚举获得字段名
    def GetEnumByName(self, name):
        if name == "Code" :
            return ColumnEnum.Code
        elif name == "Date" :
            return ColumnEnum.Date 
        elif name == "For_Adjust" :
            return ColumnEnum.For_Adjust
        elif name == "Back_Adjust" :
            return ColumnEnum.Back_Adjust



    #通过枚举获取说明
    def GetDiscByEnum(self, columnEnum):
        if columnEnum == ColumnEnum.Code :
            return "股票代码"
        elif columnEnum == ColumnEnum.Date :
            return "除权除息日期" 
        elif columnEnum == ColumnEnum.Open_Price :
            return "前复权"
        elif columnEnum == ColumnEnum.Close_Price :
            return "后复权"


    #通过枚举获取内容
    def GetValueByEnum(self, columnEnum):
        return self.dic[columnEnum]

        
    def SetValueByEnum(self, columnEnum, value):
        self.dic[columnEnum] = value