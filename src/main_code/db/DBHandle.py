import sqlite3

class DBHandler:

    def __init__(self, dbPath):
        self.dbPath = dbPath

    #读取数据库
    def ReadDb(self):
        self.dbConnect = sqlite3.connect(self.dbPath)
        self.dbCursor = self.dbConnect.cursor()
        self.CreateTable()

    #创建表
    def CreateTable(self):
        self.dbCursor.execute("""
        CREATE TABLE IF NOT EXISTS MyDb (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER
        )
        """)
        self.dbConnect.commit()



    #写入行
    def WriteRow(self, row):
        self.dbCursor
        




class DBRowStruct:

    def __init__(self, id, name, age):
        self.DBColumnDic = {
        "id" : id,
        "name" : name,
        "age" : age
        }


