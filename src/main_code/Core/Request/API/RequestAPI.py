import src.main_code.Core.Const
import baostock as bs
import tushare as ts
import pandas as pd

from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
import src.main_code.Core.Const as const_proj
import src.main_code.Core as Core
from datetime import datetime

class RequestAPIClass:
    def init(self):
        self.tuShareToken = Core.Const.token2
        ts.set_token(self.tuShareToken)
        self.pro = ts.pro_api()
        self.bao = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+self.bao.error_code)
        print('login respond  error_msg:'+self.bao.error_msg)
        print("登录流程结束")



    #拉取基本数据
    def Request_Basic(self):
        df = self.pro.stock_basic(
        exchange='',       # 空表示所有交易所
        list_status='L',   # L = 上市中
        fields='ts_code,symbol,name,area,industry,market,cnspell,list_date,act_name,act_ent_type,list_status')
        return df


    #拉取基本数据
    def Request_Company(self, exchangeName):
        df = self.pro.stock_company(exchange=exchangeName)
        return df



    # 拉取复权因子 code的形式是xxxxxxx.SZ
    def Request_Adjust(self, stockCode):
        #获取复权因子
        code = self.TuShare_to_BaoStock(stockCode)
        rs_list = []
        rs_factor = bs.query_adjust_factor(code=code)
        while (rs_factor.error_code == '0') & rs_factor.next():
            rs_list.append(rs_factor.get_row_data())

        if rs_list.__len__() != 0:
            result_factor = pd.DataFrame(rs_list, columns=rs_factor.fields)
        else:
            return None

        return result_factor
    


    #拉取日线信息StockCode为xxxxx.SZ的格式
    def RequestDaily(self, baoStockCode : str, startData_Base, endData_Base):
        if(baoStockCode.__contains__("bj")):
            return None
        if(baoStockCode.__contains__("BJ")):
            return None
            #print("北交所的行情暂不支持:", baoStockCode)
        code = self.TuShare_to_BaoStock(baoStockCode)
        startData = self.Time_Convert_Base_To_Bao(startData_Base)
        endData = self.Time_Convert_Base_To_Bao(endData_Base)
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


        if data_list.__len__() != 0:
            df = pd.DataFrame(data_list, columns=rs.fields)
        else:
            return None

        return df
    


        

    def Df_To_BasicClass(self, dfBasic, dfSZSE, dfSSE, dfBSE):
        if dfBasic is None:
            return None
        if dfSZSE is None:
            return None
        if dfSSE is None:
            return None
        if dfBSE is None:
            return None
        classList = []
        alldic = {}
        for _, row in dfBasic.iterrows():
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

        for _,row in dfSZSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        print("开始单独处理上交所")
        for _,row in dfSSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        print("开始单独处理北交所")
        for _,row in dfBSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']
        return classList

    def Df_To_AdjustClass(self, df):
        if df is None:
            return None
        dataClassList = []
        for _, row in df.iterrows():
            dataClass = AdjustDBStruct.DBStructClass()
            dataClass.dic[AdjustDBStruct.ColumnEnum.Code] = self.BaoStock_to_TuShare(row['code'])
            dataClass.dic[AdjustDBStruct.ColumnEnum.Date] = self.Time_Convert_Bao_To_Base(row['dividOperateDate'])
            dataClass.dic[AdjustDBStruct.ColumnEnum.For_Adjust] = row['foreAdjustFactor']
            dataClass.dic[AdjustDBStruct.ColumnEnum.Back_Adjust] = row['backAdjustFactor']
            dataClassList.append(dataClass)
        return dataClassList

    def Df_To_DailyClass(self, df):
        if df is None:
            return None
        dataClassList = []
        for _, row in df.iterrows():
            dataClass = DailyDBStruct.DBStructClass()
            dataClass.dic[DailyDBStruct.ColumnEnum.Code] = self.BaoStock_to_TuShare(row['code'])
            dataClass.dic[DailyDBStruct.ColumnEnum.Date] = self.Time_Convert_Bao_To_Base(row['date'])
            dataClass.dic[DailyDBStruct.ColumnEnum.Open_Price] = self.CleanData(row['open'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Close_Price] = self.CleanData(row['close'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.High_Price] = self.CleanData(row['high'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Low_Price] = self.CleanData(row['low'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Exchange_Hand] = self.CleanData(row['turn'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Change_Ratio] = self.CleanData(row['pctChg'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Amount] = self.CleanData(row['volume'], 2)
            dataClass.dic[DailyDBStruct.ColumnEnum.Amount_Price] = self.CleanData(row['amount'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Earn_TTM] = self.CleanData(row['peTTM'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Clean] = self.CleanData(row['pbMRQ'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Cash_TTM] = self.CleanData(row['pcfNcfTTM'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Sale_TTM] = self.CleanData(row['psTTM'], 1)
            dataClass.dic[DailyDBStruct.ColumnEnum.Is_ST] = self.CleanData(row['isST'], 2)
            dataClass.dic[DailyDBStruct.ColumnEnum.Is_Trading] = self.CleanData(row['tradestatus'], 2)
            dataClass.dic[DailyDBStruct.ColumnEnum.Last_Close_Price] = self.CleanData(row['preclose'], 1)
            dataClassList.append(dataClass)
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




    #把12-02-3 或者 12/02/23  变成120203
    def Time_Convert_Bao_To_Base(self, timestr):
        date_num = timestr.replace("-", "")
        date_num = date_num.replace("/", "")
        return date_num
    #把120203 变成12-02-03
    def Time_Convert_Base_To_Bao(self, timestr):
        date_fmt = datetime.strptime(timestr, "%Y%m%d").strftime("%Y-%m-%d")
        return date_fmt
    



    #把baoStock里面的sh.600000股票代码变为600000.SH格式
    def BaoStock_to_TuShare(self, dataStr):
        exchange, num = dataStr.split(".")
        return f"{num}.{exchange.upper()}"
    
    #把baoStock里面的600000.SH股票代码变为格式sh.600000
    def TuShare_to_BaoStock(self, dataStr):
        if(dataStr.__contains__(".")):
            num, exchange = dataStr.split(".")
            return f"{exchange.lower()}.{num}"
        else:
            return""

    ##获得季度数据，总股本流通股本
    #def GetStockQuarterData(self, baoStockCode, year, quarter, isNeedPull):
    #    if isNeedPull:
    #        profit_list = []
    #        rs_profit = bs.query_profit_data(code=baoStockCode, year=year, quarter=quarter)
    #        while (rs_profit.error_code == '0') & rs_profit.next():
    #            profit_list.append(rs_profit.get_row_data())
    #        result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
    #        result_profit.to_csv(f"stock_quarter_baostock_profit1111111_{baoStockCode}_{year}Q{quarter}.csv", index=False)
    #        result_profit["year"] = year
    #        result_profit["quarter"] = quarter

    
    #def date_to_year_quarter(self, date_int: int):
    #    """
    #    20200115 -> (2020, 1)
    #    """
    #    date_str = str(date_int)
    #    year = int(date_str[:4])
    #    month = int(date_str[4:6])

    #    if month <= 3:
    #        quarter = 1
    #    elif month <= 6:
    #        quarter = 2
    #    elif month <= 9:
    #        quarter = 3
    #    else:
    #        quarter = 4

    #    return year, quarter
    


    #def gen_year_quarter_range(self, start_date: int, end_date: int):
    #    sy, sq = self.date_to_year_quarter(start_date)
    #    ey, eq = self.date_to_year_quarter(end_date)

    #    result = []

    #    y, q = sy, sq
    #    while True:
    #        result.append((y, q))

    #        if y == ey and q == eq:
    #            break

    #        q += 1
    #        if q == 5:
    #            q = 1
    #            y += 1

    #    return result