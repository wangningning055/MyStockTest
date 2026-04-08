
from typing import Literal, Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import src.main_code.Core.Select.Models as Models

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

class Msg_PartStock(BaseModel):
    id: str
    name: str
    weight: float
    holdingTimeMin : int
    holdingTimeMax : int
    stopLossPercent: float
    takeProfitPercent: float
    buyConfigTree: List[Models.FactorConfig]
    sellConfigTree: List[Models.FactorConfig]
    thresholdBuy : float
    thresholdSell : float
    drawdownStartPercent : float
    maxDrawdownPercent : float


class Msg_TotalStock(BaseModel):
    divisions : List[Msg_PartStock]
    initialFund : float
    pass

class Msg_Base(BaseModel):
    isExcludeST : bool
    isExcludeCY : bool
    isExcludeKC : bool
    start_date: str
    end_date:   str
    config: Msg_TotalStock
    timestamp: Optional[str] = None
    version: str = "1.0"




# ============================
# 数据结构定义
# ============================

@dataclass
class TradeSummary:
    """统计摘要"""
    initial_fund: float = 0.0          # 初始资金
    final_fund: float = 0.0            # 最终资金
    total_return: float = 0.0          # 总收益率 (%)
    win_rate: float = 0.0              # 胜率 (%)
    annual_return: float = 0.0         # 平均年化收益率 (%)
    annual_volatility: float = 0.0     # 年化波动率 (%)
    monthly_return: float = 0.0        # 平均月化收益率 (%)
    monthly_volatility: float = 0.0    # 月化波动率 (%)
    max_drawdown: float = 0.0          # 最大回撤 (%) 负数
    sharpe_ratio: float = 0.0          # 夏普比率


@dataclass
class Position:
    """每日持仓"""
    code: str = ""
    name: str = ""
    shares: int = 0


@dataclass
class TradeMarker:
    """买卖标记（用于曲线图上标注）"""
    date: str = ""                     # "2024-01-15"
    code: str = ""
    name: str = ""
    price: float = 0.0
    equity: float = 0.0                   # 标记点的净值（Y轴坐标）


@dataclass
class EquityCurve:
    """权益曲线"""
    dates: List[str] = field(default_factory=list)           # ["2024-01-01", ...]
    nav: List[float] = field(default_factory=list)           # 净值 [1.0, 1.02, ...]
    equity: List[float] = field(default_factory=list)           # 仓价 
    returns: List[float] = field(default_factory=list)       # 累计收益率 % [0, 2.0, ...]
    drawdown: List[float] = field(default_factory=list)      # 回撤 % [0, -1.5, ...]
    positions: List[List[dict]] = field(default_factory=list) # 每日持仓 [[{code,name,shares},...], ...]
    buy_markers: List[dict] = field(default_factory=list)    # 买入标记
    sell_markers: List[dict] = field(default_factory=list)   # 卖出标记


@dataclass
class KlineData:
    """单只股票K线数据（用于成交详情弹窗）"""
    dates: List[str] = field(default_factory=list)           # ["2024-01-01", ...]
    ohlc: List[List[float]] = field(default_factory=list)    # [[open,close,low,high], ...]  注意ECharts K线顺序
    volumes: List[float] = field(default_factory=list)       # 成交量


@dataclass
class TradeRecord:
    """单笔成交记录"""
    trade_id: str = ""                 # 唯一标识
    buy_date: str = ""                 # "2024-01-15"
    sell_date: str = ""                # "2024-02-20"
    hold_days: int = 0                 # 持仓天数
    code: str = ""                     # "600000"
    name: str = ""                     # "浦发银行"
    buy_price: float = 0.0             # 买入价
    sell_price: float = 0.0            # 卖出价
    profit_pct: float = 0.0            # 盈利百分比 (%)
    profit_money: float = 0.0          # 盈利金额 (元)
    sellReason: str = ""            # 卖出原因
    kline_data: Optional[dict] = None  # K线数据 (KlineData的dict形式)


@dataclass
class DivisionResult:
    """单个仓位（总仓或分仓）的回测结果"""
    division_name: str = ""
    summary: dict = field(default_factory=dict)      # TradeSummary 的 dict
    equity_curve: dict = field(default_factory=dict)  # EquityCurve 的 dict
    trades: List[dict] = field(default_factory=list)  # TradeRecord 的 dict 列表


@dataclass
class BacktestResult:
    """完整回测结果（总仓 + 所有分仓）"""
    total: dict = field(default_factory=dict)          # DivisionResult 的 dict
    divisions: Dict[str, dict] = field(default_factory=dict)  # {divisionId: DivisionResult的dict}
