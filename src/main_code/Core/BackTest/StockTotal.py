import src.main_code.Core.BackTest.StockPart as StockPart
from typing import List, Optional, Callable, Dict, Any, Union
import src.main_code.Core.BackTest.BackTestMsgDataStruct as BackTestMsgDataStruct

# 1. 先导入TYPE_CHECKING常量
from typing import TYPE_CHECKING

# 2. 仅在类型检查时导入需要的类（运行时不执行）
if TYPE_CHECKING:
    import src.main_code.Core.BackTest.BackTestHandler as BackTestHandler

class BaseClass:
    partList : Dict[str, StockPart.BaseClass]        #分仓列表
    startValue : int                                #开仓价
    curValue : int                                  #当前价
    changeRatio : float                             #涨跌幅
    def __init__(self, handler):
        self.total_part_share = 1
        self.handler : "BackTestHandler.BaseClass" = handler
        self.partList = {}
        pass
    def Init(self, config : BackTestMsgDataStruct.Msg_TotalStock):
        self.startValue = config.initialFund
        self.curValue = config.initialFund
        self.changeRatio = 0

        for single in config.divisions:
            if(len(single.buyConfigTree) <= 0 or len(single.sellConfigTree) <= 0):
                print(f"分仓{single.name}的买入或卖出策略为空，跳过")
                self.handler.main.BoardCast(f"分仓{single.name}的买入或卖出策略为空，跳过")
                continue

            self.total_part_share -= single.weight

            if(single.weight <= 0):
                print(f"分仓{single.name}的占比小于等于1，不正确，仓位初始化失败")
                self.handler.main.BoardCast(f"分仓{single.name}的占比小于等于1，不正确，仓位初始化失败")
                return False

            if(self.total_part_share < 0):
                print(f"分仓加起来的比例大于1，不正确，仓位初始化失败")
                self.handler.main.BoardCast(f"分仓加起来的比例大于1，不正确，仓位初始化失败")
                return False
            cls = self.CreatePart(single)
            self.partList[single.name] = cls
        if len(self.partList) <= 0:
            print("有效仓位数为0， 初始化失败")
            self.handler.main.BoardCast(f"有效仓位数为0， 初始化失败")
            return False
        return True
    


    def CreatePart(self, single):
        part = StockPart.BaseClass(single, self)
        return part
    


    async def ExecuteSelect(self):
        for key, part in self.partList.items():
            await part.ExecuteSelect()


    async def ExecuteBuySell(self):
        for key, part in self.partList.items():
            part.ExecuteBuySell()