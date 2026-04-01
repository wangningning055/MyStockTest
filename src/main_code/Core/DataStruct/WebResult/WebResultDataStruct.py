from src.main_code.Core.DataStruct.Base import CalculationDataStruct
from pydantic import BaseModel, Field

class GrowValueStockListDataStruct(BaseModel):
    code : str = ""
    name : str = ""
    industry : str = ""
    type : str = ""
    score : float = 0.0


    change_3d : float = 0.0
    change_5d : float = 0.0
    change_20d : float = 0.0
    change_120d : float = 0.0
    change_240d : float = 0.0


    value : float = 0.0         #流通市值

    Roe : float = 0.0            #roe：净资产收益率      
    earn : float = 0.0         #市盈率
    clean : float = 0.0         #市净率
    sale : float = 0.0         #市销率
    cash : float = 0.0         #市现率

    YOYNi : float = 0.0            #净利润同比增长率       
    LiabilityTo : float = 0.0            #资产负债率             
    YOYEquity : float = 0.0            #净资产同比增长率       
    YOYLiability : float = 0.0            #负债同比增长率       







