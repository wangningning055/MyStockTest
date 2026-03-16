import src.main_code.Core as Core
import os
from enum import Enum
import json
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
    




    def SaveRecordJson(self, jsonStr):
        path = Core.Const.TempRecordFilePath + Core.Const.TempRecord_Industry_Result_FileName
        try:
            # 2. 检查并创建目录（如果目录不存在）
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)  # exist_ok=True 避免目录已存在时报错
            
            # 3. 验证并解析JSON字符串（确保输入是合法的JSON）
            # 如果jsonStr已经是Python对象（如dict/list），可跳过这一步直接dump
            if isinstance(jsonStr, str):
                json_data = json.loads(jsonStr)
            else:
                json_data = jsonStr  # 兼容传入Python对象的情况
            
            # 4. 写入JSON文件（带格式化和编码设置）
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(
                    json_data,
                    f,
                    ensure_ascii=False,  # 保留中文等非ASCII字符
                    indent=4,            # 格式化输出，便于阅读
                    sort_keys=False       # 不排序key，保持原有顺序
                )
            
            print(f"JSON文件已成功保存到: {path}")
            return True
        
        except json.JSONDecodeError as e:
            print(f"错误：输入的不是合法的JSON字符串 - {e}")
            return False
        except PermissionError:
            print(f"错误：没有权限写入文件 {path}")
            return False
        except Exception as e:
            print(f"保存JSON文件时发生未知错误 - {e}")
            return False
        
    def GetRecordJsonStrByPath(self):
        path = Core.Const.TempRecordFilePath + Core.Const.TempRecord_Industry_Result_FileName
        
        try:
            # 2. 前置校验：检查文件是否存在且是合法文件
            if not os.path.exists(path):
                print(f"错误：JSON文件不存在 - {path}")
                return None
            if not os.path.isfile(path):
                print(f"错误：指定路径不是文件 - {path}")
                return None
            
            # 3. 读取文件内容（UTF-8编码，避免中文乱码）
            with open(path, 'r', encoding='utf-8') as f:
                # 先读取原始文本（确保是字符串格式）
                file_content = f.read()
                
                # 4. 校验内容是否为合法JSON（避免文件存在但内容无效）
                # 先解析为Python对象，再转回字符串（保证输出是标准JSON格式）
                json.loads(file_content)  # 仅做合法性校验，解析失败会触发JSONDecodeError
                
                # 5. 返回标准JSON字符串（确保格式规范，保留中文）
                return file_content
        
        except json.JSONDecodeError as e:
            print(f"错误：文件内容不是合法的JSON格式 - {e}")
            return None
        except PermissionError:
            print(f"错误：没有读取文件的权限 - {path}")
            return None
        except Exception as e:
            print(f"读取JSON文件并转换为字符串时发生未知错误 - {e}")
            return None
        

