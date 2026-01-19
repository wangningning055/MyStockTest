import db.DBHandle
def main():
    print("Hello, Python Project!")

    
    dbHandler = db.DBHandle.DBHandler("../DB/test.db")

    #创建数据库表
    dbHandler.CreateTable()
    #dbHandler.TestWrite()
    struct = dbHandler.ReadRow()


if __name__ == "__main__":
    main()