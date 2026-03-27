
from typing import Literal, Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import src.main_code.Core.Select.Models as Models




class Msg_PartStock(BaseModel):
    id: str
    name: str
    weight: int
    holdingTimeMin : int
    holdingTimeMax : int
    stopLossPercent: float
    takeProfitPercent: float
    buyConfigTree: List[Models.FactorConfig]
    sellConfigTree: List[Models.FactorConfig]
    thresholdBuy : float
    thresholdSell : float


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

