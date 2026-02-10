import src.main_code.Core.Const
import baostock as bs
import tushare as ts
import pandas as pd
import akshare as ak
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
import src.main_code.Core.Const as const_proj
import src.main_code.Core as Core
from datetime import datetime
import asyncio

class RequestAPIClass:
    def Request_Cur_Data(self):
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        return stock_zh_a_spot_em_df
    


    #akshare拉取基本数据
    async def Request_Company_AK(self, code):
        df_info = ak.stock_individual_info_em(symbol="000001")
        df_value = ak.stock_zyjs_ths(symbol="000001")

        df_base = self.normalize_individual_info(df_info)
        df_base = self.rename_individual_columns(df_base)

        df_business = self.normalize_business_info(df_value)

        df_final = self.merge_company_info(df_base, df_business)

        await asyncio.sleep(0)
        return df_final
    
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
    
