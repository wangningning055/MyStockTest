import Core.Const
import os
from enum import Enum

class FileEnum(Enum):
    Daily = 1,
    Basic = 2,
    Adjust = 3,

class FileProcessorClass:
    def Init(self):
        self.CheckFolder(Core.Const.TempAdjustFilePath)
        self.CheckFolder(Core.Const.TempBasicFilePath)
        self.CheckFolder(Core.Const.TempDailyFilePath)

    def CheckFolder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def SaveCSV(self,df, StockCode, type:FileEnum):
        if df is None:
            return
        
        if type == FileEnum.Basic:
            path = Core.Const.TempBasicFilePath + Core.Const.TempBasicFileName + StockCode
            df.to_csv(f"{path}.csv", index=False)
        elif type == FileEnum.Daily:
            path = Core.Const.TempDailyFilePath + Core.Const.TempDailyFileName + StockCode
            df.to_csv(f"{path}.csv", index=False)
        elif type == FileEnum.Adjust:
            path = Core.Const.TempAdjustFilePath + Core.Const.TempAdjustFileName + StockCode
            df.to_csv(f"{path}.csv", index=False)

    def GetCSVPath(self, StockCode, type:FileEnum):
        path = ""
        if type == FileEnum.Basic:
            path = Core.Const.TempBasicFilePath + Core.Const.TempBasicFileName + StockCode + ".csv"
        elif type == FileEnum.Daily:
            path = Core.Const.TempDailyFilePath + Core.Const.TempDailyFileName + StockCode+ ".csv"
        elif type == FileEnum.Adjust:
            path = Core.Const.TempAdjustFilePath + Core.Const.TempAdjustFileName + StockCode+ ".csv"
        return path