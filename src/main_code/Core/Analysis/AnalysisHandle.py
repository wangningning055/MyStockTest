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

            #print(f"✅ 个股评分（-100， 100）: {score}, 第{count}个，总共：{len(self.main.calculationDataHandle.totalComponyIns.allStockList)}个, code:{val}      {cls.componyInfo.Name}, 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            count += 1
            #if count > 100:
            #    break
            if score > self.threshold * 100:
                listCode.append(val)
        print("=======================================选股结果==============================================")
        for code in listCode:
            componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
            print(f"{componyInfo.Code}, {componyInfo.Name},  {componyInfo.Industry}")

            
        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"结果长度：: {len(listCode)}， 花费时间：{totalCostTimeStr1}")



    #用于回测的个股条件因子计算和筛选
    def RunGetStockListByConditionForBackTest(self, calculationHandle : CalculationDataHandle.BaseClass, codeList, threshold, isOutKC, isOutCY, isOutST,  configsData, isBuy = True):
        evaluator : FactorEvaluator = FactorEvaluator(FACTORS_METADATA)
        evaluator.SetMain(self.main)
        evaluator.SetCalculationHandle(calculationHandle)

        pid = os.getpid()
        # 获取当前进程对象
        process = psutil.Process(pid)

        listCode = []
        count = 1
        t0 = time.perf_counter()
        print(f" 回测是开始日期是：{calculationHandle.todayStr}")
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
                #print(f"股票{cls.componyInfo.Name}：{val} 新上市交易日不足十天，跳过")
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
            score = evaluator.evaluate_stock(val, configsData)
            
            # 获取内存使用信息（以字节为单位）
            mem_info = process.memory_info()
            
            # 转换为MB（1MB = 1024 * 1024 字节）
            rss_memory = mem_info.rss / (1024 * 1024)  # 实际使用的物理内存（常驻集大小）
            vms_memory = mem_info.vms / (1024 * 1024)  # 虚拟内存大小

            #print(f"✅ 个股评分（-100， 100）: {score}, 第{count}个，总共：{len(codeList)}个, code:{val}      {cls.componyInfo.Name}, 物理内存占用：{round(rss_memory, 2)}， 虚拟内存占用：{round(vms_memory, 2)}")
            count += 1
            #if count > 100:
            #    break
            if score > threshold * 100:
                listCode.append(val)

        print("=======================================选股结果==============================================")
        for code in listCode:
            componyInfo = self.main.calculationDataHandle.totalComponyIns.GetComponyInfo(code)
            print(f"{componyInfo.Code}, {componyInfo.Name},  {componyInfo.Industry}")

            
        t1 = time.perf_counter()
        totalCostTime = (t1 - t0)
        totalCostTimeStr1 = self.main.requestor.format_seconds(totalCostTime)
        print(f"结果长度：: {len(listCode)}， 花费时间：{totalCostTimeStr1}")

