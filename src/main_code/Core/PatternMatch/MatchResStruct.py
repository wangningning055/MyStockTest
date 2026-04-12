
from typing import Literal, Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import src.main_code.Core.Select.Models as Models

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

# ============================
# 数据结构定义
# ============================

      #SC_PATTERN_MATCH_RESPONSE = {
#    "matches": [
#        {
#            "code": "600000",                # str, 股票代码
#            "name": "浦发银行",               # str, 股票名称
#            "match_start": "2024-01-05",     # str, 匹配开始日期 YYYY-MM-DD
#            "match_end": "2024-02-03",       # str, 匹配结束日期 YYYY-MM-DD
#            "days": 29,                       # int, 匹配天数
#            "change_pct": 105.3,             # float, 区间涨幅(%)

#            # ★ K线数据：前端直接使用，无需再请求
#            "kline": [
#                {
#                    "date": "2023-12-01",     # str, 日期 YYYY-MM-DD
#                    "open": 10.0,             # float, 开盘价
#                    "close": 10.5,            # float, 收盘价
#                    "high": 10.8,             # float, 最高价
#                    "low": 9.9,               # float, 最低价
#                    "volume": 50000,          # int, 成交量(万手)
#                    "turn": 1.2,              # float, 换手率(%)
#                    "change_Ratio": 2.5,      # float, 涨跌幅(%)
#                },
#                # ... 建议包含匹配区间前后各60个交易日
#            ],

#            # ★ 参数列表：分组结构，后续可自由扩展
#            "params": {
#                "groups": [
#                    {
#                        "name": "价值指标",    # str, 分组名称
#                        "items": [
#                            {
#                                "label": "市盈率(PE)",   # str, 参数名
#                                "value": 12.5,           # float|str, 参数值
#                                "type": "number"         # str, 类型: number|percent|text|currency
#                            },
#                            {
#                                "label": "市净率(PB)",
#                                "value": 1.2,
#                                "type": "number"
#                            },
#                            # ... 更多参数
#                        ]
#                    },
#                    {
#                        "name": "成长指标",
#                        "items": [
#                            {
#                                "label": "净利润同比增长率",
#                                "value": 25.6,
#                                "type": "percent"
#                            },
#                            # ...
#                        ]
#                    },
#                    # ★ 此处可继续添加更多分组 ★
#                ]
#            }
#        },
#        # ... 更多匹配记录
#    ]
#}



@dataclass
class Response:
    """统计摘要"""
    matches: List[dict] = field(default_factory=list)  #Match的字典

@dataclass
class Match:
    code: str = ""                     # "600000"
    name: str = ""                     # "浦发银行"
    match_start: str = ""                # "2024-02-20"
    match_end: str = ""                # "2024-02-20"
    days: int = 0                 # 匹配天数
    change_pct: float = 0.0            # 区间涨幅
    kline: List[dict] = field(default_factory=list)  #KLine的字典
    params: List[dict] = field(default_factory=list)  #params的字典
    klineLength = 0



@dataclass
class KlineData:
    date: str = ""                     # "期 YYYY-MM-DD"
    open: float = 0.0            # 
    close: float = 0.0            # 
    high: float = 0.0            # 
    low: float = 0.0            # 
    volume: float = 0.0            # 
    turn: float = 0.0            # 
    change_Ratio: float = 0.0            # 

@dataclass
class Params:
    groups:List[dict] = field(default_factory=list) 

@dataclass
class Groups:
    name: str = ""                     # "分组"
    items: List[dict] = field(default_factory=list)  #KLine的字典
    
    
@dataclass
class Items:
    label: str = ""                     # "分组"
    value: float = ""                     # "分组"
    type: str = ""                     # "型: number|percent|text|currency
