import src.main_code.Core.Const
import baostock as bs
import tushare as ts
import pandas as pd
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
import src.main_code.Core.Const as const_proj
import src.main_code.Core as Core
from datetime import datetime
import asyncio

class RequestAPIClass:

    
    #拉取历史原始数据


    #拉取最新日线数据


    #拉取复权因子





    def normalize_individual_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        item-value → 单行 DataFrame
        """
        row = df.set_index("item")["value"].to_dict()
        return pd.DataFrame([row])
    
    def normalize_business_info(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df.rename(columns={
            "股票代码": "code",
            "主营业务": "main_business",
            "产品类型": "product_type",
            "产品名称": "product_name",
            "经营范围": "business_scope",
        }, inplace=True)

        return df
    
    def rename_individual_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df.rename(columns={
            "股票代码": "code",
            "股票简称": "name",
            "行业": "industry",
            "上市时间": "list_date",
            "总股本": "total_share",
            "流通股": "float_share",
            "总市值": "market_cap",
            "流通市值": "float_market_cap",
            "最新": "price",
        }, inplace=True)

        return df
    
    def merge_company_info(self, df_base: pd.DataFrame, df_business: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(df_base, df_business, on="code", how="left")
    
