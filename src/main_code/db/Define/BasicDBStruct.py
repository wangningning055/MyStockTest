from enum import Enum

class ColumnEnum(Enum):
    Ts_code = 1,                                 #股票TS代码
    Code = 2,                                    #股票代码
    Name = 3,                                    #股票名称
    Area = 4,                                    #地域
    Industry = 5,                                #所属行业
    Fullname = 6,                               #股票全称
    En_Name = 7,                                 #英文全称
    Cn_spell = 8,                                #拼音缩写
    Market = 9,                                  #市场类型（主板/创业板/科创板/CDR）
    Exchange = 10,                              #交易所代码
    Curr_Type = 12,                             #交易货币
    List_Status = 13,                           #上市状态 L上市 D退市 P暂停上市
    List_date = 14,                            #上市日期
    Is_hs = 15,                                 #是否沪深港通标的，N否 H沪股通 S深股通
    Act_name = 16,                              #实控人名称
    Act_ent_type = 17,                            #实际企业类型

class BasicDBStructClass:
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
            ColumnEnum.Fullname : 0,
            ColumnEnum.En_Name : 0,
            ColumnEnum.Cn_spell : 0,
            ColumnEnum.Market : 0,
            ColumnEnum.Exchange : 0,
            ColumnEnum.Curr_Type : 0,
            ColumnEnum.List_Status : 0,
            ColumnEnum.List_date : 0,
            ColumnEnum.Is_hs : 0,
            ColumnEnum.Act_name : 0,
            ColumnEnum.Act_ent_type : 0
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
        elif enum == ColumnEnum.Fullname:
            return "fullname"
        elif enum == ColumnEnum.En_Name:
            return "en_name"
        elif enum == ColumnEnum.Cn_spell:
            return "cn_spell"
        elif enum == ColumnEnum.Market:
            return "market"
        elif enum == ColumnEnum.Exchange:
            return "exchange"
        elif enum == ColumnEnum.Curr_Type:
            return "curr_type"
        elif enum == ColumnEnum.List_Status:
            return "list_status"
        elif enum == ColumnEnum.List_date:
            return "list_date"
        elif enum == ColumnEnum.Is_hs:
            return "is_hs"
        elif enum == ColumnEnum.Act_name:
            return "act_name"
        elif enum == ColumnEnum.Act_ent_type:
            return "act_ent_type"

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
        elif enum == ColumnEnum.Fullname:
            return "股票全称"
        elif enum == ColumnEnum.En_Name:
            return "英文全称"
        elif enum == ColumnEnum.Cn_spell:
            return "拼音缩写"
        elif enum == ColumnEnum.Market:
            return "市场类型（主板/创业板/科创板/CDR）"
        elif enum == ColumnEnum.Exchange:
            return "交易所代码"
        elif enum == ColumnEnum.Curr_Type:
            return "交易货币"
        elif enum == ColumnEnum.List_Status:
            return "上市状态 L上市 D退市 P暂停上市"
        elif enum == ColumnEnum.List_date:
            return "上市日期"
        elif enum == ColumnEnum.Is_hs:
            return "是否沪深港通标的，N否 H沪股通 S深股通"
        elif enum == ColumnEnum.Act_name:
            return "实控人名称"
        elif enum == ColumnEnum.Act_ent_type:
            return "实际企业类型"

    def GetValueByEnum(self, enum):
        return self.dic[enum]
    

    def SetValueByEnum(self, enum, val):
        self.dic[enum] = val