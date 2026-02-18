import sqlite3
import time
from enum import Enum
from src.main_code.Core.DataStruct.DB import AdjustDBStruct
from src.main_code.Core.DataStruct.DB import BasicDBStruct
from src.main_code.Core.DataStruct.DB import DailyDBStruct
from src.main_code.Core import Const as const_proj
import asyncio
from collections import defaultdict
class TableEnum(Enum):
    Basic = 1,
    Daily = 2,
    Adjust = 3,


class DBHandlerClass:

    def Init(self, main):
        self.main = main
        self.dbPath = const_proj.DBPath
        self.ConnectDb()
        self.main.BoardCast(f"链接数据库成功:{self.dbPath}")
        self.CreateTable()
        self.main.BoardCast(f"创建数据表成功:{self.dbPath}")


    #读取数据库
    def ConnectDb(self):
        self.dbConnect = sqlite3.connect(self.dbPath)
        self.dbConnect.row_factory = sqlite3.Row
        self.dbCursor = self.dbConnect.cursor()
        
    #创建数据库表
    def CreateTable(self):
        self.CreateBasicTable()
        self.CreateDailyTable()
        self.CreateAdjustTable()


   #创建基础股市表
    def CreateBasicTable(self):
        self.basicDbStruct = BasicDBStruct.DBStructClass()
        columns = []
        for key, value in self.basicDbStruct.dic.items():
            columnName = self.basicDbStruct.GetNameByEnum(key)
            dbType = self.basicDbStruct.GetDBTypeByEnum(key)
            if key == BasicDBStruct.ColumnEnum.Code:
                columns.append(f"{columnName} {dbType} PRIMARY KEY")
            else: 
                columns.append(f"{columnName} {dbType}")
        sql = f"""CREATE TABLE IF NOT EXISTS {const_proj.DBBasicTableName} (
            {', '.join(columns)}
        )"""
        self.dbCursor.execute(sql)
        self.dbConnect.commit()


    #创建复权数据表
    def CreateAdjustTable(self):
        self.adjustDbStruct = AdjustDBStruct.DBStructClass()
        columns = []

        for key in self.adjustDbStruct.dic.keys():
            columnName = self.adjustDbStruct.GetNameByEnum(key)
            dbType = self.adjustDbStruct.GetDBTypeByEnum(key)
            columns.append(f"{columnName} {dbType}")

        columns.append(f"PRIMARY KEY ({self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Code)}, {self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Date)})")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {const_proj.DBAdjustTableName} (
            {', '.join(columns)}
        )
        """
        self.dbCursor.execute(sql)
        self.dbConnect.commit()


    #创建日线股市表
    def CreateDailyTable(self):
        self.dailyDbStruct = DailyDBStruct.DBStructClass()
        columns = []

        for key in self.dailyDbStruct.dic.keys():
            columnName = self.dailyDbStruct.GetNameByEnum(key)
            dbType = self.dailyDbStruct.GetDBTypeByEnum(key)
            columns.append(f"{columnName} {dbType}")

        columns.append(f"PRIMARY KEY ({self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)}, {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)})")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {const_proj.DBDailyTableName} (
            {', '.join(columns)}
        )
        """
        self.dbCursor.execute(sql)
        self.dbConnect.commit()



    def GetTableNameByEnum(self, tableEnum):
        if tableEnum == TableEnum.Basic:
            return const_proj.DBBasicTableName
        elif tableEnum == TableEnum.Daily:
            return const_proj.DBDailyTableName
        elif tableEnum == TableEnum.Adjust:
            return const_proj.DBAdjustTableName

    #读入行
    def ReadRow(self, table_name):
        sql = f'SELECT * FROM {table_name}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        logstr = ""
        for row in allRow:
            structClass = BasicDBStruct.DBStructClass()
            for idx, key in enumerate(self.dbStruct.dic.keys()):
                dicKey = self.dbStruct.GetNameByEnum(key)
                structClass.dic[dicKey] = row[idx]
                logstr += f"key={dicKey}, val={row[idx]}, name= {self.dbStruct.GetNameByEnum(key)}, disc = {self.dbStruct.GetDiscByEnum(key)}\n"
            self.LogTxt(logstr)
            return structClass
        else:
            return None

    async def WriteTable(self, classList, table_enum):
        strhead = "正在处理"
        if table_enum == TableEnum.Basic:
            strhead = "数据库写入基本数据，"
        elif table_enum == TableEnum.Daily:
            strhead = "数据库写入日线数据，"
        elif table_enum == TableEnum.Adjust:
            strhead = "数据库写入复权数据，"
        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""
        classLen = len(classList)
        table_name = self.GetTableNameByEnum(table_enum)


        self.main.BoardCast(f"{strhead}共 {classLen} 条")

        # 获取列名（所有 structClass 结构相同，取第一个即可）
        first_row = classList[0]
        column_keys = list(first_row.dic.keys())
        columns = []
        for k in column_keys:
            name = first_row.GetNameByEnum(k)
            columns.append(f'"{name}"')
        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        sql = f'INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders})'

        # 关键：关闭自动提交，手动控制事务
        self.dbConnect.execute("BEGIN;")  # 显式开始事务

        try:
            batch_size = 10000  # 每批 1 万条（可调）
            total_written = 0

            for i in range(0, classLen, batch_size):
                batch = classList[i:i + batch_size]
                values_list = []

                for data in batch:
                    # 构造值元组
                    vals = tuple(data.dic.get(k) for k in column_keys)
                    values_list.append(vals)

                # 批量插入
                self.dbCursor.executemany(sql, values_list)
                total_written += len(batch)

                # 每批广播一次进度（避免太频繁）
                if total_written % batch_size == 0 or total_written == classLen:
                    progress = total_written
                    # 简化时间估算（因为现在速度极快，预估意义不大，可只显示进度）
                    msg = f"{strhead}已写入 {progress}/{classLen} 条"
                    #await self.main.BoardCast(msg)
                    print(msg)

                # 让出控制权，避免阻塞事件循环
                await asyncio.sleep(0)

            # 提交整个事务
            self.dbConnect.commit()
            self.main.BoardCast(f"{strhead}写入完成！共 {classLen} 条")

        except Exception as e:
            self.dbConnect.rollback()
            await self.main.BoardCast(f"写入失败: {e}")
            raise



        #logCount = 0
        #for data in classList:
        #    t0 = time.perf_counter()
        #    count_stock = count_stock + 1

        #    self.WriteRow(data, table_enum)
        #    t1 = time.perf_counter()

        #    totalCostTime = totalCostTime + (t1 - t0)
        #    preCostTime = (totalCostTime / count_stock) * (len(classList) - count_stock)
        #    totalCostTimeStr = self.format_seconds(totalCostTime)
        #    preCostTimeStr = self.format_seconds(preCostTime)
        #    if(logCount > 100):
        #        self.main.BoardCast(f"{str}当前第{count_stock}条,数据长度为:{classLen}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
        #        logCount = 0
        #    logCount = logCount + 1
        #    print(f"{str}当前第{count_stock}条,数据长度为:{classLen}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
        #    await asyncio.sleep(0)

    #写入行
    def WriteRow(self, structClass, table_enum):
        table_name = self.GetTableNameByEnum(table_enum)
        rowDic = structClass.dic
        columns = []
        values = []
        for k, val in rowDic.items():
            name = structClass.GetNameByEnum(k)
            columns.append(f'"{name}"')
            values.append(str(val))
        
        columns_sql = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(values))
        sql = f'INSERT OR REPLACE INTO {table_name} ({columns_sql}) VALUES ({placeholders})'

        self.dbCursor.execute(sql, tuple(values))
        self.dbConnect.commit()

    def GetAllStockCodeFromBasicTable(self):
        sql = f'SELECT {self.basicDbStruct.GetNameByEnum(BasicDBStruct.ColumnEnum.Ts_code)} FROM {const_proj.DBBasicTableName}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        sameList = set()
        codeList = []
        for row in allRow:
            if(row[0] in sameList):
                continue
            codeList.append(row[0])
            sameList.add(row[0])
        return codeList
    
    def GetAllBasicData(self):
        sql = f'SELECT * FROM {const_proj.DBBasicTableName}'
        self.dbCursor.execute(sql)
        allRow = self.dbCursor.fetchall()
        columns = [desc[0] for desc in self.dbCursor.description]
        sameList = set()
        codeList = {}
        for row in allRow:
            row_dict = {col: row[i] for i, col in enumerate(columns)}
            ts_code:str = row[0]
            if(ts_code in sameList):
                continue
            stateName = self.basicDbStruct.GetNameByEnum(BasicDBStruct.ColumnEnum.List_Status)
            if(row_dict[stateName] != "L"):
                print(f"这是是退市的股票：{ts_code}")
                continue
            if(ts_code.lower().endswith("bj")):
                continue
            
            rowDic = dict(row)
            codeList[ts_code] = rowDic
            #sameList.add(ts_code)
        return codeList
    
    #def GetAllDailyData(self):
    #    sql = f"SELECT * FROM {const_proj.DBDailyTableName}"
    #    self.dbCursor.execute(sql)
    #    # 先拿列名
    #    columns = [desc[0] for desc in self.dbCursor.description]
    #    # 准备结果字典
    #    data_dict = {}
    #    for row in self.dbCursor.fetchall():   # row 是 tuple
    #        row_dict = {col: row[i] for i, col in enumerate(columns)}
    #        codeColumStr = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)
    #        dateColumnStr = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)
    #        key = (row_dict[codeColumStr], row_dict[dateColumnStr])  # 双主键 tuple
    #        data_dict[key] = row_dict
    #    #data_dict.__len__()
    #    return data_dict
    
    #def GetAllAdjustData(self):
    #    sql = f"SELECT * FROM {const_proj.DBAdjustTableName}"
    #    self.dbCursor.execute(sql)
    #    # 先拿列名
    #    columns = [desc[0] for desc in self.dbCursor.description]
    #    # 准备结果字典
    #    data_dict = {}
    #    for row in self.dbCursor.fetchall():   # row 是 tuple
    #        row_dict = {col: row[i] for i, col in enumerate(columns)}
    #        codeColumStr = self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Code)
    #        dateColumnStr = self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Date)
    #        key = (row_dict[codeColumStr], row_dict[dateColumnStr])  # 双主键 tuple
    #        data_dict[key] = row_dict

    #    return data_dict
    
    async def GetAllDailyData(self):
        count_sql = f"SELECT COUNT(*) FROM {const_proj.DBDailyTableName}"
        self.dbCursor.execute(count_sql)
        total_count = self.dbCursor.fetchone()[0]
        sql = f"""
        SELECT *
        FROM {const_proj.DBDailyTableName}
        ORDER BY
            {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)},
            {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)}
        """
        self.dbCursor.execute(sql)

        # 列名
        columns = [desc[0] for desc in self.dbCursor.description]

        # 外层 code，内层 date
        data_dict = defaultdict(dict)

        code_col = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)
        date_col = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)
        count = 0
        countSend = 0
        for row in self.dbCursor:   # ❗ 不用 fetchall
            count = count + 1
            countSend = countSend + 1
            if count > 10000:
                break


            row_dict = dict(zip(columns, row))

            code = row_dict[code_col]
            trade_date = row_dict[date_col]

            data_dict[code][trade_date] = row_dict

            percentage = count * 100 / total_count
            formatted = round(percentage, 2) 
            if(countSend > 1000):
                self.main.BoardCast(f"{count}读入中，共 {total_count} 条， 已读取：{formatted}% ")
                countSend = 0
            print(f"{count}读入中，共 {total_count} 条， 已读取：{formatted}%")
            await asyncio.sleep(0)

        return data_dict
    

    def GetAllDailyDataNoWait(self):
        count_sql = f"SELECT COUNT(*) FROM {const_proj.DBDailyTableName}"
        self.dbCursor.execute(count_sql)
        total_count = self.dbCursor.fetchone()[0]
        sql = f"""
        SELECT *
        FROM {const_proj.DBDailyTableName}
        ORDER BY
            {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)},
            {self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)}
        """
        self.dbCursor.execute(sql)

        # 列名
        columns = [desc[0] for desc in self.dbCursor.description]

        # 外层 code，内层 date
        data_dict = defaultdict(dict)

        code_col = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)
        date_col = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)
        count = 0
        countSend = 0
        for row in self.dbCursor:   # ❗ 不用 fetchall
            count = count + 1
            countSend = countSend + 1
            if count > 10000:
                break


            row_dict = dict(zip(columns, row))

            code = row_dict[code_col]
            trade_date = row_dict[date_col]

            data_dict[code][trade_date] = row_dict

            percentage = count * 100 / total_count
            formatted = round(percentage, 2) 
            if(countSend > 1000):
                self.main.BoardCast(f"{count}读入中，共 {total_count} 条， 已读取：{formatted}% ")
                countSend = 0
            print(f"{count}读入中，共 {total_count} 条， 已读取：{formatted}%")
        return data_dict

    def format_seconds(self, seconds: float) -> str:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    

    # ==================== 高效单行查询方法 ====================
    
    def GetBasicRowByCode(self, code):
        """
        按股票代码查询Basic表中的一行数据
        
        Args:
            code (str): 股票代码，例如 "600000" 或 "000001"
            
        Returns:
            dict or None: 返回一个字典，键为列名(str)，值为对应的数据
                          例如: {'ts_code': '600000.SH', 'code': '600000', 'name': '浦发银行', ...}
                          如果未找到则返回 None
                          
        Usage:
            row = db_handler.GetBasicRowByCode("600000")
            if row:
                print(row['name'])  # 打印股票名称
                print(row['industry'])  # 打印所属行业
        """
        column_name = self.basicDbStruct.GetNameByEnum(BasicDBStruct.ColumnEnum.Code)
        sql = f'SELECT * FROM {const_proj.DBBasicTableName} WHERE {column_name} = ?'
        self.dbCursor.execute(sql, (code,))
        row = self.dbCursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    
    def GetDailyRowByCodeAndDate(self, code, date):
        """
        按股票代码和交易日期查询Daily表中的一行数据（双主键查询）
        
        Args:
            code (str): 股票代码，例如 "600000.SH" 或 "000001.SZ"
            date (str): 交易日期，格式为 "YYYYMMDD"，例如 "20240115"
            
        Returns:
            dict or None: 返回一个字典，键为列名(str)，值为对应的数据
                          例如: {'ts_code': '600000.SH', 'trade_date': '20240115', 'open': 10.5, ...}
                          如果未找到则返回 None
                          
        Usage:
            row = db_handler.GetDailyRowByCodeAndDate("600000.SH", "20240115")
            if row:
                print(row['close'])  # 打印收盘价
                print(row['open'])  # 打印开盘价
                print(row['amount'])  # 打印成交量
                high_price = float(row['high'])  # 类型转换
        """
        code_column = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Code)
        date_column = self.dailyDbStruct.GetNameByEnum(DailyDBStruct.ColumnEnum.Date)
        
        sql = f'''SELECT * FROM {const_proj.DBDailyTableName} 
                  WHERE {code_column} = ? AND {date_column} = ?'''
        self.dbCursor.execute(sql, (code, date))
        row = self.dbCursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    
    def GetAdjustRowByCodeAndDate(self, code, date):
            """
            按股票代码查询在指定日期或之前的最新复权因子数据
            
            说明：由于复权数据不连续（只在有除权除息事件时才有数据），
            本方法返回小于等于指定日期的最新复权数据。
            例如：查询 2023-08-09，会返回 2023-06-14 的复权因子。
            
            Args:
                code (str): 股票代码，例如 "000001.SZ" 或 "600000.SH"
                date (str): 查询日期，格式为 "YYYY-MM-DD"，例如 "2023-08-09" 或 "YYYYMMDD"，例如 "20230809"
                
            Returns:
                dict or None: 返回一个字典，键为列名(str)，值为对应的数据
                            例如: {'Code': '000001.SZ', 'Date': '2023-06-14', 
                                    'For_Adjust': 0.867238, 'Back_Adjust': 104.876880}
                            如果未找到则返回 None
                            
            Usage:
                row = db_handler.GetAdjustRowByCodeAndDate("000001.SZ", "2023-08-09")
                if row:
                    for_adjust = float(row['For_Adjust'])      # 前复权因子
                    back_adjust = float(row['Back_Adjust'])    # 后复权因子
                    adjust_date = row['Date']                  # 实际的复权日期
                    print(f"使用 {adjust_date} 的复权因子: {for_adjust}")
            """
            # 处理日期格式：支持 "YYYYMMDD" 和 "YYYY-MM-DD" 两种格式
            if len(date) == 8 and date.isdigit():
                # "20230809" 转换为 "2023-08-09"
                date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
            
            code_column = self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Code)
            date_column = self.adjustDbStruct.GetNameByEnum(AdjustDBStruct.ColumnEnum.Date)
            
            # 查询 <= 指定日期的最新复权数据
            sql = f'''SELECT * FROM {const_proj.DBAdjustTableName} 
                    WHERE {code_column} = ? AND {date_column} <= ?
                    ORDER BY {date_column} DESC
                    LIMIT 1'''
            self.dbCursor.execute(sql, (code, date))
            row = self.dbCursor.fetchone()
            
            if row:
                return dict(row)
            
            return {"Open_Price" : 1}