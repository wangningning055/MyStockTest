
import json
from typing import List, Optional, Callable, Dict, Any, Union,Tuple  
class TotalRecordData:
    industryGrowDic:Dict[str,List[str]]                     #行业过去的{"202505", list[str]} 对应的年月所增长的行业

    #股票列表上次的拉取日期
    #日线列表上次完整拉取的日期
    #复权列表上次完整拉取的日期
    #价值列表上次完整拉取的日期
    #行业轮动分析上次分析完的日期

    #日线数据  股票列表，顺带最近的成功写入的日期
    #复权数据  股票列，表顺带最近的成功写入的日期
    #价值数据  股票列表，顺带最近的成功写入的日期


    def __init__(self):
        self.allDic = {}


    #后续还会加数据拉取相关的记录