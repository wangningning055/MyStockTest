# ws_routes.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from enum import Enum
import json
import asyncio
import datetime

from typing import TYPE_CHECKING
# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    from src.main_code.Core import Main

clients: set[WebSocket] = set()
mainProcessor : "Main.processor"
class MessageType(str, Enum):
    Log = "log"#服务器发送上次更新日期
    Test = "test"#测试
    SC_IN_BUSY = "sc_in_busy"               # #服务器返回是否忙碌
    SC_IN_PROGRESS = "sc_in_progress"       # #服务器返回进度
    LAST_UPDATE_DATA = "last_update_data_time"#服务器发送上次更新日期

    LAST_UPDATE_INDUSTRY = "last_update_data_industry"#服务器发送行业更新
    LAST_UPDATE_GROW_VALUE = "last_update_grow_value"#服务器发送价值成长股列表


    CS_UPDATE_DATA = "cs_update_data"               #客户端请求拉取数据
    CS_Stop_UPDATE_DATA = "cs_stop_update_data"               #客户端请求停止拉取数据
    CS_PREHEAT_DATA = "cs_preheat_data"               #客户端请求预热数据

    CS_INDUSTRY_ROTATION = "cs_industry_rotation",  # 客户端请求行业轮动分析
    SC_INDUSTRY_ROTATION = "sc_industry_rotation",  # 服务器返回行业轮动分析结果


    CS_QUERY_STOCKS = 'CS_QUERY_STOCKS',             # 客户端请求股票查询
    SC_QUERY_STOCKS_RESPONSE = 'SC_QUERY_STOCKS_RESPONSE',# 服务器返回股票查询结果


    CS_REQUEST_KLINE = 'cs_request_kline',      # 请求K线数据

    SC_KLINE_CHUNK = 'sc_kline_chunk',           # 流式K线数据块
    SC_KLINE_DATA = 'sc_kline_data',             # 一次性K线数据




    CS_SELECT_STOCKS = "cs_select_stocks"           #客户端请求执行股票筛选
    SC_SELECT_STOCKS = "sc_select_stocks",            # 客户端返回股票筛选



    CS_BACK_TEST = "cs_back_test"                   #客户端请求执行回测
    SC_BACK_TEST = "sc_back_test"                   #服务器返回回测
    CS_BACK_TEST_STOP = "cs_back_test_stop"                   #客户端请求停止回测









    CS_DIAGNOSE = "cs_diagnose"                     #客户端请求出仓判断


##发送消息
async def SendMessage(msg_type, content):
    print(f"发送消息：{msg_type}")
    data = json.dumps({"type": msg_type, "msg": content}, ensure_ascii=False, indent=2)


    dead_ws = []

    for ws in clients:
        try:
            await ws.send_text(data)
        except RuntimeError:
            # ws 已关闭
            print(f"发送失败1：{msg_type}")
            dead_ws.append(ws)
        except Exception as e:
            print(f"发送失败2：{msg_type}")
            dead_ws.append(ws)

    # 统一清理
    for ws in dead_ws:
        clients.remove(ws)


async def safe_send(*args):
    try:
        await SendMessage(*args)
    except Exception as e:
        print("发送消息失败:", e)


def SendMessage_A(*args):
    asyncio.get_running_loop().create_task(safe_send(*args))
    


## 广播函数
async def broadcast(message: str):

    data = json.dumps({"type": "log", "msg": message})
    dead = set()
    clients_copy = list(clients)

    for ws in clients_copy:
        try:
            #print(f"log测试：{message}")
            await ws.send_text(data)
        except Exception:
            dead.add(ws)

    for ws in dead:
        clients.discard(ws)





#async def broadcast(message: str):
#    print("广播消息：",json.dumps({"type": "ping", "msg": message}))
#    for client in clients:
#        await client.send_text(json.dumps({"type": "ping", "msg": message}))

