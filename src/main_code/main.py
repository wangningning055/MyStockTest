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

    #获取测试的股票数据并写入数据库
    classList = requester.GetStockBasicData(True)
    count = 1
    for data in classList:
        print(f"正在写入第{count}条基本数据,数据长度为:{len(classList)}")
        count = count + 1
        dbHandler.WriteRow(data, db.DBHandle.TableEnum.Basic)

    #dataClassList = requester.GetStockDailyData()
    #for data in dataClassList:
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)

    #codeList = requester.GetBaoStockCodeByBasicDataBase()


    #print(f"获取第一组测试数据: {codeList[0]}")


    #dataClassList1 = requester.GetStockDailyData(codeList[0], "2025-01-01", "2026-01-20")
    #for data in dataClassList1:
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)
    #print("获取完成")


    #print(f"获取第二组测试数据: {codeList[1]}")
    #dataClassList2 = requester.GetStockDailyData(codeList[1], "2025-01-01", "2026-01-20")
    #for data in dataClassList2:
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)
    #print("获取完成")


    #print(f"获取第三组测试数据: {codeList[2]}")
    #dataClassList3 = requester.GetStockDailyData(codeList[2], "2025-01-01", "2026-01-20")
    #for data in dataClassList3:
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)
    #print("全部获取完成")

    print("程序结束")

if __name__ == "__main__":
    main()