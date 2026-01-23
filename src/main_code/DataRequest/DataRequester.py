import baostock as bs
import tushare as ts
import pandas as pd
import csv
from db.Define import BasicDBStruct
from db.Define import DailyDBStruct
from db.Define import AdjustDBStruct
from datetime import datetime

class DataRequesterClass:
    #token = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
    #token = "323752147f60806f5823e0209c317ce5aa507863fa9184b3cd7d5839"
    token = "b067c471d2ee1b3875e75d01169b8a64d0707e4d1e2cb42d2ca502be"
    
    def __init__(self):
        self.InitShare()

    def InitShare(self):
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        self.bao = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+self.bao.error_code)
        print('login respond  error_msg:'+self.bao.error_msg)
        print("登录流程结束")
    #获取股票的交易日历(本地计算)
    def GetStockTradeDaily(self, start_date, end_date):

        # 生成工作日（周一到周五）
        calendar = pd.bdate_range(start=start_date, end=end_date)

        # 转成 DataFrame 并格式化为 YYYYMMDD
        df = pd.DataFrame(calendar, columns=["date"])
        df["date"] = df["date"].dt.strftime("%Y%m%d")  # 转为 20250103 格式
        df.to_csv("trading_days_local.csv", index=False)
        return df

    
    #获取股票的基本数据
    def GetStockBasicData(self, isNeedPull):
        if isNeedPull:
            print("拉取基本数据")
            df = self.pro.stock_basic(
                exchange='',       # 空表示所有交易所
                list_status='L',   # L = 上市中
                fields='ts_code,symbol,name,area,industry,market,cnspell,list_date,act_name,act_ent_type,list_status'
            )
            df.to_csv("allStock_base1.csv", index=False)

            print("拉取交易所SZSE数据")
            df2_1 = self.pro.stock_company(exchange='SZSE')
            df2_1.to_csv("allStock_base2_SZSE.csv", index=False)

            print("拉取交易所SSE数据")
            df2_2 = self.pro.stock_company(exchange='SSE')
            df2_2.to_csv("allStock_base2_SSE.csv", index=False)

            print("拉取交易所BSE数据")
            df2_3 = self.pro.stock_company(exchange='BSE')
            df2_3.to_csv("allStock_base2_BSE.csv", index=False)

        
        alldic = {}
        classList = []
        df_basic = pd.read_csv("allStock_base1.csv")
        df_1 = pd.read_csv("allStock_base2_SZSE.csv")
        df_2 = pd.read_csv("allStock_base2_SSE.csv")
        df_3 = pd.read_csv("allStock_base2_BSE.csv")
        for _, row in df_basic.iterrows():
            testClass = BasicDBStruct.DBStructClass()
            alldic[row['ts_code']] = testClass
            testClass.dic[BasicDBStruct.ColumnEnum.Ts_code] = row['ts_code']
            testClass.dic[BasicDBStruct.ColumnEnum.Code] = row['symbol']
            testClass.dic[BasicDBStruct.ColumnEnum.Name] = row['name']
            testClass.dic[BasicDBStruct.ColumnEnum.Area] = row['area']
            testClass.dic[BasicDBStruct.ColumnEnum.Industry] = row['industry']
            testClass.dic[BasicDBStruct.ColumnEnum.Cn_spell] = row['cnspell']
            testClass.dic[BasicDBStruct.ColumnEnum.Market] = row['market']
            testClass.dic[BasicDBStruct.ColumnEnum.List_Status] = row['list_status']
            testClass.dic[BasicDBStruct.ColumnEnum.List_date] = row['list_date']
            testClass.dic[BasicDBStruct.ColumnEnum.Act_name] = row['act_name']
            testClass.dic[BasicDBStruct.ColumnEnum.Act_ent_type] = row['act_ent_type']
            classList.append(testClass)
        print(f"基本数据处理完毕,数据长度是:{len(alldic)}")
        print("开始单独处理深交所")

        for _,row in df_1.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        print("开始单独处理上交所")
        for _,row in df_2.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        print("开始单独处理北交所")
        for _,row in df_3.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']

        return classList

    #获取股票的复权数据:
    def GetStockAdjustData(self, baoStockCode : str, startData_Base, endData_Base):
        #获取复权因子
        rs_list = []
        rs_factor = bs.query_adjust_factor(code=baoStockCode)
        while (rs_factor.error_code == '0') & rs_factor.next():
            rs_list.append(rs_factor.get_row_data())

        dataClassList = []
        if rs_list.__len__() == 0:
            dataClass = AdjustDBStruct.DBStructClass()
            dataClass.dic[AdjustDBStruct.ColumnEnum.Code] = self.baostock_to_tushare(baoStockCode)
            dataClass.dic[AdjustDBStruct.ColumnEnum.Date] = startData_Base
            dataClass.dic[AdjustDBStruct.ColumnEnum.For_Adjust] = 1
            dataClassList.append(dataClass)

        else:
            result_factor = pd.DataFrame(rs_list, columns=rs_factor.fields)
            #result_factor.to_csv(f"stock_daily_baostock_adjst_{baoStockCode}.csv", index=False)
            for _, row in result_factor.iterrows():
                dataClass = AdjustDBStruct.DBStructClass()
                dataClass.dic[AdjustDBStruct.ColumnEnum.Code] = self.baostock_to_tushare(row['code'])
                dataClass.dic[AdjustDBStruct.ColumnEnum.Date] = self.Time_Convert_Bao_To_Base(row['dividOperateDate'])
                dataClass.dic[AdjustDBStruct.ColumnEnum.For_Adjust] = row['foreAdjustFactor']
                dataClass.dic[AdjustDBStruct.ColumnEnum.Back_Adjust] = row['backAdjustFactor']
                dataClassList.append(dataClass)

        return dataClassList


    #获取股票的日线行情
    def GetStockDailyData(self, baoStockCode : str, startData_Base, endData_Base, isNeedPull):
        if(baoStockCode.__contains__("bj")):
            return
            #print("北交所的行情暂不支持:", baoStockCode)
        startData = self.Time_Convert_Base_To_Bao(startData_Base)
        endData = self.Time_Convert_Base_To_Bao(endData_Base)
        print(f"转换后的日期是{startData}   到 {endData}")
        if isNeedPull:
            rs = bs.query_history_k_data_plus(
                baoStockCode,
                fields="date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
                start_date=startData,
                end_date=endData,
                frequency="d",
                adjustflag="3"
            )
            data_list = []
            if rs.error_code !='0':
                print("接口调用失败：", rs.error_msg)
                return
            while rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)
            df.to_csv(f"stock_daily_baostock_Basic_{baoStockCode}.csv", index=False)



        #封装数据类
        dataClassList = []
        #for _, row in df.iterrows():
        #    dataClass = DailyDBStruct.DBStructClass()
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Code] = self.baostock_to_tushare(row['code'])
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Date] = self.Time_Convert(row['date'])
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Open_Price] = self.CleanData(row['open'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Close_Price] = self.CleanData(row['close'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.High_Price] = self.CleanData(row['high'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Low_Price] = self.CleanData(row['low'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Exchange_Hand] = self.CleanData(row['turn'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Change_Ratio] = self.CleanData(row['pctChg'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Amount] = self.CleanData(row['volume'], 2)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Amount_Price] = self.CleanData(row['amount'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Earn_TTM] = self.CleanData(row['peTTM'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Clean] = self.CleanData(row['pbMRQ'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Cash_TTM] = self.CleanData(row['pcfNcfTTM'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Sale_TTM] = self.CleanData(row['psTTM'], 1)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Is_ST] = self.CleanData(row['isST'], 2)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Is_Trading] = self.CleanData(row['tradestatus'], 2)
        #    dataClass.dic[DailyDBStruct.ColumnEnum.Last_Close_Price] = self.CleanData(row['preclose'], 1)
        #    dataClassList.append(dataClass)
        return dataClassList


    


    #可能存在空的情况，这个时候转换不成功，需要主动置空，type：1是float， 2是int
    def CleanData(self, rowData, type):
        if rowData in (None, '', 'nan', 'NaN'):
            return 0
        else:
            if type == 1:
                return float(rowData)
            elif type == 2:
                return int(rowData)
            else:
                return rowData

    def LogTxt(self, msg):
        txt_file_path = "output.txt"
        # 写入文件，使用 utf-8 编码
        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(msg)

        print(f"write Success {txt_file_path}")



    #把baoStock里面的sh.600000股票代码变为600000.SH格式
    def baostock_to_tushare(self, dataStr):
        """
        sh.600000 -> 600000.SH
        sz.000001 -> 000001.SZ
        """
        exchange, num = dataStr.split(".")
        return f"{num}.{exchange.upper()}"
    
    #把baoStock里面的sh.600000股票代码变为600000.SH格式
    def tushare_to_baostock(self, dataStr):
        """
         600000.SH ->sh.600000
        """
        if(dataStr.__contains__(".")):
            num, exchange = dataStr.split(".")
            return f"{exchange.lower()}.{num}"
        else:
            return""

    #通过basic表来获取股票代码，然后转换为baoStock的代码格式
    def GetBaoStockCodeByBasicDataBase(self):
        list_code = []
        with open("allStock_base1.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    if(row[0].__contains__("BJ")):
                        pass
                    else:
                        newstr = self.tushare_to_baostock(row[0])
                        if newstr != "":
                            list_code.append(newstr)
        return list_code
    

    def Time_Convert_Bao_To_Base(self, timestr):
        date_num = timestr.replace("-", "")
        date_num = timestr.replace("/", "")
        return date_num
    
    def Time_Convert_Base_To_Bao(self, timestr):
        date_fmt = datetime.strptime(timestr, "%Y%m%d").strftime("%Y-%m-%d")
        return date_fmt













    #获得季度数据，总股本流通股本
    def GetStockQuarterData(self, baoStockCode, year, quarter, isNeedPull):
        if isNeedPull:
            profit_list = []
            rs_profit = bs.query_profit_data(code=baoStockCode, year=year, quarter=quarter)
            while (rs_profit.error_code == '0') & rs_profit.next():
                profit_list.append(rs_profit.get_row_data())
            result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
            result_profit.to_csv(f"stock_quarter_baostock_profit1111111_{baoStockCode}_{year}Q{quarter}.csv", index=False)
            result_profit["year"] = year
            result_profit["quarter"] = quarter

    
    def date_to_year_quarter(self, date_int: int):
        """
        20200115 -> (2020, 1)
        """
        date_str = str(date_int)
        year = int(date_str[:4])
        month = int(date_str[4:6])

        if month <= 3:
            quarter = 1
        elif month <= 6:
            quarter = 2
        elif month <= 9:
            quarter = 3
        else:
            quarter = 4

        return year, quarter
    


    def gen_year_quarter_range(self, start_date: int, end_date: int):
        sy, sq = self.date_to_year_quarter(start_date)
        ey, eq = self.date_to_year_quarter(end_date)

        result = []

        y, q = sy, sq
        while True:
            result.append((y, q))

            if y == ey and q == eq:
                break

            q += 1
            if q == 5:
                q = 1
                y += 1

        return result