def register_ws(app: FastAPI):
    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        clients.add(ws)
        await ws.accept()
        print("客户端已连接")
        SendLastUpdateTime()
        SendLastUpdateIndustry()
        SendLastUpdateIndustryRotation()
        try:
            while True:
                data = await ws.receive_text()
                #print("收到前端:", data)
                msg = json.loads(data)
                HandleMsg(msg)
        except WebSocketDisconnect:
            print("客户端断开连接")

#发送上次更新日期
def SendLastUpdateTime():
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_DATA, mainProcessor.recordHandler.GetRecentRequestDateJsonStr()))

#发送行业列表
def SendLastUpdateIndustry():
    asyncio.get_running_loop().create_task(safe_send(MessageType.LAST_UPDATE_INDUSTRY,mainProcessor.recordDataCls.industry_list))
    

def SendLastUpdateIndustryRotation():
    print("发送行业轮动分析结果")
    asyncio.get_running_loop().create_task(safe_send(MessageType.SC_INDUSTRY_ROTATION,mainProcessor.recordDataCls.industry_Increase_Month_Dic))


    #for key, value in tempDic.items():
    #    print(f"行业：{key[0]}， 月份：{key[1]}， 出现次数：{value}")

def HandleMsg(msg):
    if(mainProcessor == None):
        print("主程序没有初始化完成")
        return
    if(mainProcessor.isInit == False):
        mainProcessor.BoardCast("主程序没有初始化完成")
        print("主程序没有初始化完成")
        return
    msgType = msg["type"]
    if(msgType == MessageType.Test):
        print("进行数据测试")
        mainProcessor.ExecuteTest()

    if(msgType == MessageType.CS_Stop_UPDATE_DATA):
        print("停止拉取或预热数据")
        mainProcessor.requestor.StopRequest()
        mainProcessor.StopTest()
        return
    
    elif(msgType == MessageType.CS_BACK_TEST_STOP):
        print("停止回测")
        mainProcessor.backTestHandle.StopBackTest()



    if(mainProcessor.isInHandle == True):
        mainProcessor.BoardCast("正在处理，等待处理完成")
        print("正在处理，等待处理完成")
        return


    print("处理消息，消息类型是：" + msg["type"])
    msgType = msg["type"]
    data = msg["payload"]

    if(msgType == MessageType.CS_UPDATE_DATA):
        mainProcessor.tuShareToken = data["token"]
        update_Type = data["type"]
        mainProcessor.requestor.StartRequest(update_Type)
    
    elif(msgType == MessageType.LAST_UPDATE_DATA):
        print("请求最近的更新日期")
        SendLastUpdateTime()

    elif(msgType == MessageType.CS_SELECT_STOCKS):
        print("处理选股消息")
        mainProcessor.analysisHandle.RunGetStockListByCondition(data)


    elif(msgType == MessageType.CS_PREHEAT_DATA):
        print("进行数据预热")
        task = asyncio.get_running_loop().create_task(mainProcessor.calculationDataHandle.DataPreheating())


    #需要修改成行业轮动分析
    elif(msgType == MessageType.CS_INDUSTRY_ROTATION):
        print("进行行业分析")
        mainProcessor.calculationDataHandle.AnalyzeIndustry()
        



    elif(msgType == MessageType.CS_BACK_TEST):
        print(f"执行回测, 收到的回测消息：{data}")
        task = asyncio.get_running_loop().create_task(mainProcessor.backTestHandle.CreateStockByJson(data))





    elif(msgType == MessageType.CS_DIAGNOSE):
        pass

    elif(msgType == MessageType.CS_QUERY_STOCKS):
        mainProcessor.analysisHandle.SearchStock(data)
        pass
    
    elif(msgType == MessageType.CS_REQUEST_KLINE):
        mainProcessor.analysisHandle.HandleKLineResponse(data)
        pass




#"""
#pattern_match_protocol.py - 模式匹配前后端通信协议

#前端 → 后端消息类型：
#  - cs_pattern_match          : 请求模式匹配
#  - cs_pattern_export_params  : 请求参数导出(均值/中位数/聚合)

