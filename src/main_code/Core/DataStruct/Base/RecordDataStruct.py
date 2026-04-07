
import json
import src.main_code.Core.Const as const_proj

from typing import List, Optional, Callable, Dict, Any, Union,Tuple  
class TotalRecordDataCls:
    industry_Analyze_Dic:Dict[str, List[str]]                     #行业过去的{"202505", list[str]} 对应的年月所增长的行业
    industry_Increase_Dic:Dict[int, List[str]]                     #总结出过去的五年中某个月，该行业上超过三次

    #("银行", 1):2 
    #"银行": {"1": 4, "2": 3, "3": 2, "4": 5, "5": 1, "6": 0, "7": 2, "8": 3, "9": 4, "10": 5, "11": 2, "12": 3, "avgChange": 2.18},
    industry_Increase_Month_Dic:Dict[str, Dict[str, int]]          #行业每月增长情况

    stock_list_last_data:str                                      #股票列表上次的拉取日期
    daily_list_last_data:str                                        #日线列表上次完整拉取的日期
    adjust_list_last_data:str                                        #复权列表上次完整拉取的日期
    value_list_last_data:str                                        #价值列表上次完整拉取的日期

    industry_analyze_last_data:str                                     #行业轮动分析上次分析完的日期

    industry_list:str                                               #行业列表



    def __init__(self):
        self.industry_Analyze_Dic = {}
        self.industry_Increase_Dic = {}
        self.industry_Increase_Month_Dic = {}
        self.stock_list_last_data = const_proj.first_Data
        self.daily_list_last_data = const_proj.first_Data
        self.adjust_list_last_data = const_proj.first_Data
        self.value_list_last_data = const_proj.first_Data
        self.industry_analyze_last_data = const_proj.first_Data

        self.daily_list_pull_record = []
        self.adjust_list_pull_record = []
        self.value_list_pull_record = []