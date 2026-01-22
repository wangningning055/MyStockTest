import db.DBHandle
import DataRequest.DataRequester
import pandas as pd
import sys
first_Data = "20251201"
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
def main():
    print("Hello, Python Project!")

    
    dbHandler = db.DBHandle.DBHandler("../DB/test.db")
    #如果不存在表则创建表
    dbHandler.CreateTable()

    requester = DataRequest.DataRequester.DataRequesterClass()

    #获取测试的股票列表数据并写入数据库
    #classList = requester.GetStockBasicData(False)
    #count = 1
    #for data in classList:
    #    print(f"正在写入第{count}条基本数据,数据长度为:{len(classList)}")
    #    count = count + 1
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Basic)

    #获取股票代码列表
    codeList = dbHandler.GetAllStockCodeFromBasicTable()

    #获取测试的股票日线数据并写入数据库
    toData = 20251222
    count_stock = 1
    count_api = 1
    result = requester.gen_year_quarter_range(first_Data, toData)
    print(f"预计api调用次数为{len(result) * len(codeList)}次")
    all_quarters = []
    for year, quarter in result:
        count_api = count_api + 1
        print(f"正在获取{year}年第{quarter}季度的数据,长度为：{len(result)},当前api调用为{count_api}次")
        res = requester.GetStockQuarterData("sz.300591", year, quarter, True)
        if res is not None:
            all_quarters.append(res)

    if all_quarters:
        stock_df = pd.concat(all_quarters, ignore_index=True)
        stock_df.to_csv(f"stock_quarter_baostock_value_300591.csv")

    #for code in codeList:
    #    newCode = requester.tushare_to_baostock(code)
    #    #print(f"正在获取股票代码:{newCode}的日线数据, 日期为{first_Data}到{toData}，长度为：{len(codeList)},这是第{count_stock}只股票,计算数量是{len(result)}")
    #    count_stock = count_stock + 1
    #    all_quarters = []
        #for year, quarter in result:
        #    count_api = count_api + 1
        #    print(f"正在获取{year}年第{quarter}季度的数据,长度为：{len(result)},当前api调用为{count_api}次")

        #    if res is not None:
        #        all_quarters.append(res)

        #if all_quarters:
        #    stock_df = pd.concat(all_quarters, ignore_index=True)
        #    stock_df.to_csv(f"stock_quarter_baostock_value_{newCode}.csv")


        #result_profit.to_csv(f"stock_quarter_baostock_value_{baoStockCode}.csv", encoding="gbk", index=False)

        #dataClassList = requester.GetStockDailyData(code, first_Data, toData, False)
        #count = 1
        #for data in dataClassList:
        #    print(f"正在写入第{count}条日线数据,数据长度为:{len(dataClassList)}")
        #    count = count + 1
        #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)


    print("基本数据和日线数据写入完成.api调用总次数为:", count_api)
    #count = 1
    #for data in dataClassList:
    #    print(f"正在写入第{count}条基本数据,数据长度为:{len(dataClassList)}")
    #    count = count + 1
    #    dbHandler.WriteRow(data, db.DBHandle.TableEnum.Daily)


    print("程序结束")

if __name__ == "__main__":
    main()