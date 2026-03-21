
import json
import src.main_code.Core.Const as const_proj

from typing import List, Optional, Callable, Dict, Any, Union,Tuple  
class TotalRecordDataCls:
    industry_Analyze_Dic:Dict[str,List[str]]                     #行业过去的{"202505", list[str]} 对应的年月所增长的行业

    stock_list_last_data:str                                      #股票列表上次的拉取日期
    daily_list_last_data:str                                        #日线列表上次完整拉取的日期
    adjust_list_last_data:str                                        #复权列表上次完整拉取的日期
    value_list_last_data:str                                        #价值列表上次完整拉取的日期

    industry_analyze_last_data:str                                     #行业轮动分析上次分析完的日期

    #daily_list_pull_record:List[Dict[str, str]]                   #日线数据  股票列表，顺带最近的成功写入的日期  [000001.SZ, 20260304]
    #adjust_list_pull_record:List[Dict[str, str]]                   #复权数据  股票列，表顺带最近的成功写入的日期
    #value_list_pull_record:List[Dict[str, str]]                   #价值数据  股票列表，顺带最近的成功写入的日期


    def __init__(self):
        self.industry_Analyze_Dic = {}
        self.stock_list_last_data = const_proj.first_Data
        self.daily_list_last_data = const_proj.first_Data
        self.adjust_list_last_data = const_proj.first_Data
        self.value_list_last_data = const_proj.first_Data
        self.industry_analyze_last_data = const_proj.first_Data

        self.daily_list_pull_record = []
        self.adjust_list_pull_record = []
        self.value_list_pull_record = []