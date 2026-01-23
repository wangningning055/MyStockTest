import db.DBHandle
import DataRequest.DataRequester
import pandas as pd
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


first_Data = "20200101"
update_date_file_name = "last_update_date.txt"
def main():
    print("Hello, Python Project!")

    
    dbHandler = db.DBHandle.DBHandler("../DB/test.db")
    #如果不存在表则创建表
    dbHandler.CreateTable()
    requester = DataRequest.DataRequester.DataRequesterClass()

    #获取当天的日期
    today_str = datetime.today().strftime("%Y%m%d")
    lastDayStr = first_Data
    if not os.path.exists(update_date_file_name):
        lastDayStr = first_Data
    else:
        with open(update_date_file_name, "r", encoding="utf-8") as f:
            lastDayStr = f.read().strip()

    lastDayStr = first_Data
    if lastDayStr == today_str:
        print("是最新数据，无需拉取")
    else:
        print(f"拉取数据区间为：{lastDayStr}  ----  {today_str}")
        RequestData(dbHandler, requester, lastDayStr, today_str)

    with open("last_update_date.txt", "w", encoding="utf-8") as f:
        f.write(today_str)

    print("基本数据和日线数据写入完成")

    print("程序结束")


def RequestData(dbHandler : "db.DBHandle.DBHandler", requester : DataRequest.DataRequester.DataRequesterClass, fromData, toData):
    #拉取股票列表数据并写入数据库
    print("开始拉取股票基础数据")
    #classList = requester.GetStockBasicData(False)
    #count = 1
    #for data in classList:
    #    print(f"正在写入第{count}条基本数据,数据长度为:{len(classList)}")
    #    count = count + 1
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Basic)
    print("股票基础数据处理完毕")

    #获取股票代码列表
    codeList = dbHandler.GetAllStockCodeFromBasicTable()

    print("开始拉取复权因子")

    count_stock = 1
    for code in codeList:
        newCode = requester.tushare_to_baostock(code)
        dataClassList = requester.GetStockAdjustData(code, first_Data, toData)
        print(f"正在获取股票代码:{newCode}的复权数据, 日期为{first_Data}到{toData}，长度为：{len(codeList)},这是第{count_stock}只股票,复权长度为{len(dataClassList)}")
        count_stock = count_stock + 1

        for data in dataClassList:
            #print(f"正在写入第{count}条复权数据,数据长度为:{len(dataClassList)}")
            dbHandler.WriteRow(data, db.DBHandle.TableEnum.Adjust)

    print("复权因子处理完毕")


    print("开始拉取日线数据")
    #count_stock = 1
    ##获取测试的股票日线数据并写入数据库
    #for code in codeList:
    #    newCode = requester.tushare_to_baostock(code)
    #    print(f"正在获取股票代码:{newCode}的日线数据, 日期为{first_Data}到{toData}，长度为：{len(codeList)},这是第{count_stock}只股票")
    #    dataClassList = requester.GetStockDailyData(code, fromData, toData, True)
    #    count_stock = count_stock + 1

    #    count = 1
    #    for data in dataClassList:
    #        print(f"正在写入第{count}条日线数据,数据长度为:{len(dataClassList)}")
    #        count = count + 1
    #        dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)
    print("日线数据处理完毕")



if __name__ == "__main__":
    main()