#后端 → 前端消息类型：
#  - sc_pattern_match          : 返回匹配结果
#  - sc_pattern_export_params  : 返回参数导出结果
#"""

## ============================================================
## 1. 前端 → 后端：模式匹配请求
## ============================================================
## 消息类型: "cs_pattern_match"
## 前端发送的 payload 结构:
#CS_PATTERN_MATCH_REQUEST = {
#    "start_date": "20200101",        # str, YYYYMMDD, 匹配搜索起始日期
#    "end_date": "20250101",          # str, YYYYMMDD, 可为空字符串表示到最新
#    "conditions": [                   # list, 匹配条件组(多条件AND关系)
#        {
#            "days_min": 1,            # int, 天数区间最小值
#            "days_max": 30,           # int, 天数区间最大值
#            "change_min": 100.0,      # float|None, 涨幅最小值(%), None表示不限
#            "change_max": None,       # float|None, 涨幅最大值(%), None表示不限
#        },
#        # 可以有多组条件...
#    ],
#    "exclude_st": True,              # bool, 是否排除ST
#    "exclude_kc": True,              # bool, 是否排除科创板
#    "exclude_cy": True,              # bool, 是否排除创业板
#    "timestamp": "2025-01-01T00:00:00.000Z"  # str, 请求时间戳
#}


## ============================================================
## 2. 后端 → 前端：模式匹配结果
## ============================================================
## 消息类型: "sc_pattern_match"
## 后端返回的 msg 结构:
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


## ============================================================
## 3. 前端 → 后端：参数导出请求
## ============================================================
## 消息类型: "cs_pattern_export_params"
#CS_PATTERN_EXPORT_PARAMS_REQUEST = {
#    "export_type": "mean",           # str, 导出类型: "mean"|"median"|"aggregate"
#    "matches": [                      # list, 匹配记录列表(只传标识信息)
#        {
#            "code": "600000",         # str, 股票代码
#            "match_start": "2024-01-05",  # str, 匹配开始
#            "match_end": "2024-02-03",    # str, 匹配结束
#        },
#        # ...
#    ],
#    "timestamp": "2025-01-01T00:00:00.000Z"
#}


## ============================================================
## 4. 后端 → 前端：参数导出结果
## ============================================================
## 消息类型: "sc_pattern_export_params"
#SC_PATTERN_EXPORT_PARAMS_RESPONSE = {
#    "export_type": "mean",           # str, 导出类型
#    "params": [                       # list, 参数列表
#        {
#            "name": "市盈率(PE)",      # str, 参数名称
#            "value": 25.67            # float, 参数值(均值/中位数/聚合值)
#        },
#        {
#            "name": "市净率(PB)",
#            "value": 2.34
#        },
#        # ...
#    ]
#}


"""
pattern_match_handler.py - 模式匹配后端处理器

接入方法：
1. 在 WebSocket 消息分发器中注册 "cs_pattern_match" 和 "cs_pattern_export_params"
2. 实现 handle_pattern_match() 和 handle_pattern_export_params()
3. 通过 ws.send() 将结果发回前端
"""

#import json
#import numpy as np
#from datetime import datetime, timedelta


#class PatternMatchHandler:
#    """模式匹配处理器"""

#    def __init__(self, data_manager):
#        """
#        data_manager: 你的数据管理器实例，需提供以下接口:
#            - get_stock_list()       → 返回所有股票列表
#            - get_daily_data(code)   → 返回某只股票的日线数据DataFrame
#            - get_value_data(code)   → 返回某只股票的价值数据
#        """
#        self.dm = data_manager

#    def handle_pattern_match(self, payload: dict) -> dict:
#        """
#        处理模式匹配请求

#        Args:
#            payload: 前端发送的请求数据，结构见 CS_PATTERN_MATCH_REQUEST

