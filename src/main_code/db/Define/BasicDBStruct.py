from enum import Enum

class ColumnEnum(Enum):
    Ts_code = 1,                                 #股票TS代码(已有)
    Code = 2,                                    #股票代码(已有)
    Name = 3,                                    #股票名称(已有)
    Area = 4,                                    #地域(已有)
    Industry = 5,                                #所属行业(已有)
    Cn_spell = 6,                                #拼音缩写(已有)
    Market = 7,                                  #市场类型（主板/创业板/科创板/CDR）(已有)
    List_Status = 8,                           #上市状态 L上市 D退市 P暂停上市(已有)
    List_date = 9,                            #上市日期(已有)
    Act_name = 10,                              #实控人名称(已有)
    Act_ent_type = 11,                            #实际企业类型(已有)
    Product = 12                                 #主要产品(已有)
    Business_Scope = 13,                            #经营范围(已有)
    Introduction = 14,                             #公司简介(已有)
    Com_name = 15                                   #公司名称(已有)

class DBStructClass:
    def __init__(self):
        self.CreateDic()
    def GetDBTypeByEnum(self, enum):
        return "TEXT"

    def CreateDic(self):
        self.dic = {
            ColumnEnum.Ts_code : 0,
            ColumnEnum.Code : 0,
            ColumnEnum.Name : 0,
            ColumnEnum.Area : 0,
            ColumnEnum.Industry : 0,
            ColumnEnum.Cn_spell : 0,
            ColumnEnum.Market : 0,
            ColumnEnum.List_Status : 0,
            ColumnEnum.List_date : 0,
            ColumnEnum.Act_name : 0,
            ColumnEnum.Act_ent_type : 0,
            ColumnEnum.Product : 0,
            ColumnEnum.Business_Scope : 0,
            ColumnEnum.Introduction : 0,
            ColumnEnum.Com_name : 0
        }


    def GetNameByEnum(self, enum):
        if enum == ColumnEnum.Ts_code:
            return "ts_code"
        elif enum == ColumnEnum.Code:
            return "code"
        elif enum == ColumnEnum.Name:
            return "name"
        elif enum == ColumnEnum.Area:
            return "area"
        elif enum == ColumnEnum.Industry:
            return "industry"
        elif enum == ColumnEnum.Cn_spell:
            return "cn_spell"
        elif enum == ColumnEnum.Market:
            return "market"
        elif enum == ColumnEnum.List_Status:
            return "list_status"
        elif enum == ColumnEnum.List_date:
            return "list_date"
        elif enum == ColumnEnum.Act_name:
            return "act_name"
        elif enum == ColumnEnum.Act_ent_type:
            return "act_ent_type"
        elif enum == ColumnEnum.Product:
            return "product"
        elif enum == ColumnEnum.Business_Scope:
            return "business_scope"
        elif enum == ColumnEnum.Introduction:
            return "introduction"
        elif enum == ColumnEnum.Com_name:
            return "com_name"

    def GetDiscByEnum(self, enum):
        if enum == ColumnEnum.Ts_code:
            return "股票TS代码"
        elif enum == ColumnEnum.Code:
            return "股票代码"
        elif enum == ColumnEnum.Name:
            return "股票名称"
        elif enum == ColumnEnum.Area:
            return "地域"
        elif enum == ColumnEnum.Industry:
            return "所属行业"
        elif enum == ColumnEnum.Cn_spell:
            return "拼音缩写"
        elif enum == ColumnEnum.Market:
            return "市场类型（主板/创业板/科创板/CDR）"
        elif enum == ColumnEnum.List_Status:
            return "上市状态 L上市 D退市 P暂停上市"
        elif enum == ColumnEnum.List_date:
            return "上市日期"
        elif enum == ColumnEnum.Act_name:
            return "实控人名称"
        elif enum == ColumnEnum.Act_ent_type:
            return "实际企业类型"
        elif enum == ColumnEnum.Product:
            return "主要产品"
        elif enum == ColumnEnum.Business_Scope:
            return "经营范围"
        elif enum == ColumnEnum.Introduction:
            return "公司简介"
        elif enum == ColumnEnum.Com_name:
            return "公司名称"
        
    def GetValueByEnum(self, enum):
        return self.dic[enum]
    

    def SetValueByEnum(self, enum, val):
        self.dic[enum] = val