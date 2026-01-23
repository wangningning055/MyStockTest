import db.DBHandle
import DataRequest.DataRequester
import pandas as pd
import sys
import os
import time
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
    #totalCostTime = 0
    #preCostTime = 0
    #count_stock = 0
    #print("开始拉取股票基础数据")
    #classList = requester.GetStockBasicData(True)
    #for data in classList:
    #    t0 = time.perf_counter()
    #    count_stock = count_stock + 1
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Basic)
    #    t1 = time.perf_counter()

    #    totalCostTime = totalCostTime + (t1 - t0)
    #    preCostTime = (totalCostTime / count_stock) * (len(classList) - count_stock)
    #    totalCostTimeStr = format_seconds(totalCostTime)
    #    preCostTimeStr = format_seconds(preCostTime)
    #    print(f"写入第{count_stock}条基本数据,数据长度为:{len(classList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
    print("股票基础数据处理完毕")

    #获取股票代码列表
    codeList = dbHandler.GetAllStockCodeFromBasicTable()

    print("开始拉取复权因子")
    totalCostTime = 0
    preCostTime = 0
    count_stock = 0
    for code in codeList:
        t0 = time.perf_counter()
        newCode = requester.tushare_to_baostock(code)
        dataClassList = requester.GetStockAdjustData(code, first_Data, toData)
        count_stock = count_stock + 1

        for data in dataClassList:
            #print(f"正在写入第{count}条复权数据,数据长度为:{len(dataClassList)}")
            dbHandler.WriteRow(data, db.DBHandle.TableEnum.Adjust)
        t1 = time.perf_counter()

        totalCostTime = totalCostTime + (t1 - t0)
        preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
        totalCostTimeStr = format_seconds(totalCostTime)
        preCostTimeStr = format_seconds(preCostTime)
        print(f"获取股票代码:{newCode}的复权数据, 日期为{first_Data}到{toData}，长度为：{len(codeList)},这是第{count_stock}只股票,复权长度为{len(dataClassList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")

    print("复权因子处理完毕")


    print("开始拉取日线数据")
    #totalCostTime = 0
    #preCostTime = 0
    #count_stock = 0
    ###获取测试的股票日线数据并写入数据库
    #for code in codeList:
    #    t0 = time.perf_counter()
    #    newCode = requester.tushare_to_baostock(code)
    #    dataClassList = requester.GetStockDailyData(code, fromData, toData, True)
    #    count_stock = count_stock + 1

    #    count = 1
    #    for data in dataClassList:
    #        count = count + 1
    #        dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)
    #    t1 = time.perf_counter()

    #    totalCostTime = totalCostTime + (t1 - t0)
    #    preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
    #    totalCostTimeStr = format_seconds(totalCostTime)
    #    preCostTimeStr = format_seconds(preCostTime)
    #    print(f"写入股票代码:{newCode}的日线数据, 日期为{first_Data}到{toData}，长度为：{len(codeList)},这是第{count_stock}只股票， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr} ")

    print("日线数据处理完毕")


def format_seconds(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

if __name__ == "__main__":
    main()