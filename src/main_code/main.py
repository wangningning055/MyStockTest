import db.DBHandle
import DataRequest.DataRequester
def main():
    print("Hello, Python Project!")

    
    dbHandler = db.DBHandle.DBHandler("../DB/test.db")
    #如果不存在表则创建表
    dbHandler.CreateTable()

    requester = DataRequest.DataRequester.DataRequesterClass()
    #requester.GetStockBasicData()

    #获取测试的股票数据
    classList = requester.GetStockDailyData()
    for dataClass in classList:
        dbHandler.WriteRow(dataClass, db.DBHandle.TableEnum.Daily)


if __name__ == "__main__":
    main()