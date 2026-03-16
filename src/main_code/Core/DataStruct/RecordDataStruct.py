
import json
from typing import List, Optional, Callable, Dict, Any, Union,Tuple  
class TotalRecordData:
    industryGrowDic:Dict[str,List[str]]                     #行业过去的{"202505", list[str]} 对应的年月所增长的行业


    def __init__(self):
        self.allDic = {}


    #后续还会加数据拉取相关的记录