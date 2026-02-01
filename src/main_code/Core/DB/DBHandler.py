import sqlite3
import time
from enum import Enum
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core import Const as const_proj
import asyncio
class TableEnum(Enum):
    Basic = 1,
    Daily = 2,
    Adjust = 3,


class DBHandlerClass:

    def Init(self, main):
        self.main = main
        self.dbPath = const_proj.DBPath
        self.ConnectDb()
        self.main.BoardCast(f"链接数据库成功:{self.dbPath}")
        self.CreateTable()
        self.main.BoardCast(f"创建数据表成功:{self.dbPath}")


    #读取数据库
    def ConnectDb(self):
        self.dbConnect = sqlite3.connect(self.dbPath)
        self.dbCursor = self.dbConnect.cursor()
    #创建数据库表
    def CreateTable(self):
        self.CreateBasicTable()
        self.CreateDailyTable()
        self.CreateAdjustTable()


   #创建基础股市表
    def CreateBasicTable(self):
        self.basicDbStruct = BasicDBStruct.DBStructClass()
        columns = []
        for key, value in self.basicDbStruct.dic.items():
            columnName = self.basicDbStruct.GetNameByEnum(key)
            dbType = self.basicDbStruct.GetDBTypeByEnum(key)
            if key == BasicDBStruct.ColumnEnum.Code:
                columns.append(f"{columnName} {dbType} PRIMARY KEY")
            else:
                columns.append(f"{columnName} {dbType}")
        sql = f"""CREATE TABLE IF NOT EXISTS {const_proj.DBBasicTableName} (
            {', '.join(columns)}
        )"""
        self.dbCursor.execute(sql)
        self.dbConnect.commit()


    #创建复权数据表
    def CreateAdjustTable(self):
        self.adjustDbStruct = AdjustDBStruct.DBStructClass()
        columns = []

        for key in self.adjustDbStruct.dic.keys():
            columnName = self.adjustDbStruct.GetNameByEnum(key)
            dbType = self.adjustDbStruct.GetDBTypeByEnum(key)
            columns.append(f"{columnName} {dbType}")

        columns.append(f"PRIMARY KEY ({self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Code)}, {self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Date)})")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {const_proj.DBAdjustTableName} (
            {', '.join(columns)}
        )
        """
        self.dbCursor.execute(sql)
        self.dbConnect.commit()


    #创建日线股市表
    def CreateDailyTable(self):
        self.dailyDbStruct = DailyDBStruct.DBStructClass()
        columns = []

        for key in self.dailyDbStruct.dic.keys():
            columnName = self.dailyDbStruct.GetNameByEnum(key)
            dbType = self.dailyDbStruct.GetDBTypeByEnum(key)
            columns.append(f"{columnName} {dbType}")

        columns.append(f"PRIMARY KEY ({self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)}, {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)})")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {const_proj.DBDailyTableName} (
            {', '.join(columns)}
        )
        """
        self.dbCursor.execute(sql)
        self.dbConnect.commit()



    def GetTableNameByEnum(self, tableEnum):
        if tableEnum == TableEnum.Basic:
            return const_proj.DBBasicTableName
        elif tableEnum == TableEnum.Daily:
            return const_proj.DBDailyTableName
        elif tableEnum == TableEnum.Adjust:
            return const_proj.DBAdjustTableName

    #读入行
    def ReadRow(self, table_name):
        sql = f'SELECT * FROM {table_name}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        logstr = ""
        for row in allRow:
            structClass = BasicDBStruct.DBStructClass()
            for idx, key in enumerate(self.dbStruct.dic.keys()):
                dicKey = self.dbStruct.GetNameByEnum(key)
                structClass.dic[dicKey] = row[idx]
                logstr += f"key={dicKey}, val={row[idx]}, name= {self.dbStruct.GetNameByEnum(key)}, disc = {self.dbStruct.GetDiscByEnum(key)}\n"
            self.LogTxt(logstr)
            return structClass
        else:
            return None

    async def WriteTable(self, classList, table_enum):
        strhead = "正在处理"
        if table_enum == TableEnum.Basic:
            strhead = "数据库写入基本数据，"
        elif table_enum == TableEnum.Daily:
            strhead = "数据库写入日线数据，"
        elif table_enum == TableEnum.Adjust:
            strhead = "数据库写入复权数据，"
        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""
        classLen = len(classList)
        table_name = self.GetTableNameByEnum(table_enum)


        self.main.BoardCast(f"{strhead}共 {classLen} 条")

        # 获取列名（所有 structClass 结构相同，取第一个即可）
        first_row = classList[0]
        columns = []
        for k in first_row.dic.keys():
            name = first_row.GetNameByEnum(k)
            columns.append(f'"{name}"')
        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        sql = f'INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders})'

        # 关键：关闭自动提交，手动控制事务
        self.dbConnect.execute("BEGIN;")  # 显式开始事务

        try:
            batch_size = 10000  # 每批 1 万条（可调）
            total_written = 0

            for i in range(0, classLen, batch_size):
                batch = classList[i:i + batch_size]
                values_list = []

                for data in batch:
                    # 构造值元组
                    vals = tuple(str(data.dic[k]) for k in data.dic.keys())
                    values_list.append(vals)

                # 批量插入
                self.dbCursor.executemany(sql, values_list)
                total_written += len(batch)

                # 每批广播一次进度（避免太频繁）
                if total_written % batch_size == 0 or total_written == classLen:
                    progress = total_written
                    # 简化时间估算（因为现在速度极快，预估意义不大，可只显示进度）
                    msg = f"{strhead}已写入 {progress}/{classLen} 条"
                    #await self.main.BoardCast(msg)
                    print(msg)

                # 让出控制权，避免阻塞事件循环
                await asyncio.sleep(0)

            # 提交整个事务
            self.dbConnect.commit()
            self.main.BoardCast(f"{strhead}写入完成！共 {classLen} 条")

        except Exception as e:
            self.dbConnect.rollback()
            await self.main.BoardCast(f"写入失败: {e}")
            raise



        #logCount = 0
        #for data in classList:
        #    t0 = time.perf_counter()
        #    count_stock = count_stock + 1

        #    self.WriteRow(data, table_enum)
        #    t1 = time.perf_counter()

        #    totalCostTime = totalCostTime + (t1 - t0)
        #    preCostTime = (totalCostTime / count_stock) * (len(classList) - count_stock)
        #    totalCostTimeStr = self.format_seconds(totalCostTime)
        #    preCostTimeStr = self.format_seconds(preCostTime)
        #    if(logCount > 100):
        #        self.main.BoardCast(f"{str}当前第{count_stock}条,数据长度为:{classLen}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
        #        logCount = 0
        #    logCount = logCount + 1
        #    print(f"{str}当前第{count_stock}条,数据长度为:{classLen}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
        #    await asyncio.sleep(0)

    #写入行
    def WriteRow(self, structClass, table_enum):
        table_name = self.GetTableNameByEnum(table_enum)
        rowDic = structClass.dic
        columns = []
        values = []
        for k, val in rowDic.items():
            name = structClass.GetNameByEnum(k)
            columns.append(f'"{name}"')
            values.append(str(val))
        
        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(values))
        sql = f'INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders})'

        self.dbCursor.execute(sql, tuple(values))
        self.dbConnect.commit()

    def GetAllStockCodeFromBasicTable(self):
        sql = f'SELECT {self.basicDbStruct.GetNameByEnum(BasicDBStruct.ColumnEnum.Ts_code)} FROM {const_proj.DBBasicTableName}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        sameList = set()
        codeList = []
        for row in allRow:
            if(row[0] in sameList):
                continue
            codeList.append(row[0])
            sameList.add(row[0])


        return codeList
    


    def format_seconds(self, seconds: float) -> str:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"