#        Returns:
#            dict: 匹配结果，结构见 SC_PATTERN_MATCH_RESPONSE
#        """
#        start_date = payload.get('start_date', '')
#        end_date = payload.get('end_date', '')
#        conditions = payload.get('conditions', [])
#        exclude_st = payload.get('exclude_st', True)
#        exclude_kc = payload.get('exclude_kc', True)
#        exclude_cy = payload.get('exclude_cy', True)

#        # 1. 获取股票列表（根据筛选条件过滤）
#        stocks = self.dm.get_stock_list()
#        if exclude_st:
#            stocks = [s for s in stocks if 'ST' not in s.get('name', '')]
#        if exclude_kc:
#            stocks = [s for s in stocks if not s['code'].startswith('688')]
#        if exclude_cy:
#            stocks = [s for s in stocks if not s['code'].startswith('300')]

#        # 2. 遍历股票，执行匹配
#        all_matches = []
#        for stock in stocks:
#            code = stock['code']
#            name = stock.get('name', '')

#            # 获取日线数据
#            daily = self.dm.get_daily_data(code)
#            if daily is None or len(daily) == 0:
#                continue

#            # 在日期范围内搜索
#            matches = self._find_matches(
#                code, name, daily,
#                start_date, end_date, conditions
#            )
#            all_matches.extend(matches)

#        return {"matches": all_matches}

#    def _find_matches(self, code, name, daily, start_date, end_date, conditions):
#        """
#        在单只股票上执行匹配逻辑

#        思路：
#        - 遍历每个交易日作为潜在的匹配起点
#        - 对每个条件组，检查从起点开始的 days_min ~ days_max 范围内
#          是否存在满足涨幅条件的终点
#        - 所有条件组都满足时，记录为一次匹配
#        """
#        matches = []
#        dates = daily['date'].tolist()  # 假设日期已排序
#        closes = daily['close'].tolist()

#        for i in range(len(dates)):
#            cur_date = dates[i]

#            # 日期范围检查
#            if start_date and cur_date < start_date:
#                continue
#            if end_date and cur_date > end_date:
#                continue

#            # 检查所有条件是否都能满足
#            all_satisfied = True
#            best_end_idx = i  # 记录最远的匹配终点

#            for cond in conditions:
#                days_min = cond.get('days_min', 1)
#                days_max = cond.get('days_max', 30)
#                change_min = cond.get('change_min')
#                change_max = cond.get('change_max')

#                cond_satisfied = False
#                for j in range(i + days_min, min(i + days_max + 1, len(dates))):
#                    change = (closes[j] - closes[i]) / closes[i] * 100

#                    min_ok = change_min is None or change >= change_min
#                    max_ok = change_max is None or change <= change_max

#                    if min_ok and max_ok:
#                        cond_satisfied = True
#                        best_end_idx = max(best_end_idx, j)
#                        break

#                if not cond_satisfied:
#                    all_satisfied = False
#                    break

#            if all_satisfied and best_end_idx > i:
#                match_start = dates[i]
#                match_end = dates[best_end_idx]
#                days = best_end_idx - i
#                change_pct = (closes[best_end_idx] - closes[i]) / closes[i] * 100

#                # 获取K线数据（前后各60天）
#                kline_start = max(0, i - 60)
#                kline_end = min(len(dates), best_end_idx + 60)
#                kline_data = []
#                for k in range(kline_start, kline_end):
#                    row = daily.iloc[k]
#                    kline_data.append({
#                        "date": str(row['date']),  # 转换日期格式
#                        "open": float(row['open']),
#                        "close": float(row['close']),
#                        "high": float(row['high']),
#                        "low": float(row['low']),
#                        "volume": int(row.get('volume', 0)),
#                        "turn": float(row.get('turn', 0)),
#                        "change_Ratio": float(row.get('change_pct', 0)),
#                    })

#                # 获取参数（★ 此处自行扩展 ★）
#                params = self._get_stock_params(code, match_start)

