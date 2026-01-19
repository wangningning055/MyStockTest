import sqlite3
from . import DBStruct

class DBHandler:
    DbName = "MyDb"
    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.ReadDb()

    #读取数据库
    def ReadDb(self):
        self.dbConnect = sqlite3.connect(self.dbPath)
        self.dbCursor = self.dbConnect.cursor()
        self.CreateTable()

    #创建表
    def CreateTable(self):
        self.dbStruct = DBStruct.DBStructClass()
        columns = []
        for key, value in self.dbStruct.dic.items():
            columnName = self.dbStruct.GetNameByEnum(key)
            if key == DBStruct.ColumnEnum.Code:
                columns.append(f"{columnName} INTEGER PRIMARY KEY")
            else:
                columns.append(f"{columnName} TEXT")

        sql = f"""CREATE TABLE IF NOT EXISTS {self.DbName} (
            {', '.join(columns)}
        )"""
        #print(sql)
        #print("...............................................")
        self.dbCursor.execute(sql)
        self.dbConnect.commit()

    def ReadRow(self):
        sql = f'SELECT * FROM {self.DbName}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        logstr = ""
        for row in allRow:
            structClass = DBStruct.DBStructClass()
            for idx, key in enumerate(self.dbStruct.dic.keys()):
                dicKey = self.dbStruct.GetNameByEnum(key)
                structClass.dic[dicKey] = row[idx]
                logstr += f"key={dicKey}, val={row[idx]}, name= {self.dbStruct.GetNameByEnum(key)}, disc = {self.dbStruct.GetDiscByEnum(key)}\n"
            self.LogTxt(logstr)
            return structClass
        else:
            return None


    #写入行
    def WriteRow(self, structClass):
        rowDic = structClass.dic
        print("Writing Row:rowDic.keys()=", len(rowDic.keys()))
        columns = []
        values = []
        for k, val in rowDic.items():
            name = self.dbStruct.GetNameByEnum(k)
            columns.append(f'"{name}"')
            values.append(str(val))
        
        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(values))
        sql = f'INSERT INTO MyDb ({columns_sql}) VALUES ({placeholders})'

        #print(sql)
        #print(".....................我是分隔符..........................")
        #print(values)
        self.dbCursor.execute(sql, tuple(values))
        self.dbConnect.commit()



    def TestWrite(self):
        structClass = DBStruct.DBStructClass()
        structClass.CreateDic()
        structClass.dic[DBStruct.ColumnEnum.Code] = 1
        structClass.dic[DBStruct.ColumnEnum.Date] = "2024-01-01"
        structClass.dic[DBStruct.ColumnEnum.Open_Price] = "10.5"
        structClass.dic[DBStruct.ColumnEnum.Close_Price] = "10.8"
        structClass.dic[DBStruct.ColumnEnum.Name] = "TestStock"
        structClass.dic[DBStruct.ColumnEnum.High_Price] = "11.0"
        structClass.dic[DBStruct.ColumnEnum.Low_Price] = "10.2"
        structClass.dic[DBStruct.ColumnEnum.Change_Num] = "0.3"
        structClass.dic[DBStruct.ColumnEnum.Change_Ratio] = "2.86"
        structClass.dic[DBStruct.ColumnEnum.Amount] = "1000"
        structClass.dic[DBStruct.ColumnEnum.Amount_Price] = "10500"
        structClass.dic[DBStruct.ColumnEnum.Hand] = "1.5"
        structClass.dic[DBStruct.ColumnEnum.Hand_All] = "2.0"
        structClass.dic[DBStruct.ColumnEnum.Volume_Ratio] = "1.2"
        structClass.dic[DBStruct.ColumnEnum.Earn_Static] = "15.0"
        structClass.dic[DBStruct.ColumnEnum.Earn_TTM] = "14.5"
        structClass.dic[DBStruct.ColumnEnum.Clean] = "1.8"
        structClass.dic[DBStruct.ColumnEnum.Sale] = "2.5"
        structClass.dic[DBStruct.ColumnEnum.Sale_TTM] = "2.3"
        structClass.dic[DBStruct.ColumnEnum.All_Hand] = "50000"
        structClass.dic[DBStruct.ColumnEnum.Flow_Hand] = "30000"
        structClass.dic[DBStruct.ColumnEnum.Free_Flow_Hand] = "20000"
        structClass.dic[DBStruct.ColumnEnum.Total_Market_Price] = "550000"
        structClass.dic[DBStruct.ColumnEnum.Flow_Market_Price] = "330000"
        structClass.dic[DBStruct.ColumnEnum.Name] = "TestStock"
        self.WriteRow(structClass)

    def LogTxt(self, msg):
        txt_file_path = "output.txt"
        # 写入文件，使用 utf-8 编码
        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(msg)

        print(f"write Success {txt_file_path}")