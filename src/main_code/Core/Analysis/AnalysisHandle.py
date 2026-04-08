from src.main_code.Core.Select.Models import SelectionRequest
from src.main_code.Core.Select.ConditionEvaluator import FactorEvaluator, load_factors_metadata
from src.main_code.Core.Const import FactorsJsonPath
from src.main_code.Core import Main
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from src.main_code.Core.DataStruct.Base import CalculationDataStruct
import src.main_code.Core.Calculate.CalculationDataHandle as CalculationDataHandle
import src.main_code.Core.Const as const
import time
import psutil
import os
from datetime import datetime
FACTORS_METADATA = None
class BaseClass :
    def Init(self, main):
        self.main : Main.processor  = main
    def __init__(self):
        global FACTORS_METADATA
        FACTORS_METADATA = load_factors_metadata(FactorsJsonPath)
        self.isOutST = True             #是否剔除ST股票
        self.isOutST = True             #是否剔除ST股票
        self.isOutCY = True             #是否剔除创业板股票
        self.isOutKC = True             #是否剔除科创板股票
        self.isOnlyValue = False          #是否只计算价值股
        self.isOnlyGrow = False           #是否只计算成长股
        self.factorLimit = 0.5                 #条件因子筛选的边界值，默认为0.5，即大于0.5则满足条件，小于0.5则不满足条件
        self.evaluator = None


    #个股条件因子计算和筛选
    def RunGetStockListByCondition(self, conditionJson):
        print(f"开始进行条件筛选: {conditionJson}")
        evaluator : FactorEvaluator = FactorEvaluator(FACTORS_METADATA)
        evaluator.SetMain(self.main)
        evaluator.SetCalculationHandle(self.main.calculationDataHandle)
        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)

        try:
            # Pydantic自动验证并转换
            print("")
            print("")
            print("")
            request = SelectionRequest(**conditionJson)
            print(request)
            self.isOutST = request.isExcludeST
            self.isOutCY = request.isExcludeCY
            self.isOutKC = request.isExcludeKC
            self.isOnlyValue = request.isExclude_Value
            self.isOnlyGrow = request.isExclude_Grow
            self.threshold = request.threshold
            print(f"✅ 数据验证成功:ST:{self.isOutST}    cy:{self.isOutCY}   ke:  {self.isOutKC}  value:{self.isOnlyValue}    grow:  {self.isOnlyGrow}")
            #print(f"   配置数: {len(request.configs)}")
            #print(f"   第一个因子: {request.configs[0].factor_group_name}")
            #print(f"   权重: {request.configs[0].weight}")
            #print(f"   条件数: {len(request.configs[0].logic_tree)}")
            #print(f"   权重阈值: {request.threshold}")
        except Exception as e:
            print(f"❌ 数据验证失败: {e}")

        
        listCode = []
        count = 1
        t0 = time.perf_counter()
        for val, single in self.main.calculationDataHandle.totalComponyIns.allStockList.items():
            #如果状态不是成交状态就跳过
            todayStr = self.main.todayStockDate
            cls = self.main.calculationDataHandle.GetBaseDataClass(val, todayStr ,False)
            if cls == None:
                continue

            if cls.trade_state != 1:
                #print(f"股票{cls.componyInfo.Name}：{val} 在 {todayStr} 停牌，不执行")
                continue
            if len(cls.dataList_240) < 10:
                #print(f"股票{cls.componyInfo.Name}：{val} 新上市交易日不足十天，跳过")
                continue
            if self.isOutST == True:
                if cls.isST == 1:
                    continue
            if self.isOutKC == True:
                if const.GetIsKC(val):
                    continue
            if self.isOutCY == True:
                if const.GetIsCy(val):
                    continue
            score = evaluator.evaluate_stock(val, request.configs)
            
            # 获取内存使用信息（以字节为单位）
            mem_info = process.memory_info()
            
            # 转换为MB（1MB = 1024 * 1024 字节）
            rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
            vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小

            print(f"✅ 个股评分（-100， 100）: {score}, 第{count}个，总共：{len(self.main.calculationDataHandle.totalComponyIns.allStockList)}个, code:{val}      {cls.componyInfo.Name}, 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            count += 1
            #if count > 100:
            #    break
            if score >= self.threshold * 100:
                res = (val, score)
                listCode.append(res)
        print("=======================================选股结果==============================================")
        for resSingle in listCode:
            componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(resSingle[0])
            print(f"{componyInfo.Code}, {componyInfo.Name},  {componyInfo.Industry}")

            
        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        
        print(f"结果长度：: {len(listCode)}， 花费时间：{totalCostTimeStr1}")
        self.CreateSelectStockResponse(listCode)



    def InitEvaluator(self, calculationHandle : CalculationDataHandle.BaseClass):
        evaluator : FactorEvaluator = FactorEvaluator(FACTORS_METADATA)
        evaluator.SetMain(self.main)
        evaluator.SetCalculationHandle(calculationHandle)
        self.evaluator = evaluator

    #用于回测的个股条件因子计算和筛选
    def RunGetStockListByConditionForBackTest(self, calculationHandle : CalculationDataHandle.BaseClass, codeList, threshold, isOutKC, isOutCY, isOutST,  configsData, isBuy = True):
        if(self.evaluator == None):
            print("评估器未初始化，正在初始化")
            self.InitEvaluator(calculationHandle)


        listCode = []
        res = {}
        count = 1
        for val in codeList:
            #如果状态不是成交状态就跳过
            todayStr = calculationHandle.todayStr
            cls = calculationHandle.GetBaseDataClass(val, todayStr ,False)

            if cls == None:
                continue

            if cls.trade_state != 1:
                #print(f"股票{cls.componyInfo.Name}：{val} 在 {todayStr} 停牌，不执行")
                continue


            if len(cls.dataList_240) < 10:
                continue

            if isOutST == True:
                if cls.isST == 1:
                    continue
            if isOutKC == True:
                if const.GetIsKC(val):
                    continue
            if isOutCY == True:
                if const.GetIsCy(val):
                    continue
            score =  self.evaluator.evaluate_stock(val, configsData)
            
  
            #print(f"✅ 个股评分（-100， 100）: {score}, 第{count}个，总共：{len(codeList)}个, code:{val}      {cls.componyInfo.Name}, 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            count += 1
            #if count > 100:
            #    break
            if score >= threshold * 100:
                listCode.append(val)
                res[score] = val

        #print("=======================================选股结果==============================================")
        #for code in listCode:
        #    componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
            #print(f"{componyInfo.Code}, {componyInfo.Name},  {componyInfo.Industry}")



        return res



    ## 构建股票查询的响应
    #response = {
    #    'query_type': query_type,
    #    'query_value': query_value,
    #    'stocks': [
    #        {
    #            'code': stock.code,
    #            'name': stock.name,
    #            'market_cap': float(stock.market_cap),
    #            'change_3d': float(stock.change_3d),
    #            'change_5d': float(stock.change_5d),
    #            'change_10d': float(stock.change_10d),
    #            'change_20d': float(stock.change_20d),
    #            'change_40d': float(stock.change_40d),
    #            'change_60d': float(stock.change_60d),
    #            'change_120d': float(stock.change_120d),
    #            'change_240d': float(stock.change_240d),
    #            'company_type': stock.company_type,
    #            'company_name': stock.company_name,
    #            'main_products': stock.main_products,
    #            'business_scope': stock.business_scope,
    #            'company_description': stock.company_description
    #        }
    #        for stock in stocks
    #    ],
    #    'timestamp': datetime.now().isoformat()
    #}




    #选股数据结构

    """
============================================================
前后端数据结构契约文档
============================================================

1. 选股结果 (sc_select_stocks_result)
============================================================
"""


## 后端返回：
#    "msg": {
#        "stocks": [
#            {
#                "code": "600000",            # str: 6位股票代码
#                "name": "浦发银行",           # str: 股票名称
#                "score": 85.30,              # float: 筛选综合得分
#                "industry": "银行",           # str: 所属行业
#                "market_cap": 150000000000,  # float: 流通市值(元)
#                "change_3d": 2.15,           # float: 3日涨跌幅(%)
#                "change_5d": 3.40,           # float: 5日涨跌幅(%)
#                "change_10d": -1.20,         # float: 10日涨跌幅(%)
#                "change_20d": 5.60,          # float: 20日涨跌幅(%)
#                "change_40d": 8.30,          # float: 40日涨跌幅(%)
#                "change_60d": 12.50,         # float: 60日涨跌幅(%)
#                "change_120d": -3.80,        # float: 120日涨跌幅(%)
#                "change_240d": 15.20,        # float: 240日涨跌幅(%)
#                "params": {                  # dict: 详细参数(可选,可在请求K线时返回)
#                    "groups": [
#                        {
#                            "name": "分组名称",  # str: 参数分组名
#                            "items": [
#                                {
#                                    "label": "参数名",      # str: 参数显示名
#                                    "value": 12.34,         # any: 参数值
#                                    "type": "number"        # str: text|number|percent|currency|market_cap
#                                }
#                            ]
#                        }
#                    ]
#                }
#            }
#        ],
#        "total": 120,                        # int: 总数量
#        "timestamp": "2025-01-15T10:30:00"   # str: 时间戳
#    }


    def CreateSelectStockResponse(self, codeList):
        response = {}
        total = len(codeList)
        response["total"] = total
        response["timestamp"] = "2025-01-15T10:30:00"
        response["stocks"] = []
        for resSingle in codeList:
            code = resSingle[0]
            score = resSingle[1]
            cls = self.main.calculationDataHandle.GetBaseDataClass_WithTradeState(code ,self.main.todayStockDate)
            componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
            industryCls = self.main.calculationDataHandle.totalComponyIns.GetIndustryClsByCode(code)
            single = {
                "code": cls.code,            # str: 6位股票代码
                "name": componyInfo.Name,           # str: 股票名称
                "score": score,              # float: 筛选综合得分
                "industry": industryCls.industryName,           # str: 所属行业
                "market_cap": cls.total_value / 100000000,  # float: 流通市值(亿元)
                "change_3d": cls.change_Ratio_single_3,           # float: 3日涨跌幅(%)
                "change_5d": cls.change_Ratio_single_5,           # float: 5日涨跌幅(%)
                "change_10d": cls.change_Ratio_single_10,         # float: 10日涨跌幅(%)
                "change_20d": cls.change_Ratio_single_20,          # float: 20日涨跌幅(%)
                "change_40d": cls.change_Ratio_single_40,          # float: 40日涨跌幅(%)
                "change_60d": cls.change_Ratio_single_60,         # float: 60日涨跌幅(%)
                "change_120d": cls.change_Ratio_single_120,        # float: 120日涨跌幅(%)
                "change_240d": cls.change_Ratio_single_240,        # float: 240日涨跌幅(%)
                "params": {                  # dict: 详细参数(可选,可在请求K线时返回)
                "groups": [
                    {
                        "name": "基础标识",
                        "items": [
                            {
                                "label": "股票代码",
                                "value": cls.code,
                                "type": "text"
                            },
                            {
                                "label": "交易日期",
                                "value": cls.trade_date,
                                "type": "text"
                            },
                            {
                                "label": "所属行业",
                                "value": cls.industry,
                                "type": "text"
                            },
                            {
                                "label": "是否ST",
                                "value": cls.isST,
                                "type": "number"
                            },
                            {
                                "label": "交易状态",
                                "value": cls.trade_state,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "股票评分",
                        "items": [
                            {
                                "label": "价值股评分",
                                "value": cls.ValueScore,
                                "type": "number"
                            },
                            {
                                "label": "成长股评分",
                                "value": cls.GrowScore,
                                "type": "number"
                            },
                            {
                                "label": "是否行业上涨周期",
                                "value": cls.isInIndustryUp,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "价格数据(复权)",
                        "items": [
                            {
                                "label": "开盘价",
                                "value": cls.open,
                                "type": "number"
                            },
                            {
                                "label": "收盘价",
                                "value": cls.close,
                                "type": "number"
                            },
                            {
                                "label": "昨收价",
                                "value": cls.last_close,
                                "type": "number"
                            },
                            {
                                "label": "最高价",
                                "value": cls.high,
                                "type": "number"
                            },
                            {
                                "label": "最低价",
                                "value": cls.low,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "价格数据(原始)",
                        "items": [
                            {
                                "label": "开盘价(原始)",
                                "value": cls.open_ori,
                                "type": "number"
                            },
                            {
                                "label": "收盘价(原始)",
                                "value": cls.close_ori,
                                "type": "number"
                            },
                            {
                                "label": "最高价(原始)",
                                "value": cls.high_ori,
                                "type": "number"
                            },
                            {
                                "label": "最低价(原始)",
                                "value": cls.low_ori,
                                "type": "number"
                            },
                            {
                                "label": "均价(原始)",
                                "value": cls.avg_ori,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "均价与比值",
                        "items": [
                            {
                                "label": "当日均价",
                                "value": cls.avg,
                                "type": "number"
                            },
                            {
                                "label": "均价涨跌幅",
                                "value": cls.avg_ratio,
                                "type": "percent"
                            },
                            {
                                "label": "5日均价",
                                "value": cls.avg_5,
                                "type": "number"
                            },
                            {
                                "label": "10日均价",
                                "value": cls.avg_10,
                                "type": "number"
                            },
                            {
                                "label": "20日均价",
                                "value": cls.avg_20,
                                "type": "number"
                            },
                            {
                                "label": "40日均价",
                                "value": cls.avg_40,
                                "type": "number"
                            },
                            {
                                "label": "60日均价",
                                "value": cls.avg_60,
                                "type": "number"
                            },
                            {
                                "label": "120日均价",
                                "value": cls.avg_120,
                                "type": "number"
                            },
                            {
                                "label": "240日均价",
                                "value": cls.avg_240,
                                "type": "number"
                            },
                            {
                                "label": "均价/5日均价比值",
                                "value": cls.avg_ratio_5,
                                "type": "number"
                            },
                            {
                                "label": "均价/10日均价比值",
                                "value": cls.avg_ratio_10,
                                "type": "number"
                            },
                            {
                                "label": "均价/20日均价比值",
                                "value": cls.avg_ratio_20,
                                "type": "number"
                            },
                            {
                                "label": "均价/40日均价比值",
                                "value": cls.avg_ratio_40,
                                "type": "number"
                            },
                            {
                                "label": "均价/60日均价比值",
                                "value": cls.avg_ratio_60,
                                "type": "number"
                            },
                            {
                                "label": "均价/120日均价比值",
                                "value": cls.avg_ratio_120,
                                "type": "number"
                            },
                            {
                                "label": "均价/240日均价比值",
                                "value": cls.avg_ratio_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "涨跌幅",
                        "items": [
                            {
                                "label": "当日涨跌幅",
                                "value": cls.change_Ratio,
                                "type": "percent"
                            },
                            {
                                "label": "3日涨跌幅",
                                "value": cls.change_Ratio_3,
                                "type": "percent"
                            },
                            {
                                "label": "5日涨跌幅",
                                "value": cls.change_Ratio_5,
                                "type": "percent"
                            },
                            {
                                "label": "10日涨跌幅",
                                "value": cls.change_Ratio_10,
                                "type": "percent"
                            },
                            {
                                "label": "20日涨跌幅",
                                "value": cls.change_Ratio_20,
                                "type": "percent"
                            },
                            {
                                "label": "40日涨跌幅",
                                "value": cls.change_Ratio_40,
                                "type": "percent"
                            },
                            {
                                "label": "60日涨跌幅",
                                "value": cls.change_Ratio_60,
                                "type": "percent"
                            },
                            {
                                "label": "120日涨跌幅",
                                "value": cls.change_Ratio_120,
                                "type": "percent"
                            },
                            {
                                "label": "240日涨跌幅",
                                "value": cls.change_Ratio_240,
                                "type": "percent"
                            },
                            {
                                "label": "3日距今涨跌幅",
                                "value": cls.change_Ratio_single_3,
                                "type": "percent"
                            },
                            {
                                "label": "5日距今涨跌幅",
                                "value": cls.change_Ratio_single_5,
                                "type": "percent"
                            },
                            {
                                "label": "10日距今涨跌幅",
                                "value": cls.change_Ratio_single_10,
                                "type": "percent"
                            },
                            {
                                "label": "20日距今涨跌幅",
                                "value": cls.change_Ratio_single_20,
                                "type": "percent"
                            },
                            {
                                "label": "40日距今涨跌幅",
                                "value": cls.change_Ratio_single_40,
                                "type": "percent"
                            },
                            {
                                "label": "60日距今涨跌幅",
                                "value": cls.change_Ratio_single_60,
                                "type": "percent"
                            },
                            {
                                "label": "120日距今涨跌幅",
                                "value": cls.change_Ratio_single_120,
                                "type": "percent"
                            },
                            {
                                "label": "240日距今涨跌幅",
                                "value": cls.change_Ratio_single_240,
                                "type": "percent"
                            }
                        ]
                    },
                    {
                        "name": "振幅",
                        "items": [
                            {
                                "label": "当日振幅",
                                "value": cls.amplitude,
                                "type": "percent"
                            },
                            {
                                "label": "3日振幅",
                                "value": cls.amplitude_3,
                                "type": "percent"
                            },
                            {
                                "label": "5日振幅",
                                "value": cls.amplitude_5,
                                "type": "percent"
                            },
                            {
                                "label": "10日振幅",
                                "value": cls.amplitude_10,
                                "type": "percent"
                            }
                        ]
                    },
                    {
                        "name": "成交量",
                        "items": [
                            {
                                "label": "当日成交量",
                                "value": cls.volume,
                                "type": "number"
                            },
                            {
                                "label": "成交量涨跌幅",
                                "value": cls.volume_ratio,
                                "type": "percent"
                            },
                            {
                                "label": "3日成交量涨跌幅",
                                "value": cls.volume_ratio_3,
                                "type": "percent"
                            },
                            {
                                "label": "5日成交量涨跌幅",
                                "value": cls.volume_ratio_5_percent,
                                "type": "percent"
                            },
                            {
                                "label": "10日成交量涨跌幅",
                                "value": cls.volume_ratio_10,
                                "type": "percent"
                            },
                            {
                                "label": "20日成交量涨跌幅",
                                "value": cls.volume_ratio_20,
                                "type": "percent"
                            },
                            {
                                "label": "40日成交量涨跌幅",
                                "value": cls.volume_ratio_40,
                                "type": "percent"
                            },
                            {
                                "label": "当日量比",
                                "value": cls.volume_ratio_5,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "成交额",
                        "items": [
                            {
                                "label": "当日成交额",
                                "value": cls.volume_price,
                                "type": "currency"
                            },
                            {
                                "label": "成交额涨跌幅",
                                "value": cls.volume_price_ratio,
                                "type": "percent"
                            },
                            {
                                "label": "3日成交额涨跌幅",
                                "value": cls.volume_price_ratio_3,
                                "type": "percent"
                            },
                            {
                                "label": "5日成交额涨跌幅",
                                "value": cls.volume_price_ratio_5,
                                "type": "percent"
                            },
                            {
                                "label": "10日成交额涨跌幅",
                                "value": cls.volume_price_ratio_10,
                                "type": "percent"
                            },
                            {
                                "label": "20日成交额涨跌幅",
                                "value": cls.volume_price_ratio_20,
                                "type": "percent"
                            },
                            {
                                "label": "40日成交额涨跌幅",
                                "value": cls.volume_price_ratio_40,
                                "type": "percent"
                            }
                        ]
                    },
                    {
                        "name": "换手率与流通",
                        "items": [
                            {
                                "label": "当日换手率",
                                "value": cls.turn,
                                "type": "percent"
                            },
                            {
                                "label": "资金流通率",
                                "value": cls.turn_value,
                                "type": "percent"
                            },
                            {
                                "label": "换手率涨跌幅",
                                "value": cls.turn_ratio,
                                "type": "percent"
                            }
                        ]
                    },
                    {
                        "name": "市值与估值",
                        "items": [
                            {
                                "label": "总市值",
                                "value": cls.total_value,
                                "type": "market_cap"
                            },
                            {
                                "label": "市盈率",
                                "value": cls.earn,
                                "type": "number"
                            },
                            {
                                "label": "市净率",
                                "value": cls.clean,
                                "type": "number"
                            },
                            {
                                "label": "市销率",
                                "value": cls.cash,
                                "type": "number"
                            },
                            {
                                "label": "市现率",
                                "value": cls.sale,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "压力位数值",
                        "items": [
                            {
                                "label": "20日上压力位",
                                "value": cls.up_pressure_20,
                                "type": "number"
                            },
                            {
                                "label": "20日下压力位",
                                "value": cls.down_pressure_20,
                                "type": "number"
                            },
                            {
                                "label": "40日上压力位",
                                "value": cls.up_pressure_40,
                                "type": "number"
                            },
                            {
                                "label": "40日下压力位",
                                "value": cls.down_pressure_40,
                                "type": "number"
                            },
                            {
                                "label": "60日上压力位",
                                "value": cls.up_pressure_60,
                                "type": "number"
                            },
                            {
                                "label": "60日下压力位",
                                "value": cls.down_pressure_60,
                                "type": "number"
                            },
                            {
                                "label": "120日上压力位",
                                "value": cls.up_pressure_120,
                                "type": "number"
                            },
                            {
                                "label": "120日下压力位",
                                "value": cls.down_pressure_120,
                                "type": "number"
                            },
                            {
                                "label": "240日上压力位",
                                "value": cls.up_pressure_240,
                                "type": "number"
                            },
                            {
                                "label": "240日下压力位",
                                "value": cls.down_pressure_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "单日突破压力位",
                        "items": [
                            {
                                "label": "突破20日上压力位",
                                "value": cls.is_break_upper_20,
                                "type": "number"
                            },
                            {
                                "label": "跌破20日下压力位",
                                "value": cls.is_break_lower_20,
                                "type": "number"
                            },
                            {
                                "label": "突破40日上压力位",
                                "value": cls.is_break_upper_40,
                                "type": "number"
                            },
                            {
                                "label": "跌破40日下压力位",
                                "value": cls.is_break_lower_40,
                                "type": "number"
                            },
                            {
                                "label": "突破60日上压力位",
                                "value": cls.is_break_upper_60,
                                "type": "number"
                            },
                            {
                                "label": "跌破60日下压力位",
                                "value": cls.is_break_lower_60,
                                "type": "number"
                            },
                            {
                                "label": "突破120日上压力位",
                                "value": cls.is_break_upper_120,
                                "type": "number"
                            },
                            {
                                "label": "跌破120日下压力位",
                                "value": cls.is_break_lower_120,
                                "type": "number"
                            },
                            {
                                "label": "突破240日上压力位",
                                "value": cls.is_break_upper_240,
                                "type": "number"
                            },
                            {
                                "label": "跌破240日下压力位",
                                "value": cls.is_break_lower_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "连续2日突破压力位",
                        "items": [
                            {
                                "label": "连续2日突破20日上压力位",
                                "value": cls.is_break_upper_20_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日跌破20日下压力位",
                                "value": cls.is_break_lower_20_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日突破40日上压力位",
                                "value": cls.is_break_upper_40_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日跌破40日下压力位",
                                "value": cls.is_break_lower_40_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日突破60日上压力位",
                                "value": cls.is_break_upper_60_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日跌破60日下压力位",
                                "value": cls.is_break_lower_60_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日突破120日上压力位",
                                "value": cls.is_break_upper_120_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日跌破120日下压力位",
                                "value": cls.is_break_lower_120_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日突破240日上压力位",
                                "value": cls.is_break_upper_240_2,
                                "type": "number"
                            },
                            {
                                "label": "连续2日跌破240日下压力位",
                                "value": cls.is_break_lower_240_2,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "连续3日突破压力位",
                        "items": [
                            {
                                "label": "连续3日突破20日上压力位",
                                "value": cls.is_break_upper_20_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日跌破20日下压力位",
                                "value": cls.is_break_lower_20_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日突破40日上压力位",
                                "value": cls.is_break_upper_40_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日跌破40日下压力位",
                                "value": cls.is_break_lower_40_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日突破60日上压力位",
                                "value": cls.is_break_upper_60_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日跌破60日下压力位",
                                "value": cls.is_break_lower_60_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日突破120日上压力位",
                                "value": cls.is_break_upper_120_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日跌破120日下压力位",
                                "value": cls.is_break_lower_120_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日突破240日上压力位",
                                "value": cls.is_break_upper_240_3,
                                "type": "number"
                            },
                            {
                                "label": "连续3日跌破240日下压力位",
                                "value": cls.is_break_lower_240_3,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "连续5日突破压力位",
                        "items": [
                            {
                                "label": "连续5日突破20日上压力位",
                                "value": cls.is_break_upper_20_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日跌破20日下压力位",
                                "value": cls.is_break_lower_20_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日突破40日上压力位",
                                "value": cls.is_break_upper_40_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日跌破40日下压力位",
                                "value": cls.is_break_lower_40_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日突破60日上压力位",
                                "value": cls.is_break_upper_60_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日跌破60日下压力位",
                                "value": cls.is_break_lower_60_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日突破120日上压力位",
                                "value": cls.is_break_upper_120_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日跌破120日下压力位",
                                "value": cls.is_break_lower_120_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日突破240日上压力位",
                                "value": cls.is_break_upper_240_5,
                                "type": "number"
                            },
                            {
                                "label": "连续5日跌破240日下压力位",
                                "value": cls.is_break_lower_240_5,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "收盘价/压力位比值",
                        "items": [
                            {
                                "label": "收盘价/20日上压力位",
                                "value": cls.ratio_close_upper_20,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/20日下压力位",
                                "value": cls.ratio_close_lower_20,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/40日上压力位",
                                "value": cls.ratio_close_upper_40,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/40日下压力位",
                                "value": cls.ratio_close_lower_40,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/60日上压力位",
                                "value": cls.ratio_close_upper_60,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/60日下压力位",
                                "value": cls.ratio_close_lower_60,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/120日上压力位",
                                "value": cls.ratio_close_upper_120,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/120日下压力位",
                                "value": cls.ratio_close_lower_120,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/240日上压力位",
                                "value": cls.ratio_close_upper_240,
                                "type": "number"
                            },
                            {
                                "label": "收盘价/240日下压力位",
                                "value": cls.ratio_close_lower_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "2日均价/压力位比值",
                        "items": [
                            {
                                "label": "2日均价/20日上压力位",
                                "value": cls.ratio_close_upper_2_20,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/20日下压力位",
                                "value": cls.ratio_close_lower_2_20,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/40日上压力位",
                                "value": cls.ratio_close_upper_2_40,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/40日下压力位",
                                "value": cls.ratio_close_lower_2_40,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/60日上压力位",
                                "value": cls.ratio_close_upper_2_60,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/60日下压力位",
                                "value": cls.ratio_close_lower_2_60,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/120日上压力位",
                                "value": cls.ratio_close_upper_2_120,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/120日下压力位",
                                "value": cls.ratio_close_lower_2_120,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/240日上压力位",
                                "value": cls.ratio_close_upper_2_240,
                                "type": "number"
                            },
                            {
                                "label": "2日均价/240日下压力位",
                                "value": cls.ratio_close_lower_2_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "3日均价/压力位比值",
                        "items": [
                            {
                                "label": "3日均价/20日上压力位",
                                "value": cls.ratio_close_upper_3_20,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/20日下压力位",
                                "value": cls.ratio_close_lower_3_20,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/40日上压力位",
                                "value": cls.ratio_close_upper_3_40,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/40日下压力位",
                                "value": cls.ratio_close_lower_3_40,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/60日上压力位",
                                "value": cls.ratio_close_upper_3_60,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/60日下压力位",
                                "value": cls.ratio_close_lower_3_60,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/120日上压力位",
                                "value": cls.ratio_close_upper_3_120,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/120日下压力位",
                                "value": cls.ratio_close_lower_3_120,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/240日上压力位",
                                "value": cls.ratio_close_upper_3_240,
                                "type": "number"
                            },
                            {
                                "label": "3日均价/240日下压力位",
                                "value": cls.ratio_close_lower_3_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "5日均价/压力位比值",
                        "items": [
                            {
                                "label": "5日均价/20日上压力位",
                                "value": cls.ratio_close_upper_5_20,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/20日下压力位",
                                "value": cls.ratio_close_lower_5_20,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/40日上压力位",
                                "value": cls.ratio_close_upper_5_40,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/40日下压力位",
                                "value": cls.ratio_close_lower_5_40,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/60日上压力位",
                                "value": cls.ratio_close_upper_5_60,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/60日下压力位",
                                "value": cls.ratio_close_lower_5_60,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/120日上压力位",
                                "value": cls.ratio_close_upper_5_120,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/120日下压力位",
                                "value": cls.ratio_close_lower_5_120,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/240日上压力位",
                                "value": cls.ratio_close_upper_5_240,
                                "type": "number"
                            },
                            {
                                "label": "5日均价/240日下压力位",
                                "value": cls.ratio_close_lower_5_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "行业排名",
                        "items": [
                            {
                                "label": "总市值行业排名",
                                "value": cls.total_value_ratio,
                                "type": "number"
                            },
                            {
                                "label": "市盈率行业排名",
                                "value": cls.earn_ratio,
                                "type": "number"
                            },
                            {
                                "label": "市净率行业排名",
                                "value": cls.clean_ratio,
                                "type": "number"
                            },
                            {
                                "label": "市销率行业排名",
                                "value": cls.cash_ratio,
                                "type": "number"
                            },
                            {
                                "label": "市现率行业排名",
                                "value": cls.sale_ratio,
                                "type": "number"
                            },
                            {
                                "label": "成交量行业排名",
                                "value": cls.volume_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "成交额行业排名",
                                "value": cls.total_price_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "成交额涨跌幅行业排名",
                                "value": cls.total_price_ratio_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "成交量涨跌幅行业排名",
                                "value": cls.volume_ratio_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "涨跌幅行业排名",
                                "value": cls.ratio_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "振幅行业排名",
                                "value": cls.amplitude_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "换手率行业排名",
                                "value": cls.turn_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "换手率涨跌幅行业排名",
                                "value": cls.turn_ratio_industry_rank,
                                "type": "number"
                            },
                            {
                                "label": "均价涨跌幅行业排名",
                                "value": cls.avg_industry_rank,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "成交量状态",
                        "items": [
                            {
                                "label": "成交量状态_1日",
                                "value": cls.volumeState_1,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_3日",
                                "value": cls.volumeState_3,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_5日",
                                "value": cls.volumeState_5,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_10日",
                                "value": cls.volumeState_10,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_20日",
                                "value": cls.volumeState_20,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_40日",
                                "value": cls.volumeState_40,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_60日",
                                "value": cls.volumeState_60,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_120日",
                                "value": cls.volumeState_120,
                                "type": "number"
                            },
                            {
                                "label": "成交量状态_240日",
                                "value": cls.volumeState_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "价格状态",
                        "items": [
                            {
                                "label": "价格状态_1日",
                                "value": cls.priceState_1,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_3日",
                                "value": cls.priceState_3,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_5日",
                                "value": cls.priceState_5,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_10日",
                                "value": cls.priceState_10,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_20日",
                                "value": cls.priceState_20,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_40日",
                                "value": cls.priceState_40,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_60日",
                                "value": cls.priceState_60,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_120日",
                                "value": cls.priceState_120,
                                "type": "number"
                            },
                            {
                                "label": "价格状态_240日",
                                "value": cls.priceState_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "振幅状态",
                        "items": [
                            {
                                "label": "振幅状态_1日",
                                "value": cls.amplitudeState_1,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_3日",
                                "value": cls.amplitudeState_3,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_5日",
                                "value": cls.amplitudeState_5,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_10日",
                                "value": cls.amplitudeState_10,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_20日",
                                "value": cls.amplitudeState_20,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_40日",
                                "value": cls.amplitudeState_40,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_60日",
                                "value": cls.amplitudeState_60,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_120日",
                                "value": cls.amplitudeState_120,
                                "type": "number"
                            },
                            {
                                "label": "振幅状态_240日",
                                "value": cls.amplitudeState_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "1日量价形态",
                        "items": [
                            {
                                "label": "放量增长",
                                "value": cls.is_up_up,
                                "type": "number"
                            },
                            {
                                "label": "缩量增长",
                                "value": cls.is_low_up,
                                "type": "number"
                            },
                            {
                                "label": "放量降低",
                                "value": cls.is_up_low,
                                "type": "number"
                            },
                            {
                                "label": "缩量降低",
                                "value": cls.is_low_low,
                                "type": "number"
                            },
                            {
                                "label": "放量横盘",
                                "value": cls.is_up_mid,
                                "type": "number"
                            },
                            {
                                "label": "缩量横盘",
                                "value": cls.is_low_mid,
                                "type": "number"
                            },
                            {
                                "label": "平量增长",
                                "value": cls.is_mid_up,
                                "type": "number"
                            },
                            {
                                "label": "平量降低",
                                "value": cls.is_mid_low,
                                "type": "number"
                            },
                            {
                                "label": "震荡上行",
                                "value": cls.is_pop_up,
                                "type": "number"
                            },
                            {
                                "label": "震荡下行",
                                "value": cls.is_pop_down,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "3日量价形态",
                        "items": [
                            {
                                "label": "3日放量增长",
                                "value": cls.is_up_up_3,
                                "type": "number"
                            },
                            {
                                "label": "3日缩量增长",
                                "value": cls.is_low_up_3,
                                "type": "number"
                            },
                            {
                                "label": "3日放量降低",
                                "value": cls.is_up_low_3,
                                "type": "number"
                            },
                            {
                                "label": "3日缩量降低",
                                "value": cls.is_low_low_3,
                                "type": "number"
                            },
                            {
                                "label": "3日放量横盘",
                                "value": cls.is_up_mid_3,
                                "type": "number"
                            },
                            {
                                "label": "3日缩量横盘",
                                "value": cls.is_low_mid_3,
                                "type": "number"
                            },
                            {
                                "label": "3日平量增长",
                                "value": cls.is_mid_up_3,
                                "type": "number"
                            },
                            {
                                "label": "3日平量降低",
                                "value": cls.is_mid_low_3,
                                "type": "number"
                            },
                            {
                                "label": "3日震荡上行",
                                "value": cls.is_pop_up_3,
                                "type": "number"
                            },
                            {
                                "label": "3日震荡下行",
                                "value": cls.is_pop_down_3,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "5日量价形态",
                        "items": [
                            {
                                "label": "5日放量增长",
                                "value": cls.is_up_up_5,
                                "type": "number"
                            },
                            {
                                "label": "5日缩量增长",
                                "value": cls.is_low_up_5,
                                "type": "number"
                            },
                            {
                                "label": "5日放量降低",
                                "value": cls.is_up_low_5,
                                "type": "number"
                            },
                            {
                                "label": "5日缩量降低",
                                "value": cls.is_low_low_5,
                                "type": "number"
                            },
                            {
                                "label": "5日放量横盘",
                                "value": cls.is_up_mid_5,
                                "type": "number"
                            },
                            {
                                "label": "5日缩量横盘",
                                "value": cls.is_low_mid_5,
                                "type": "number"
                            },
                            {
                                "label": "5日平量增长",
                                "value": cls.is_mid_up_5,
                                "type": "number"
                            },
                            {
                                "label": "5日平量降低",
                                "value": cls.is_mid_low_5,
                                "type": "number"
                            },
                            {
                                "label": "5日震荡上行",
                                "value": cls.is_pop_up_5,
                                "type": "number"
                            },
                            {
                                "label": "5日震荡下行",
                                "value": cls.is_pop_down_5,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "10日量价形态",
                        "items": [
                            {
                                "label": "10日放量增长",
                                "value": cls.is_up_up_10,
                                "type": "number"
                            },
                            {
                                "label": "10日缩量增长",
                                "value": cls.is_low_up_10,
                                "type": "number"
                            },
                            {
                                "label": "10日放量降低",
                                "value": cls.is_up_low_10,
                                "type": "number"
                            },
                            {
                                "label": "10日缩量降低",
                                "value": cls.is_low_low_10,
                                "type": "number"
                            },
                            {
                                "label": "10日放量横盘",
                                "value": cls.is_up_mid_10,
                                "type": "number"
                            },
                            {
                                "label": "10日缩量横盘",
                                "value": cls.is_low_mid_10,
                                "type": "number"
                            },
                            {
                                "label": "10日平量增长",
                                "value": cls.is_mid_up_10,
                                "type": "number"
                            },
                            {
                                "label": "10日平量降低",
                                "value": cls.is_mid_low_10,
                                "type": "number"
                            },
                            {
                                "label": "10日震荡上行",
                                "value": cls.is_pop_up_10,
                                "type": "number"
                            },
                            {
                                "label": "10日震荡下行",
                                "value": cls.is_pop_down_10,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "20日量价形态",
                        "items": [
                            {
                                "label": "20日放量增长",
                                "value": cls.is_up_up_20,
                                "type": "number"
                            },
                            {
                                "label": "20日缩量增长",
                                "value": cls.is_low_up_20,
                                "type": "number"
                            },
                            {
                                "label": "20日放量降低",
                                "value": cls.is_up_low_20,
                                "type": "number"
                            },
                            {
                                "label": "20日缩量降低",
                                "value": cls.is_low_low_20,
                                "type": "number"
                            },
                            {
                                "label": "20日放量横盘",
                                "value": cls.is_up_mid_20,
                                "type": "number"
                            },
                            {
                                "label": "20日缩量横盘",
                                "value": cls.is_low_mid_20,
                                "type": "number"
                            },
                            {
                                "label": "20日平量增长",
                                "value": cls.is_mid_up_20,
                                "type": "number"
                            },
                            {
                                "label": "20日平量降低",
                                "value": cls.is_mid_low_20,
                                "type": "number"
                            },
                            {
                                "label": "20日震荡上行",
                                "value": cls.is_pop_up_20,
                                "type": "number"
                            },
                            {
                                "label": "20日震荡下行",
                                "value": cls.is_pop_down_20,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "40日量价形态",
                        "items": [
                            {
                                "label": "40日放量增长",
                                "value": cls.is_up_up_40,
                                "type": "number"
                            },
                            {
                                "label": "40日缩量增长",
                                "value": cls.is_low_up_40,
                                "type": "number"
                            },
                            {
                                "label": "40日放量降低",
                                "value": cls.is_up_low_40,
                                "type": "number"
                            },
                            {
                                "label": "40日缩量降低",
                                "value": cls.is_low_low_40,
                                "type": "number"
                            },
                            {
                                "label": "40日放量横盘",
                                "value": cls.is_up_mid_40,
                                "type": "number"
                            },
                            {
                                "label": "40日缩量横盘",
                                "value": cls.is_low_mid_40,
                                "type": "number"
                            },
                            {
                                "label": "40日平量增长",
                                "value": cls.is_mid_up_40,
                                "type": "number"
                            },
                            {
                                "label": "40日平量降低",
                                "value": cls.is_mid_low_40,
                                "type": "number"
                            },
                            {
                                "label": "40日震荡上行",
                                "value": cls.is_pop_up_40,
                                "type": "number"
                            },
                            {
                                "label": "40日震荡下行",
                                "value": cls.is_pop_down_40,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "60日量价形态",
                        "items": [
                            {
                                "label": "60日放量增长",
                                "value": cls.is_up_up_60,
                                "type": "number"
                            },
                            {
                                "label": "60日缩量增长",
                                "value": cls.is_low_up_60,
                                "type": "number"
                            },
                            {
                                "label": "60日放量降低",
                                "value": cls.is_up_low_60,
                                "type": "number"
                            },
                            {
                                "label": "60日缩量降低",
                                "value": cls.is_low_low_60,
                                "type": "number"
                            },
                            {
                                "label": "60日放量横盘",
                                "value": cls.is_up_mid_60,
                                "type": "number"
                            },
                            {
                                "label": "60日缩量横盘",
                                "value": cls.is_low_mid_60,
                                "type": "number"
                            },
                            {
                                "label": "60日平量增长",
                                "value": cls.is_mid_up_60,
                                "type": "number"
                            },
                            {
                                "label": "60日平量降低",
                                "value": cls.is_mid_low_60,
                                "type": "number"
                            },
                            {
                                "label": "60日震荡上行",
                                "value": cls.is_pop_up_60,
                                "type": "number"
                            },
                            {
                                "label": "60日震荡下行",
                                "value": cls.is_pop_down_60,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "120日量价形态",
                        "items": [
                            {
                                "label": "120日放量增长",
                                "value": cls.is_up_up_120,
                                "type": "number"
                            },
                            {
                                "label": "120日缩量增长",
                                "value": cls.is_low_up_120,
                                "type": "number"
                            },
                            {
                                "label": "120日放量降低",
                                "value": cls.is_up_low_120,
                                "type": "number"
                            },
                            {
                                "label": "120日缩量降低",
                                "value": cls.is_low_low_120,
                                "type": "number"
                            },
                            {
                                "label": "120日放量横盘",
                                "value": cls.is_up_mid_120,
                                "type": "number"
                            },
                            {
                                "label": "120日缩量横盘",
                                "value": cls.is_low_mid_120,
                                "type": "number"
                            },
                            {
                                "label": "120日平量增长",
                                "value": cls.is_mid_up_120,
                                "type": "number"
                            },
                            {
                                "label": "120日平量降低",
                                "value": cls.is_mid_low_120,
                                "type": "number"
                            },
                            {
                                "label": "120日震荡上行",
                                "value": cls.is_pop_up_120,
                                "type": "number"
                            },
                            {
                                "label": "120日震荡下行",
                                "value": cls.is_pop_down_120,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "240日量价形态",
                        "items": [
                            {
                                "label": "240日放量增长",
                                "value": cls.is_up_up_240,
                                "type": "number"
                            },
                            {
                                "label": "240日缩量增长",
                                "value": cls.is_low_up_240,
                                "type": "number"
                            },
                            {
                                "label": "240日放量降低",
                                "value": cls.is_up_low_240,
                                "type": "number"
                            },
                            {
                                "label": "240日缩量降低",
                                "value": cls.is_low_low_240,
                                "type": "number"
                            },
                            {
                                "label": "240日放量横盘",
                                "value": cls.is_up_mid_240,
                                "type": "number"
                            },
                            {
                                "label": "240日缩量横盘",
                                "value": cls.is_low_mid_240,
                                "type": "number"
                            },
                            {
                                "label": "240日平量增长",
                                "value": cls.is_mid_up_240,
                                "type": "number"
                            },
                            {
                                "label": "240日平量降低",
                                "value": cls.is_mid_low_240,
                                "type": "number"
                            },
                            {
                                "label": "240日震荡上行",
                                "value": cls.is_pop_up_240,
                                "type": "number"
                            },
                            {
                                "label": "240日震荡下行",
                                "value": cls.is_pop_down_240,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "涨跌停特征",
                        "items": [
                            {
                                "label": "是否涨停",
                                "value": cls.is_up_stop,
                                "type": "number"
                            },
                            {
                                "label": "是否跌停",
                                "value": cls.is_down_stop,
                                "type": "number"
                            },
                            {
                                "label": "是否触及涨停",
                                "value": cls.is_touch_up_stop,
                                "type": "number"
                            },
                            {
                                "label": "是否触及跌停",
                                "value": cls.is_touch_down_stop,
                                "type": "number"
                            },
                            {
                                "label": "是否一字板",
                                "value": cls.is_one_ban,
                                "type": "number"
                            }
                        ]
                    },
                    {
                        "name": "K线形态",
                        "items": [
                            {
                                "label": "是否短实体",
                                "value": cls.is_short_entity,
                                "type": "number"
                            },
                            {
                                "label": "是否长上影线",
                                "value": cls.is_long_shadow_up,
                                "type": "number"
                            },
                            {
                                "label": "是否长下影线",
                                "value": cls.is_long_shadow_down,
                                "type": "number"
                            },
                            {
                                "label": "是否长十字",
                                "value": cls.is_long_cross,
                                "type": "number"
                            },
                            {
                                "label": "是否短十字",
                                "value": cls.is_short_cross,
                                "type": "number"
                            },
                            {
                                "label": "是否正T字",
                                "value": cls.is_T_up,
                                "type": "number"
                            },
                            {
                                "label": "是否倒T字",
                                "value": cls.is_T_down,
                                "type": "number"
                            }
                        ]
                    }
                ]
                }
            }

            response["stocks"].append(single)

        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_SELECT_STOCKS, response["stocks"])




    def SearchStock(self, data):
        query_type = data.get("query_type")
        query_value = data.get("query_value")
        print(f"查询股票，类型：{query_type}，值：{query_value}")
        if self.main.calculationDataHandle.isPreheating == False:
            print("没有预热，请先预热")
            self.main.BoardCast("没有预热，请先预热")
            return
        response = {
            'query_type': query_type,
            'query_value': query_value,
            'stocks': []
        }
        stockList = self.main.calculationDataHandle.totalComponyIns.allStockList
        if query_type == "code":
            for code in stockList:
                if code == query_value or code.split(".")[0] == query_value:
                    res = self.CreateSearchResponseSingle(code)
                    response['stocks'].append(res)
        
        elif query_type == "letter":
            for code in stockList:
                componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
                if componyInfo.Cn_spell != None and componyInfo.Cn_spell.__contains__(query_value):
                    res = self.CreateSearchResponseSingle(code)
                    response['stocks'].append(res)
                    
        elif query_type == "keyword":
            containsList = []
            for code in stockList:
                componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
                inName = componyInfo.Name != None and componyInfo.Name.__contains__(query_value)
                inComName = componyInfo.Com_name != None and componyInfo.Com_name.__contains__(query_value)
                inProduct = componyInfo.Product != None and componyInfo.Product.__contains__(query_value)
                if inName or inComName or inProduct:
                    res = self.CreateSearchResponseSingle(code)
                    response['stocks'].append(res)
                    containsList.append(code)

            for code in stockList:
                componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
                inBusinessScope = componyInfo.Business_Scope != None and componyInfo.Business_Scope.__contains__(query_value)
                inIntro = componyInfo.Introduction != None and componyInfo.Introduction.__contains__(query_value)
                if inBusinessScope or inIntro:
                    if code not in containsList:
                        res = self.CreateSearchResponseSingle(code)
                        response['stocks'].append(res)

        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_QUERY_STOCKS_RESPONSE, response)

        pass

    def CreateSearchResponseSingle(self, stockCode):
        componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(stockCode)
        cls = self.main.calculationDataHandle.GetBaseDataClass_WithTradeState(stockCode, self.main.todayStockDate, False)
        print(f"查询结果：{componyInfo.Code}, {componyInfo.Name},  {componyInfo.Industry}")
        stock = {
        'code': stockCode,
        'name': componyInfo.Name,
        'market_cap': float(cls.total_value / 100000000) if cls != None else 0,              #流通市值
        'change_3d': float(cls.change_Ratio_single_3) if cls != None else 0,   #30天涨跌幅
        'change_5d': float(cls.change_Ratio_single_5) if cls != None else 0,
        'change_10d': float(cls.change_Ratio_single_10) if cls != None else 0,
        'change_20d': float(cls.change_Ratio_single_20) if cls != None else 0,
        'change_40d': float(cls.change_Ratio_single_40) if cls != None else 0,
        'change_60d': float(cls.change_Ratio_single_60) if cls != None else 0,
        'change_120d': float(cls.change_Ratio_single_120) if cls != None else 0,
        'change_240d': float(cls.change_Ratio_single_240) if cls != None else 0,




        'earn': float(cls.earn) if cls != None else 0,
        'clean': float(cls.clean) if cls != None else 0,
        'sale': float(cls.sale) if cls != None else 0,
        'cash': float(cls.cash) if cls != None else 0,

        'Roe': float(componyInfo.Roe) if cls != None else 0,
        'YOYNi': float(componyInfo.YOYNi) if cls != None else 0,
        'LiabilityTo': float(componyInfo.LiabilityTo) if cls != None else 0,
        'YOYEquity': float(componyInfo.YOYEquity) if cls != None else 0,
        'YOYLiability': float(componyInfo.YOYLiability) if cls != None else 0,


    

        'company_type': componyInfo.Act_ent_type,
        'company_name': componyInfo.Com_name,
        'main_products': componyInfo.Product,
        'business_scope': componyInfo.Business_Scope,
        'company_description': componyInfo.Introduction
        }
        return stock





    ## 后端返回（流式，多次发送）：
    #SC_KLINE_CHUNK = {
    #    "type": "sc_kline_chunk",
    #    "msg": {
    #        "code": "600000",                    # str: 股票代码
    #        "chunk": [                           # list: 本次发送的K线数据块
    #            {
    #                "date": "2024-06-15",        # str: 日期 YYYY-MM-DD
    #                "open": 8.56,                # float: 开盘价
    #                "close": 8.72,               # float: 收盘价
    #                "high": 8.85,                # float: 最高价
    #                "low": 8.45,                 # float: 最低价
    #                "volume": 123456             # float: 成交量
    #            }
    #        ],
    #        "progress": 0.5,                     # float: 进度 0~1
    #        "is_last": False,                    # bool: 是否最后一块
    #        "total": 240                         # int: 总K线数
    #    }
    #}

    ## 后端返回（一次性，单次发送）：
    #SC_KLINE_DATA = {
    #        "code": "600000",
    #        "kline": [
    #            {
    #                "date": "2024-06-15",
    #                "open": 8.56,
    #                "close": 8.72,
    #                "high": 8.85,
    #                "low": 8.45,
    #                "volume": 123456
    #            }
    #            # ... 所有K线数据
    #        ]
    #    }
    #返回K线数据
    def HandleKLineResponse(self, data):
        code = data.get("code")
        dayNum = data.get("days")
        response = {}
        response["code"] = code
        response["kline"] = []
        cls = self.main.calculationDataHandle.GetBaseDataClass_WithTradeState(code, self.main.todayStockDate, False)
        for single in cls.dataList_240:
            date_obj = datetime.strptime(single.trade_date, "%Y%m%d")
            targetDate = date_obj.strftime("%Y-%m-%d")
            singleKline = {}
            singleKline["date"] = targetDate
            singleKline["open"] = single.open
            singleKline["close"] = single.close
            singleKline["high"] = single.high
            singleKline["low"] = single.low
            singleKline["volume"] = single.volume / 10000
            singleKline["turn"] = single.turn
            singleKline["change_Ratio"] = single.change_Ratio
            response["kline"].append(singleKline)
        response["kline"].reverse()
        self.main.websocketHandler.SendMessage_A(self.main.websocketHandler.MessageType.SC_KLINE_DATA, response)
        