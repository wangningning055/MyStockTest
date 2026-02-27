from src.main_code.Core.Select.Models import SelectionRequest
from src.main_code.Core.Select.ConditionEvaluator import FactorEvaluator, load_factors_metadata
from src.main_code.Core.Const import FactorsJsonPath
FACTORS_METADATA = None
class BaseClass :
    def Init(self, main):
        self.main  = main
    def __init__(self):
        global FACTORS_METADATA
        FACTORS_METADATA = load_factors_metadata(FactorsJsonPath)
        self.isOutCY = True             #是否剔除创业板股票
        self.isOutST = True             #是否剔除ST股票
        self.isOutKC = True             #是否剔除科创板股票
        self.isOnlyValue = False          #是否只计算价值股
        self.isOnlyGrow = False           #是否只计算成长股
        self.isOnlyGrow_Value = False     #是否只计算成长价值股
        self.factorLimit = 0.5                 #条件因子筛选的边界值，默认为0.5，即大于0.5则满足条件，小于0.5则不满足条件


    #个股条件因子计算和筛选
    def RunGetStockListByCondition(self, conditionJson):
        print(f"开始进行条件选股: {conditionJson}")
        evaluator = FactorEvaluator(FACTORS_METADATA)

        try:
            # Pydantic自动验证并转换
            request = SelectionRequest(**conditionJson)
            print(f"✅ 数据验证成功")
            print(f"   配置数: {len(request.configs)}")
            print(f"   第一个因子: {request.configs[0].factor_group_name}")
            print(f"   权重: {request.configs[0].weight}")
            print(f"   条件数: {len(request.configs[0].logic_tree)}")
            
        except Exception as e:
            print(f"❌ 数据验证失败: {e}")

        #self.main.calculationDataHandle.GetBaseDataClass()
        #score = evaluator.evaluate_stock(stock_data, request.configs)
        #print(f"✅ 个股评分: {score}")
        pass

    #行业轮动分析
    def RunGetIndustryListByYearMonth(self, industry_code, factor_name):
        pass

    #价值股和成长股筛选
    def RunGetValue_Grow_StockList(self, stock_code, factor_name):
        pass
    pass

    #条件1： 3日放量增长条件 == 1 或（当日成交量涨幅 > 10% 且 当日均价与5日均价比 > 1.05） ， 权重：0.4 

    #条件2： 市盈率行业排名 < 15% 且（5日是否震荡上行 == 1 或 5日涨跌幅 > 5） ， 权重：0.6 