#                matches.append({
#                    "code": code,
#                    "name": name,
#                    "match_start": self._format_date(match_start),
#                    "match_end": self._format_date(match_end),
#                    "days": days,
#                    "change_pct": round(change_pct, 2),
#                    "kline": kline_data,
#                    "params": params
#                })

#        return matches

#    def _get_stock_params(self, code, date) -> dict:
#        """
#        获取股票参数（★ 此处自行扩展 ★）

#        返回格式:
#        {
#            "groups": [
#                { "name": "分组名", "items": [{ "label": "名", "value": 值, "type": "number" }] },
#                ...
#            ]
#        }
#        """
#        # 示例：从 data_manager 获取价值数据
#        # value_data = self.dm.get_value_data(code)

#        return {
#            "groups": [
#                {
#                    "name": "基本信息",
#                    "items": [
#                        # ★ 在此添加你需要的参数 ★
#                        # {"label": "市盈率", "value": value_data.get('pe', 0), "type": "number"},
#                        # {"label": "市净率", "value": value_data.get('pb', 0), "type": "number"},
#                    ]
#                }
#            ]
#        }

#    def _format_date(self, date_str):
#        """将 YYYYMMDD 格式转为 YYYY-MM-DD"""
#        if len(date_str) == 8:
#            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
#        return date_str

#    def handle_pattern_export_params(self, payload: dict) -> dict:
#        """
#        处理参数导出请求

#        Args:
#            payload: 前端发送的请求数据，结构见 CS_PATTERN_EXPORT_PARAMS_REQUEST

#        Returns:
#            dict: 导出结果，结构见 SC_PATTERN_EXPORT_PARAMS_RESPONSE
#        """
#        export_type = payload.get('export_type', 'mean')
#        match_list = payload.get('matches', [])

#        # 1. 收集所有匹配记录的参数
#        all_param_values = {}  # { param_name: [value1, value2, ...] }

#        for match_info in match_list:
#            code = match_info['code']
#            match_start = match_info['match_start']

#            # 获取该股票在匹配时间点的参数
#            params = self._get_stock_params(code, match_start)
#            if params and 'groups' in params:
#                for group in params['groups']:
#                    for item in group.get('items', []):
#                        name = item['label']
#                        value = item['value']
#                        if isinstance(value, (int, float)):
#                            if name not in all_param_values:
#                                all_param_values[name] = []
#                            all_param_values[name].append(value)

#        # 2. 计算统计值
#        result_params = []
#        for name, values in all_param_values.items():
#            if len(values) == 0:
#                continue

#            if export_type == 'mean':
#                stat_value = float(np.mean(values))
#            elif export_type == 'median':
#                stat_value = float(np.median(values))
#            elif export_type == 'aggregate':
#                # 聚合：返回均值、中位数、标准差等
#                stat_value = {
#                    "mean": float(np.mean(values)),
#                    "median": float(np.median(values)),
#                    "std": float(np.std(values)),
#                    "min": float(np.min(values)),
#                    "max": float(np.max(values)),
#                    "count": len(values)
#                }
#            else:
#                stat_value = float(np.mean(values))

#            result_params.append({
#                "name": name,
#                "value": stat_value
#            })

#        return {
#            "export_type": export_type,
#            "params": result_params
#        }


## ============================================================
## WebSocket 消息分发器中的接入代码
## ============================================================
#"""
#在你的 WebSocket 消息处理函数中添加：

## 初始化（在服务启动时）
#pattern_handler = PatternMatchHandler(data_manager)

## 消息分发（在 on_message 中）
#if msg_type == 'cs_pattern_match':
#    result = pattern_handler.handle_pattern_match(payload)
#    ws.send(json.dumps({
#        "type": "sc_pattern_match",
#        "msg": result
#    }))

#elif msg_type == 'cs_pattern_export_params':
#    result = pattern_handler.handle_pattern_export_params(payload)
#    ws.send(json.dumps({
#        "type": "sc_pattern_export_params",
#        "msg": result
#    }))
#"""


