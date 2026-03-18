from src.main_code.Core.DataStruct.Base import RecordDataStruct
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main_code.Core import Main

class BaseClass:
    def Init(self, main):
        self.main :"Main.processor" = main
    #读出记录数据
    def ReadRecordData(self):
        fileJson = self.main.fileProcessor.GetRecordJsonStrByPath()
        if fileJson == None:
            return RecordDataStruct.TotalRecordDataCls()
        print(fileJson)
        data = json.loads(fileJson)
        classBase2 = RecordDataStruct.TotalRecordDataCls()
        classBase2.__dict__.update(data)
        return classBase2



    #写入记录数据
    def WriteRecordData(self):
        jsonStr = json.dumps(self.main.recordDataCls.__dict__, ensure_ascii=False, indent=4)
        self.main.fileProcessor.SaveRecordJson(jsonStr)
