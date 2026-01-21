import sqlite3
from db.Define import AllDataDBStruct
from db.Define import BasicDBStruct
from db.Define import DailyDBStruct
from enum import Enum

class TableEnum(Enum):
    Basic = 1,
    Daily = 2,
    Total = 3,

class DBHandler:
    BasicTableName = "Basic"
    DailyTableName = "Daily"
    DbName = "TotalDB"

    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.ConnectDb()
        print("链接数据库成功:", dbPath)
        self.CreateTable()
        print("创建数据表成功:", dbPath)

    #读取数据库
    def ConnectDb(self):
        self.dbConnect = sqlite3.connect(self.dbPath)
        self.dbCursor = self.dbConnect.cursor()
    #创建数据库表
    def CreateTable(self):
        self.CreateBasicTable()
        self.CreateDailyTable()

    #创建基础股市表
    def CreateBasicTable(self):
        self.basicDbStruct = BasicDBStruct.BasicDBStructClass()
        columns = []
        for key, value in self.basicDbStruct.dic.items():
            columnName = self.basicDbStruct.GetNameByEnum(key)
            dbType = self.basicDbStruct.GetDBTypeByEnum(key)
            if key == BasicDBStruct.ColumnEnum.Code:
                columns.append(f"{columnName} {dbType} PRIMARY KEY")
            else:
                columns.append(f"{columnName} {dbType}")
        sql = f"""CREATE TABLE IF NOT EXISTS {self.BasicTableName} (
            {', '.join(columns)}
        )"""
        self.dbCursor.execute(sql)
        self.dbConnect.commit()

    #创建日线股市表
    def CreateDailyTable(self):
        self.dailyDbStruct = DailyDBStruct.DailyDBStructClass()
        columns = []

        for key in self.dailyDbStruct.dic.keys():
            columnName = self.dailyDbStruct.GetNameByEnum(key)
            dbType = self.dailyDbStruct.GetDBTypeByEnum(key)
            columns.append(f"{columnName} {dbType}")

        columns.append(f"PRIMARY KEY ({self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)}, {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)})")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.DailyTableName} (
            {', '.join(columns)}
        )
        """
        self.dbCursor.execute(sql)
        self.dbConnect.commit()



    def GetTableNameByEnum(self, tableEnum):
        if tableEnum == TableEnum.Basic:
            return self.BasicTableName
        elif tableEnum == TableEnum.Daily:
            return self.DailyTableName
        elif tableEnum == TableEnum.Total:
            return self.DbName

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


    #def TestWrite(self):
    #    structClass = DBStruct.DBStructClass()
    #    structClass.CreateDic()
    #    structClass.dic[DBStruct.ColumnEnum.Code] = 1
    #    structClass.dic[DBStruct.ColumnEnum.Date] = "2024-01-01"
    #    structClass.dic[DBStruct.ColumnEnum.Open_Price] = "10.5"
    #    structClass.dic[DBStruct.ColumnEnum.Close_Price] = "10.8"
    #    structClass.dic[DBStruct.ColumnEnum.Name] = "TestStock"
    #    structClass.dic[DBStruct.ColumnEnum.High_Price] = "11.0"
    #    structClass.dic[DBStruct.ColumnEnum.Low_Price] = "10.2"
    #    structClass.dic[DBStruct.ColumnEnum.Change_Num] = "0.3"
    #    structClass.dic[DBStruct.ColumnEnum.Change_Ratio] = "2.86"
    #    structClass.dic[DBStruct.ColumnEnum.Amount] = "1000"
    #    structClass.dic[DBStruct.ColumnEnum.Amount_Price] = "10500"
    #    structClass.dic[DBStruct.ColumnEnum.Hand] = "1.5"
    #    structClass.dic[DBStruct.ColumnEnum.Hand_All] = "2.0"
    #    structClass.dic[DBStruct.ColumnEnum.Volume_Ratio] = "1.2"
    #    structClass.dic[DBStruct.ColumnEnum.Earn_Static] = "15.0"
    #    structClass.dic[DBStruct.ColumnEnum.Earn_TTM] = "14.5"
    #    structClass.dic[DBStruct.ColumnEnum.Clean] = "1.8"
    #    structClass.dic[DBStruct.ColumnEnum.Sale] = "2.5"
    #    structClass.dic[DBStruct.ColumnEnum.Sale_TTM] = "2.3"
    #    structClass.dic[DBStruct.ColumnEnum.All_Hand] = "50000"
    #    structClass.dic[DBStruct.ColumnEnum.Flow_Hand] = "30000"
    #    structClass.dic[DBStruct.ColumnEnum.Free_Flow_Hand] = "20000"
    #    structClass.dic[DBStruct.ColumnEnum.Total_Market_Price] = "550000"
    #    structClass.dic[DBStruct.ColumnEnum.Flow_Market_Price] = "330000"
    #    structClass.dic[DBStruct.ColumnEnum.Name] = "TestStock"
    #    self.WriteRow(structClass)

    #def LogTxt(self, msg):
    #    txt_file_path = "output.txt"
    #    # 写入文件，使用 utf-8 编码
    #    with open(txt_file_path, "w", encoding="utf-8") as f:
    #        f.write(msg)

    #    print(f"write Success {txt_file_path}")