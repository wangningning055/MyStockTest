from src.main_code.Core.DataStruct.Base import RecordDataStruct
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main_code.Core import Main

class BaseClass:
    def Init(self, main):
        self.main :"Main.processor" = main
        self.recordCls : RecordDataStruct.TotalRecordDataCls = RecordDataStruct.TotalRecordDataCls()
        self.ReadRecordData()
        self.main.recordDataCls = self.recordCls
    #读出记录数据
    def ReadRecordData(self):
        fileJson = self.main.fileProcessor.GetRecordJsonStrByPath()
        if fileJson == None:
            return RecordDataStruct.TotalRecordDataCls()
        print(fileJson)
        data = json.loads(fileJson)
        classBase2 = RecordDataStruct.TotalRecordDataCls()
        classBase2.__dict__.update(data)
        self.recordCls = classBase2
        return classBase2



    #写入记录数据
    def WriteRecordData(self):
        print("写入记录数据")
        jsonStr = json.dumps(self.main.recordDataCls.__dict__, ensure_ascii=False, indent=4)
        self.main.fileProcessor.SaveRecordJson(jsonStr)


    def GetRecentRequestDateJsonStr(self):
        if self.recordCls is None:
            return ""

        res1 = "{" + f"\"stock\" : \"{self.recordCls.stock_list_last_data}\","
        res2 = f"\"daily\" : \"{self.recordCls.daily_list_last_data}\","
        res3 = f"\"adjust\" : \"{self.recordCls.adjust_list_last_data}\","
        res4 = f"\"value\" : \"{self.recordCls.value_list_last_data}\","
        res5 = f"\"industry\" : \"{self.recordCls.industry_analyze_last_data}\"" + "} "


        return res1 + res2 + res3 + res4 + res5 
    