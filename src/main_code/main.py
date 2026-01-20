import db.DBHandle
import DataRequest.DataRequester
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
def main():
    print("Hello, Python Project!")

    
    dbHandler = db.DBHandle.DBHandler("../DB/test.db")
    #如果不存在表则创建表
    dbHandler.CreateTable()

    requester = DataRequest.DataRequester.DataRequesterClass()
    #requester.GetStockBasicData()

    #获取测试的股票数据并写入数据库
    #classList = requester.GetStockDailyData()
    #for dataClass in classList:
    #    dbHandler.WriteRow(dataClass, db.DBHandle.TableEnum.Daily)

    # 获取交易日历
    tradeDaysDf = requester.GetStockTradeDaily("20250101", "20260119")
    print(tradeDaysDf.head())

if __name__ == "__main__":
    main()