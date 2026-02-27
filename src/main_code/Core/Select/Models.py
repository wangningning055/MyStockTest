"""
models.py - 数据模型定义
定义所有API请求和响应的数据结构
"""

from typing import Literal, Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ConditionNode(BaseModel):
    """条件节点 - 表示一个具体的因子条件"""
    type: Literal['condition'] = 'condition'
    relation: Literal['START', 'AND', 'OR'] = 'START'
    factor_name: str  # 因子名称，与factors.json中的name字段对应
    factor_id: int  
    operator: Literal['gt', 'lt', 'eq', 'ge', 'le']  # 比较操作符
    value: float  # 条件值
    dateFrom: int = Field(default=30, description="起始天数（天前）")
    dateTo: int = Field(default=0, description="结束天数（天前）")

    #class Config:
    #    json_schema_extra = {
    #        "example": {
    #            "type": "condition",
    #            "relation": "START",
    #            "factor_name": "3日放量增长条件",
    #            "operator": "eq",
    #            "value": 1,
    #            "dateFrom": 30,
    #            "dateTo": 0
    #        }
    #    }


class GroupNode(BaseModel):
    """分组节点 - 表示多个条件的组合"""
    type: Literal['group'] = 'group'
    relation: Literal['START', 'AND', 'OR'] = 'START'
    children: List['TreeNode']

    #class Config:
    #    json_schema_extra = {
    #        "example": {
    #            "type": "group",
    #            "relation": "OR",
    #            "children": [
    #                {
    #                    "type": "condition",
    #                    "relation": "START",
    #                    "factor_name": "因子1",
    #                    "operator": "gt",
    #                    "value": 10
    #                }
    #            ]
    #        }
    #    }


# 定义递归类型
TreeNode = Union[ConditionNode, GroupNode]
GroupNode.update_forward_refs()


class FactorConfig(BaseModel):
    """因子配置 - 表示一个完整的选股因子"""
    factor_group_name: str  # 因子组名称（用户自定义）
    weight: float = Field(ge=0, description="权重（0-100）")
    logic_tree: List[TreeNode]  # 树形条件结构

    #class Config:
    #    json_schema_extra = {
    #        "example": {
    #            "factor_group_name": "3日放量增长条件",
    #            "weight": 0.4,
    #            "logic_tree": [
    #                {
    #                    "type": "condition",
    #                    "relation": "START",
    #                    "factor_name": "3日放量增长条件",
    #                    "operator": "eq",
    #                    "value": 1
    #                }
    #            ]
    #        }
    #    }


class SelectionRequest(BaseModel):
    """选股请求"""
    configs: List[FactorConfig]
    timestamp: Optional[str] = None
    version: str = "1.0"


class BacktestRequest(BaseModel):
    """回测请求"""
    buy_configs: List[FactorConfig]
    sell_configs: Optional[List[FactorConfig]] = None
    initial_fund: float = Field(default=100000, ge=0)
    start_date: str = Field(description="开始日期，格式YYYYMMDD")
    end_date: str = Field(description="结束日期，格式YYYYMMDD")
    is_ideal: bool = False
    timestamp: Optional[str] = None
    version: str = "1.0"


class DiagnoseRequest(BaseModel):
    """出仓判断请求"""
    holdings: List[Dict[str, Any]]  # 持仓列表
    sell_configs: Optional[List[FactorConfig]] = None
    timestamp: Optional[str] = None
    version: str = "1.0"


class FactorsMetadata(BaseModel):
    """因子元数据"""
    id: int
    name_field: str  # 数据库字段名
    name: str  # 显示名称
    type: str  # 数据类型
    description: str


# ==================== 响应模型 ====================

class StockResult(BaseModel):
    """选股结果中的单只股票"""
    code: str
    name: str
    score: float
    industry: Optional[str] = None


class SelectionResult(BaseModel):
    """选股结果"""
    success: bool = True
    timestamp: str
    total: int
    stocks: List[StockResult]
    industryAnalysis: Optional[Dict[str, Any]] = None


class BacktestResult(BaseModel):
    """回测结果"""
    success: bool = True
    timestamp: str
    totalReturn: float
    winRate: float
    maxDrawdown: float
    shapreRatio: float
    klineData: Optional[List[Dict[str, Any]]] = None
    portfolioData: Optional[Dict[str, Any]] = None


class DiagnoseResult(BaseModel):
    """出仓判断结果"""
    code: str
    name: str
    should_sell: bool
    score: float
    reason: Optional[str] = None


class DiagnoseResponse(BaseModel):
    """出仓判断响应"""
    success: bool = True
    timestamp: str
    results: List[DiagnoseResult]