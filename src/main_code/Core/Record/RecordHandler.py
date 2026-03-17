from src.main_code.Core.DataStruct.Base import RecordDataStruct
from src.main_code.Core import Main

class BaseClass:
    def Init(self, main):
        self.main :Main.processor = main
    #读出记录数据
    def ReadRecordData():
        #classBase = IndustryAnalysisResult()
        #key = "202505"
        #value = []
        #value.append("僬侥")
        #value.append("僬侥1")
        #value.append("僬侥2")
        #value.append("僬侥3")
        #value.append("僬侥4")
        #value.append("僬侥5")
        #classBase.allDic[key] = value
        #jsonStr = json.dumps(classBase.__dict__, ensure_ascii=False, indent=4)
        #main.fileProcessor.SaveJson(jsonStr)
        #fileJson = main.fileProcessor.GetJsonStrByPath()
        #print("3#############################################")
        #print(fileJson)
        #data = json.loads(fileJson)
        #classBase2 = IndustryAnalysisResult()
        #classBase2.__dict__.update(data)
        #print(classBase2)
        #for key, value in classBase2.allDic.items():
        #    print(f"key: {key}   value:{value}")
        pass

    #写入记录数据
    def WriteRecordData(data: RecordDataStruct):
        pass
