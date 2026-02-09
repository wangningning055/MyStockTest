import src.main_code.Core.Const
import baostock as bs
import tushare as ts
import pandas as pd
import akshare as ak
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
import src.main_code.Core.Const as const_proj
import src.main_code.Core as Core
from datetime import datetime
import asyncio

class RequestAPIClass:
    def init(self, main):
        self.main =main
        self.bao = bs.login()
        self.isInitShare = False
        # 显示登陆返回信息
        self.main.BoardCast('login respond error_code:'+self.bao.error_code)
        self.main.BoardCast('login respond  error_msg:'+self.bao.error_msg)
        self.main.BoardCast("登录流程结束")

    def initShare(self):
        try:
            self.tuShareToken = self.main.tuShareToken
            ts.set_token(self.tuShareToken)
            self.pro = ts.pro_api()
            self.isInitShare = True
        except Exception as e:
            print(f"tuShare初始化失败: {e}")
            self.isInitShare = False
            self.main.BoardCast(f"tuShare初始化失败: {e}")

    #拉取基本数据
    async def Request_Basic(self):
        if self.pro is None or not  self.isInitShare:
            print("tushare尚未初始化")
            self.main.BoardCast("tushare尚未初始化")
            return
        df = self.pro.stock_basic(
        exchange='',       # 空表示所有交易所
        list_status='L',   # L = 上市中
        fields='ts_code,symbol,name,area,industry,market,cnspell,list_date,act_name,act_ent_type,list_status')
        await asyncio.sleep(0)
        return df


    #拉取基本数据
    async def Request_Company(self, exchangeName):
        if self.pro is None:
            print("tushare尚未初始化")
            self.main.BoardCast("tushare尚未初始化")
            return
        df = self.pro.stock_company(exchange=exchangeName)
        await asyncio.sleep(0)
        return df
    




    def get_last_quarter(self, ref_date=None):
        """
        返回 (year, quarter)，表示 ref_date 的上一个季度
        """
        if ref_date is None:
            ref_date = datetime.now()

        year = ref_date.year
        month = ref_date.month

        # 当前季度（1~4）
        current_quarter = (month - 1) // 3 + 1

        if current_quarter == 1:
            return year - 1, 4
        else:
            return year - 1, current_quarter - 1



    #拉取股本数据  code的形式是xxxxxxx.SZ
    async def Request_TotalValue(self, stockCode):
        year, quarter = self.get_last_quarter()
        code = self.TuShare_to_BaoStock(stockCode)
        profit_list = []
        rs_profit = bs.query_profit_data(code=stockCode, year=year)
        while (rs_profit.error_code == '0') & rs_profit.next():
            profit_list.append(rs_profit.get_row_data())
        result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
        return result_profit


    # 拉取复权因子 code的形式是xxxxxxx.SZ
    async def Request_Adjust(self, stockCode):
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

        await asyncio.sleep(0)
        return result_factor

    #拉取日线信息StockCode为xxxxx.SZ的格式
    async def RequestDaily(self, baoStockCode : str, startData_Base, endData_Base):
        if(baoStockCode.__contains__("bj")):
            return None
        if(baoStockCode.__contains__("BJ")):
            return None
            #self.main.BoardCast("北交所的行情暂不支持:", baoStockCode)
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
            self.main.BoardCast("接口调用失败：", rs.error_msg)
            return
        while rs.next():
            data_list.append(rs.get_row_data())


        if data_list.__len__() != 0:
            df = pd.DataFrame(data_list, columns=rs.fields)
        else:
            return None

        await asyncio.sleep(0)
        return df


    def Df_To_BasicClass_TotalValue(self, dfValue):
        if dfValue is None:
            return None
        classList = []
        for _, row in dfValue.iterrows():
            testClass = BasicDBStruct.DBStructClass()
            testClass.dic[BasicDBStruct.ColumnEnum.Ts_code] = self.BaoStock_to_TuShare(row['code'])
            testClass.dic[BasicDBStruct.ColumnEnum.Total_Value] = row['totalShare']
            val = row['totalShare']
            print(f"code是{testClass.dic[BasicDBStruct.ColumnEnum.Ts_code]} 股本是：{val}")
            classList.append(testClass)
        return classList
    

    def Df_To_BasicClass(self, dfBasic, dfSZSE, dfSSE, dfBSE, df_Total):
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
        self.main.BoardCast(f"基本数据处理完毕,数据长度是:{len(alldic)}")
        self.main.BoardCast("开始单独处理深交所")

        for _,row in dfSZSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        self.main.BoardCast("开始单独处理上交所")
        for _,row in dfSSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']


        self.main.BoardCast("开始单独处理北交所")
        for _,row in dfBSE.iterrows():
            testClass = alldic.get(row['ts_code'])
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Product] = row['main_business']
                testClass.dic[BasicDBStruct.ColumnEnum.Business_Scope] = row['business_scope']
                testClass.dic[BasicDBStruct.ColumnEnum.Com_name] = row['com_name']
                testClass.dic[BasicDBStruct.ColumnEnum.Introduction] = row['introduction']

        print("开始单独处理总股本")
        self.main.BoardCast("开始单独处理总股本")
        for _,row in df_Total.iterrows():
            code = self.BaoStock_to_TuShare(row['code'])
            testClass = alldic.get(code)
            if(testClass is not None):
                testClass.dic[BasicDBStruct.ColumnEnum.Total_Value] = row['totalShare']
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

    def TuShare_to_BaoAKShare(self, dataStr):
        if(dataStr.__contains__(".")):
            num, exchange = dataStr.split(".")
            return f"{exchange.lower()}.{num}"
        else:
            return""