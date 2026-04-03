"""
backend_kline_stream.py - 后端K线数据流式传输示例

支持两种模式：
1. WebSocket 流式传输（分块推送）
2. HTTP SSE 流式传输（备选方案）

依赖：websockets / fastapi / uvicorn
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class KlineItem:
    """单根K线数据"""
    date: str           # "2024-01-15"
    open: float
    close: float
    high: float
    low: float
    volume: float       # 成交量
    amount: float = 0   # 成交额（可选）
    turnover: float = 0 # 换手率（可选）


@dataclass
class StockParam:
    """单个参数"""
    label: str
    value: Any
    type: str = "text"  # text | number | percent | currency | market_cap


@dataclass
class StockParamGroup:
    """参数分组"""
    name: str
    items: List[StockParam] = field(default_factory=list)


@dataclass
class StockDetailResult:
    """个股详情完整结果"""
    code: str
    name: str
    industry: str
    kline: List[KlineItem] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    # params 格式：{ "groups": [ { "name": "xxx", "items": [...] } ] }


@dataclass
class SelectionStockItem:
    """选股结果中的单只股票"""
    code: str
    name: str
    score: float
    industry: str
    market_cap: float           # 流通市值
    change_3d: float = 0.0
    change_5d: float = 0.0
    change_10d: float = 0.0
    change_20d: float = 0.0
    change_40d: float = 0.0
    change_60d: float = 0.0
    change_120d: float = 0.0
    change_240d: float = 0.0
    # 详细参数（在选股结果列表中为概要，点击查看详情后填充完整参数）
    params: Optional[Dict[str, Any]] = None


@dataclass
class SelectionResult:
    """选股结果总体"""
    stocks: List[SelectionStockItem] = field(default_factory=list)
    total: int = 0
    timestamp: str = ""


# ============================================================
# WebSocket 流式传输 K线数据
# ============================================================

class KlineStreamService:
    """K线数据流式传输服务"""

    CHUNK_SIZE = 30  # 每次发送30根K线

    async def stream_kline_via_websocket(
        self, 
        ws,          # WebSocket 连接对象
        stock_code: str, 
        days: int = 240
    ):
        """
        通过 WebSocket 流式发送K线数据
        
        发送消息格式：
        {
            "type": "sc_kline_chunk",
            "msg": {
                "code": "600000",
                "chunk": [ {date, open, close, high, low, volume}, ... ],
                "progress": 0.5,      # 0~1
                "is_last": false,
                "total": 240
            }
        }
        """
        # 1. 从数据库/缓存中查询K线数据
        all_kline = await self._query_kline_data(stock_code, days)
        total = len(all_kline)
        
        if total == 0:
            # 发送空结果
            await ws.send(json.dumps({
                "type": "sc_kline_chunk",
                "msg": {
                    "code": stock_code,
                    "chunk": [],
                    "progress": 1.0,
                    "is_last": True,
                    "total": 0
                }
            }))
            return

        # 2. 分块发送
        sent = 0
        while sent < total:
            end = min(sent + self.CHUNK_SIZE, total)
            chunk = all_kline[sent:end]
            progress = end / total
            is_last = (end >= total)

            message = {
                "type": "sc_kline_chunk",
                "msg": {
                    "code": stock_code,
                    "chunk": [asdict(k) for k in chunk],
                    "progress": round(progress, 3),
                    "is_last": is_last,
                    "total": total
                }
            }

            await ws.send(json.dumps(message))
            sent = end

            # 适当延迟，避免浏览器消息堆积
            if not is_last:
                await asyncio.sleep(0.05)

        print(f"[KlineStream] {stock_code} 流式传输完成, 共 {total} 根K线")

    async def send_kline_full(
        self,
        ws,
        stock_code: str,
        days: int = 240
    ):
        """
        一次性发送全部K线数据（非流式，数据量小时使用）
        
        发送消息格式：
        {
            "type": "sc_kline_data",
            "msg": {
                "code": "600000",
                "kline": [ {date, open, close, high, low, volume}, ... ]
            }
        }
        """
        all_kline = await self._query_kline_data(stock_code, days)

        message = {
            "type": "sc_kline_data",
            "msg": {
                "code": stock_code,
                "kline": [asdict(k) for k in all_kline]
            }
        }

        await ws.send(json.dumps(message))
        print(f"[KlineFull] {stock_code} 发送完成, 共 {len(all_kline)} 根K线")

    async def _query_kline_data(
        self, 
        stock_code: str, 
        days: int
    ) -> List[KlineItem]:
        """
        查询K线数据（替换为你的实际数据查询逻辑）
        """
        # TODO: 替换为实际的数据库查询
        # 示例：从 pandas DataFrame 或数据库获取
        #
        # import pandas as pd
        # df = pd.read_sql(
        #     f"SELECT * FROM daily WHERE ts_code='{stock_code}' "
        #     f"ORDER BY trade_date DESC LIMIT {days}",
        #     engine
        # )
        # return [
        #     KlineItem(
        #         date=row['trade_date'],
        #         open=row['open'],
        #         close=row['close'],
        #         high=row['high'],
        #         low=row['low'],
        #         volume=row['vol']
        #     )
        #     for _, row in df.iterrows()
        # ]
        
        # 这里返回模拟数据用于演示
        import random
        result = []
        base_price = random.uniform(10, 50)
        for i in range(days):
            dt = datetime(2024, 1, 1) + __import__('datetime').timedelta(days=i)
            o = base_price + random.uniform(-1, 1)
            c = o + random.uniform(-2, 2)
            h = max(o, c) + random.uniform(0, 1)
            l = min(o, c) - random.uniform(0, 1)
            v = random.uniform(50000, 500000)
            base_price = c
            result.append(KlineItem(
                date=dt.strftime("%Y-%m-%d"),
                open=round(o, 2),
                close=round(c, 2),
                high=round(h, 2),
                low=round(l, 2),
                volume=round(v, 0)
            ))
        return result


# ============================================================
# WebSocket 消息路由（集成到你现有的消息处理中）
# ============================================================

kline_service = KlineStreamService()


async def handle_websocket_message(ws, message_type: str, payload: dict):
    """
    WebSocket 消息路由示例
    在你现有的消息分发逻辑中添加以下分支
    """
    if message_type == "cs_request_kline":
        code = payload.get("code", "")
        days = payload.get("days", 240)
        
        if days > 500:
            # 数据量大，使用流式传输
            await kline_service.stream_kline_via_websocket(ws, code, days)
        else:
            # 数据量小，一次性发送
            await kline_service.send_kline_full(ws, code, days)


# ============================================================
# 选股结果数据组装示例
# ============================================================

def build_selection_result(stock_data_list: list) -> dict:
    """
    组装选股结果数据，用于发送到前端
    
    返回格式:
    {
        "type": "sc_select_stocks_result",
        "msg": {
            "stocks": [
                {
                    "code": "600000",
                    "name": "浦发银行",
                    "score": 85.3,
                    "industry": "银行",
                    "market_cap": 1500000000,
                    "change_3d": 2.15,
                    "change_5d": 3.40,
                    "change_10d": -1.20,
                    "change_20d": 5.60,
                    "change_40d": 8.30,
                    "change_60d": 12.50,
                    "change_120d": -3.80,
                    "change_240d": 15.20,
                    "params": {
                        "groups": [
                            {
                                "name": "基本面",
                                "items": [
                                    {"label": "市盈率(PE)", "value": 6.52, "type": "number"},
                                    {"label": "市净率(PB)", "value": 0.45, "type": "number"},
                                    ...
                                ]
                            },
                            {
                                "name": "技术面",
                                "items": [...]
                            }
                        ]
                    }
                },
                ...
            ],
            "total": 120,
            "timestamp": "2025-01-15T10:30:00"
        }
    }
    """
    stocks = []
    for item in stock_data_list:
        stock = SelectionStockItem(
            code=item.get("code", ""),
            name=item.get("name", ""),
            score=item.get("score", 0),
            industry=item.get("industry", ""),
            market_cap=item.get("market_cap", 0),
            change_3d=item.get("change_3d", 0),
            change_5d=item.get("change_5d", 0),
            change_10d=item.get("change_10d", 0),
            change_20d=item.get("change_20d", 0),
            change_40d=item.get("change_40d", 0),
            change_60d=item.get("change_60d", 0),
            change_120d=item.get("change_120d", 0),
            change_240d=item.get("change_240d", 0),
            params=item.get("params", None)
        )
        stocks.append(stock)

    result = {
        "type": "sc_select_stocks_result",
        "msg": {
            "stocks": [asdict(s) for s in stocks],
            "total": len(stocks),
            "timestamp": datetime.now().isoformat()
        }
    }
    return result


def build_stock_detail_params(stock_code: str) -> dict:
    """
    构建个股详细参数示例
    
    你可以根据需要自定义分组和参数项
    预计100+参数可以分成多个组
    """
    return {
        "groups": [
            {
                "name": "📊 基本信息",
                "items": [
                    {"label": "股票代码", "value": stock_code, "type": "text"},
                    {"label": "上市日期", "value": "2000-01-01", "type": "text"},
                    {"label": "所属行业", "value": "银行", "type": "text"},
                    {"label": "所属概念", "value": "沪深300,MSCI", "type": "text"},
                ]
            },
            {
                "name": "💰 估值指标",
                "items": [
                    {"label": "市盈率(PE-TTM)", "value": 6.52, "type": "number"},
                    {"label": "市净率(PB)", "value": 0.45, "type": "number"},
                    {"label": "市销率(PS)", "value": 1.23, "type": "number"},
                    {"label": "市现率(PCF)", "value": 8.77, "type": "number"},
                    {"label": "股息率", "value": 5.23, "type": "percent"},
                    {"label": "总市值", "value": 280000000000, "type": "market_cap"},
                    {"label": "流通市值", "value": 150000000000, "type": "market_cap"},
                    {"label": "企业价值(EV)", "value": 320000000000, "type": "market_cap"},
                    {"label": "EV/EBITDA", "value": 4.56, "type": "number"},
                ]
            },
            {
                "name": "📈 盈利能力",
                "items": [
                    {"label": "ROE(加权)", "value": 12.35, "type": "percent"},
                    {"label": "ROA", "value": 0.89, "type": "percent"},
                    {"label": "ROIC", "value": 8.56, "type": "percent"},
                    {"label": "净利润率", "value": 32.45, "type": "percent"},
                    {"label": "毛利润率", "value": 45.67, "type": "percent"},
                    {"label": "营业利润率", "value": 38.90, "type": "percent"},
                    {"label": "净利润(TTM)", "value": 58000000000, "type": "market_cap"},
                    {"label": "营业收入(TTM)", "value": 180000000000, "type": "market_cap"},
                    {"label": "每股收益(EPS)", "value": 2.15, "type": "currency"},
                    {"label": "每股净资产(BPS)", "value": 18.56, "type": "currency"},
                ]
            },
            {
                "name": "📊 成长性",
                "items": [
                    {"label": "营收同比增长", "value": 8.56, "type": "percent"},
                    {"label": "净利润同比增长", "value": 12.34, "type": "percent"},
                    {"label": "营收环比增长", "value": 3.21, "type": "percent"},
                    {"label": "净利润环比增长", "value": 5.67, "type": "percent"},
                    {"label": "净资产同比增长", "value": 9.12, "type": "percent"},
                    {"label": "总资产同比增长", "value": 7.89, "type": "percent"},
                    {"label": "经营现金流增长", "value": 15.34, "type": "percent"},
                    {"label": "近3年营收CAGR", "value": 10.23, "type": "percent"},
                    {"label": "近3年利润CAGR", "value": 11.56, "type": "percent"},
                ]
            },
            {
                "name": "🏦 财务健康",
                "items": [
                    {"label": "资产负债率", "value": 92.34, "type": "percent"},
                    {"label": "流动比率", "value": 1.23, "type": "number"},
                    {"label": "速动比率", "value": 0.98, "type": "number"},
                    {"label": "利息覆盖倍数", "value": 2.56, "type": "number"},
                    {"label": "经营现金流/营收", "value": 28.90, "type": "percent"},
                    {"label": "自由现金流", "value": 25000000000, "type": "market_cap"},
                    {"label": "商誉占净资产比", "value": 1.23, "type": "percent"},
                ]
            },
            {
                "name": "📉 技术指标",
                "items": [
                    {"label": "最新收盘价", "value": 8.56, "type": "currency"},
                    {"label": "MA5", "value": 8.45, "type": "currency"},
                    {"label": "MA10", "value": 8.32, "type": "currency"},
                    {"label": "MA20", "value": 8.15, "type": "currency"},
                    {"label": "MA60", "value": 7.89, "type": "currency"},
                    {"label": "MA120", "value": 7.56, "type": "currency"},
                    {"label": "MA240", "value": 7.23, "type": "currency"},
                    {"label": "RSI(14)", "value": 55.67, "type": "number"},
                    {"label": "MACD-DIF", "value": 0.12, "type": "number"},
                    {"label": "MACD-DEA", "value": 0.08, "type": "number"},
                    {"label": "MACD柱", "value": 0.04, "type": "number"},
                    {"label": "KDJ-K", "value": 62.34, "type": "number"},
                    {"label": "KDJ-D", "value": 58.90, "type": "number"},
                    {"label": "KDJ-J", "value": 69.22, "type": "number"},
                    {"label": "布林上轨", "value": 9.12, "type": "currency"},
                    {"label": "布林中轨", "value": 8.45, "type": "currency"},
                    {"label": "布林下轨", "value": 7.78, "type": "currency"},
                    {"label": "ATR(14)", "value": 0.35, "type": "number"},
                    {"label": "量比", "value": 1.23, "type": "number"},
                    {"label": "换手率", "value": 0.89, "type": "percent"},
                    {"label": "5日均量", "value": 123456789, "type": "market_cap"},
                    {"label": "20日均量", "value": 98765432, "type": "market_cap"},
                ]
            },
            {
                "name": "📊 涨跌统计",
                "items": [
                    {"label": "3日涨跌幅", "value": 2.15, "type": "percent"},
                    {"label": "5日涨跌幅", "value": 3.40, "type": "percent"},
                    {"label": "10日涨跌幅", "value": -1.20, "type": "percent"},
                    {"label": "20日涨跌幅", "value": 5.60, "type": "percent"},
                    {"label": "40日涨跌幅", "value": 8.30, "type": "percent"},
                    {"label": "60日涨跌幅", "value": 12.50, "type": "percent"},
                    {"label": "120日涨跌幅", "value": -3.80, "type": "percent"},
                    {"label": "240日涨跌幅", "value": 15.20, "type": "percent"},
                    {"label": "年初至今涨跌幅", "value": 18.90, "type": "percent"},
                    {"label": "52周最高价", "value": 10.23, "type": "currency"},
                    {"label": "52周最低价", "value": 6.78, "type": "currency"},
                    {"label": "距52周高点", "value": -16.32, "type": "percent"},
                    {"label": "距52周低点", "value": 26.25, "type": "percent"},
                ]
            },
            {
                "name": "🔧 筛选因子得分",
                "items": [
                    # 这些是你的自定义因子打分
                    {"label": "综合得分", "value": 85.3, "type": "number"},
                    {"label": "价值因子得分", "value": 72.5, "type": "number"},
                    {"label": "成长因子得分", "value": 68.9, "type": "number"},
                    {"label": "动量因子得分", "value": 55.2, "type": "number"},
                    {"label": "质量因子得分", "value": 81.7, "type": "number"},
                    # ... 你可以根据需要添加更多
                ]
            }
        ]
    }