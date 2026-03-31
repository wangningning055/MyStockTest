from src.main_code.Core.Request.API import RequestAPI
from src.main_code.Core.Request.API import RequestAKAPI
import src.main_code.Core.Const as const_proj
from src.main_code.Core.FileProcess import FileProcessor
from src.main_code.Core.DB import DBHandler
from src.main_code.Core import Main
import time
import os
import pandas as pd
import traceback
import asyncio
import datetime
class RequestorClass:
    def Init(self, main):
        self.api = RequestAPI.RequestAPIClass()
        self.ak_api = RequestAKAPI.RequestAPIClass()
        self.main : Main.processor = main
        self.api.init(main)
        self.isInStop = False
        self.isInRequester = False
        self.task = None

    async def RequestBasic(self):
        print("初始化tushare")
        self.api.initShare()
        if not self.api.isInitShare:
            print("tushare没有正确初始化")
            self.main.BoardCast("tushare没有正确初始化")
            return
        self.main.BoardCast("开始拉取基础数据")
        df_Basic = await self.api.Request_Basic()
        df_Company_SZSE =await self.api.Request_Company(const_proj.TradeNameSZSE)
        df_Company_SSE =await self.api.Request_Company(const_proj.TradeNameSSE)
        df_Company_BSE =await self.api.Request_Company(const_proj.TradeNameBSE)
        #df_TotalValue =await self.RequestTotalValue()
        self.main.fileProcessor.SaveCSV(df_Basic, "Base", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_SZSE, "SZSE", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_SSE, "SSE", FileProcessor.FileEnum.Basic)
        self.main.fileProcessor.SaveCSV(df_Company_BSE, "BSE", FileProcessor.FileEnum.Basic)
        #self.main.fileProcessor.SaveCSV(df_TotalValue, "TotalValue", FileProcessor.FileEnum.Basic)
        classList = self.api.Df_To_BasicClass(df_Basic, df_Company_SZSE, df_Company_SSE, df_Company_BSE)
        try:
            await self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Basic)
        except Exception as e:
            print(f"写入数据库失败: {e}")
        self.main.BoardCast("处理基础数据完成")



    async def RequestBasic_ByCSV(self):
        self.main.isInBase = True
        self.main.BoardCast("处理基础数据")
        pathBase = self.main.fileProcessor.GetCSVPath("Base", FileProcessor.FileEnum.Basic)
        path1 = self.main.fileProcessor.GetCSVPath("SZSE", FileProcessor.FileEnum.Basic)
        path2 = self.main.fileProcessor.GetCSVPath("SSE", FileProcessor.FileEnum.Basic)
        path3 = self.main.fileProcessor.GetCSVPath("BSE", FileProcessor.FileEnum.Basic)
        path4 = self.main.fileProcessor.GetCSVPath("TotalValue", FileProcessor.FileEnum.Basic)
        if not os.path.exists(pathBase):
            return None
        if not os.path.exists(path1):
            return None
        if not os.path.exists(path2):
            return None
        if not os.path.exists(path3):
            return None
        if not os.path.exists(path4):
            return None
        df_basic = pd.read_csv(pathBase)
        df_1 = pd.read_csv(path1)
        df_2 = pd.read_csv(path2)
        df_3 = pd.read_csv(path3)
        df_4 = pd.read_csv(path4)
        classList = self.api.Df_To_BasicClass(df_basic, df_1, df_2, df_3, df_4)
        self.main.BoardCast(f"基础数据长度为：{len(classList)}")

        try:
            await self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Basic)
        except Exception as e:
            full_trace = traceback.format_exc()
            print(f"写入数据库失败: {e}")
            print(f"写入数据库失败: {full_trace}")
        self.main.BoardCast("处理基础数据完成")


        

    async def RequestAdjust(self):
        self.main.BoardCast("处理复权数据")
        count_stock = 0
        dfList = []
        codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()

        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""

        sameList = set()
        logCount = 0
        progressInterval = 0
        for code in codeList:
            if self.isInStop:
                break
            progressInterval = progressInterval + 1
            if progressInterval >= const_proj.progress_interval_pull:
                self.main.SendProgress(logCount / len(codeList))
                progressInterval = 0
                await asyncio.sleep(0)

            logCount = logCount + 1
            ##测试边界
            #if logCount > 10:
            #    break
            if code in sameList:
                self.main.BoardCast("已经拉取过，跳过")
                continue

            t0 = time.perf_counter()

            df = await self.api.Request_Adjust(code)
            if df is None:
                continue
            dfList.append(df)
            self.main.fileProcessor.SaveCSV(df, code, FileProcessor.FileEnum.Adjust)

            count_stock = count_stock + 1
            t1 = time.perf_counter()
            totalCostTime = totalCostTime + (t1 - t0)
            preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
            totalCostTimeStr = self.format_seconds(totalCostTime)
            preCostTimeStr = self.format_seconds(preCostTime)
            print(f"正在通过api拉取复权数据， 当前第{count_stock}条,数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            self.main.BoardCast(f"正在通过api拉取复权数据， 当前第{count_stock}条,数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            sameList.add(code)
            #await asyncio.sleep(1)


        df_all = pd.concat(dfList, ignore_index=True)
        classList = self.api.Df_To_AdjustClass(df_all)
        if classList is None :
            return
        print("开始写入")
        try:
            await self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Adjust)
        except Exception as e:
            print(f"写入数据库失败: {e}")
            
        self.main.BoardCast("处理复权数据完成")



    async def RequestDaily(self, startData, endData):
        self.main.BoardCast("处理日线数据")
        #获取股票代码列表
        count_stock = 0
        totalCostTime = 0
        preCostTime = 0
        totalCostTimeStr = ""
        preCostTimeStr = ""

        sameList = set()
        dfList = []
        codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()

        count = 0
        progressInterval = 0
        for code in codeList:
            progressInterval = progressInterval + 1
            if progressInterval >= const_proj.progress_interval_pull:
                self.main.SendProgress(count / len(codeList))
                progressInterval = 0
                await asyncio.sleep(0)
            if self.isInStop:
                break
            count = count + 1
            ##测试边界
            #if count > 10:
            #    break

            if code in sameList:
                self.main.BoardCast("已经拉取过，跳过")
                continue
            
            t0 = time.perf_counter()

            df = await self.api.RequestDaily(code, startData, endData)
            if df is None:
                continue
            dfList.append(df)
            self.main.fileProcessor.SaveCSV(df, code, FileProcessor.FileEnum.Daily)

            count_stock = count_stock + 1
            t1 = time.perf_counter()
            totalCostTime = totalCostTime + (t1 - t0)
            preCostTime = (totalCostTime / count_stock) * (len(codeList) - count_stock)
            totalCostTimeStr = self.format_seconds(totalCostTime)
            preCostTimeStr = self.format_seconds(preCostTime)
            print(f"正在通过api拉取日线数据， 当前第{count_stock}条,时间为从{startData}  到 {endData}，数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            self.main.BoardCast(f"正在通过api拉取日线数据， 当前第{count_stock}条,时间为从{startData}  到 {endData}，数据长度为:{len(codeList)}， 已消耗时间：{totalCostTimeStr}， 预计剩余时间{preCostTimeStr}")
            sameList.add(code)
            #await asyncio.sleep(1)

        
        df_all = pd.concat(dfList, ignore_index=True)
        
        classList = self.api.Df_To_DailyClass(df_all)
        if classList is None:
            return
        await self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Daily)
        #task = asyncio.get_running_loop().create_task(self.main.dbHandler.WriteTable(classList, DBHandler.TableEnum.Daily))
        #task.add_done_callback(self.main.task_finished_callback_Daily)
        self.main.BoardCast("处理日线数据完成")

    async def RequestValue(self, dateTo):
        self.main.BoardCast("处理价值数据")
        codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()
        async def pullVal(year, quarter):
            #直接拉
            year = year
            quarter = quarter
            clsList = []
            count = 0
            progressInterval = 0
            for code in codeList:

                progressInterval = progressInterval + 1
                if progressInterval >= const_proj.progress_interval_pull:
                    self.main.SendProgress(count / len(codeList))
                    progressInterval = 0
                    await asyncio.sleep(0)

                ##测试边界
                #if count > 10:
                #    break
                if self.isInStop:
                    break
                df_Roe = await self.api.RequestValue_Roe(code, year, quarter)
                df_YOYNi = await self.api.RequestValue_YOYNi(code, year, quarter)
                df_LiabilityTo = await self.api.RequestValue_LiabilityTo(code, year, quarter)
                cls = self.api.Df_To_ValueClass(code, year, quarter, df_Roe, df_YOYNi, df_LiabilityTo)
                
                if cls is not None:
                    clsList.append(cls)
                    tempList = []
                    tempList.append(cls)
                    try:
                        await self.main.dbHandler.WriteTable(tempList, DBHandler.TableEnum.Value)
                    except Exception as e:
                        print(f"写入数据库失败: {e}")


                #self.main.fileProcessor.SaveCSV(df_Roe, f"Value_Roe_{year}_{quarter}_{code}", FileProcessor.FileEnum.Basic)
                #self.main.fileProcessor.SaveCSV(df_YOYNi, f"Value_YOYNi_{year}_{quarter}_{code}", FileProcessor.FileEnum.Basic)
                #self.main.fileProcessor.SaveCSV(df_LiabilityTo, f"Value_LiabilityTo_{year}_{quarter}_{code}", FileProcessor.FileEnum.Basic)

                print (f"正在通过api拉取价值数据， 当前第{count}条,数据长度为:{len(codeList)}, code:{code}")
                count = count + 1
                #if count > 3:
                #    break
                    #print(f"正在拉取价值数据， 当前第{count}条,数据长度为:{len(codeList)}")

            
            print(f"开始写入:长度为：{len(clsList)}")
            if clsList is not None and len(clsList) > 0:
                try:
                    await self.main.dbHandler.WriteTable(clsList, DBHandler.TableEnum.Value)
                except Exception as e:
                    print(f"写入数据库失败: {e}")

            self.main.BoardCast("处理价值数据完成")
        year, quarter, isNeedYear = self.get_report_quarter(dateTo)
        if isNeedYear:
            await pullVal(year, quarter)
            await pullVal(year - 1, 4)
        else:
            await pullVal(year, quarter)

    async def _wait_task_cancel(self):
        try:
            await self.task  # 等待任务处理取消逻辑
        except asyncio.CancelledError:
            self.main.SetIsInHandle(False)
            self.isInStop = False
            self.isInRequester = False
        finally:
            self.task = None  # 任务结束后再置空

    def StopRequest(self):
        if self.task == None:
            return
        if self.isInStop:
            return
        if self.task and not self.task.done():
            self.isInStop = True
            # 发送取消请求
            self.task.cancel()
            # 异步等待任务结束（避免直接 await，这里用 create_task 包装）
            asyncio.create_task(self._wait_task_cancel())


    def StartRequest(self, type):
        self.task = asyncio.get_running_loop().create_task(self.main.requestor.OnMsgRequestDataByType(type))
        self.task.add_done_callback(self.main.task_finished_callback)


    async def OnMsgRequestDataByType(self, type):
        if self.isInRequester or self.main.isInHandle:
            return
        self.main.SetIsInHandle(True)

        self.isInRequester = True
        self.main.calculationDataHandle.isPreheating = False
        if type == 1:
            await self.OnMsgRequestStockListData()
        if type == 2:
            await self.OnMsgRequestDailyData()
            print("日线数据拉取完毕")
        if type == 3:
            await self.OnMsgRequestAdjustData()
        if type == 4:
            await self.OnMsgRequestValueData()
        if type == 5:
            await self.OnMsgRequestAllData()

        self.isInRequester = False
        self.main.SetIsInHandle(False)
        self.main.websocketHandler.SendLastUpdateTime()

    #async def RequestTest(self):
    #    lastDateStr = self.main.recordDataCls.daily_list_last_data
    #    isNeedPull, dateFrom, dateTo = self.CheckIsNeedPull(lastDateStr)
    #    if isNeedPull:
    #        for i in range(10):
    #            if self.isInStop == True:
    #                break
    #            print(f"开始进行数据拉取{i}")
    #            await asyncio.sleep(1)
    #        self.main.recordDataCls.daily_list_last_data = dateTo
    #    else:
    #        self.main.BoardCast("是最新数据无需拉取")

    #一次性拉取数据
    async def OnMsgRequestAllData(self):
        try:

            await self.OnMsgRequestStockListData()
            await self.OnMsgRequestDailyData()
            await self.OnMsgRequestAdjustData()
            #await self.OnMsgRequestValueData()

        except Exception as e:
            self.main.SetIsInHandle(False)
            print(f"拉取失败失败: {e}")
            full_trace = traceback.format_exc()
            print(f"拉取失败失败: {full_trace}")
            self.main.BoardCast(f"拉取失败失败: {e}")



    #拉取列表数据
    async def OnMsgRequestStockListData(self):
        try:
            lastDayStr = self.main.recordDataCls.stock_list_last_data
            isNeedPull, dateFrom, dateTo = self.CheckIsNeedPull(lastDayStr)
            if isNeedPull:
                await self.RequestBasic()
                self.main.recordDataCls.stock_list_last_data = dateTo

        except Exception as e:
            self.main.SetIsInHandle(False)
            print(f"股票列表拉取失败失败，等一个小时再拉，一天只能拉五次（包括失败的次数）: {e}")
            full_trace = traceback.format_exc()
            print(f"股票列表拉取失败失败，等一个小时再拉，一天只能拉五次（包括失败的次数: {full_trace}")
            self.main.BoardCast(f"股票列表拉取失败失败，等一个小时再拉，一天只能拉五次（包括失败的次数: {e}")

    #拉取日线数据
    async def OnMsgRequestDailyData(self):
        try:
            lastDateStr = self.main.recordDataCls.daily_list_last_data
            isNeedPull, dateFrom, dateTo = self.CheckIsNeedPull(lastDateStr)
            if isNeedPull:
                await self.RequestDaily(dateFrom, dateTo)
                self.main.recordDataCls.daily_list_last_data = dateTo


        except Exception as e:
            self.main.SetIsInHandle(False)
            print(f"日线数据拉取失败失败: {e}")
            full_trace = traceback.format_exc()
            print(f"日线数据拉取失败失败: {full_trace}")
            self.main.BoardCast(f"日线数据拉取失败失败: {e}")



    #拉取复权数据
    async def OnMsgRequestAdjustData(self):
        try:
            lastDateStr = self.main.recordDataCls.adjust_list_last_data
            isNeedPull, dateFrom, dateTo = self.CheckIsNeedPull(lastDateStr)
            if isNeedPull:
                await self.RequestAdjust()
                self.main.recordDataCls.adjust_list_last_data = dateTo

        except Exception as e:
            self.main.SetIsInHandle(False)
            print(f"复权数据拉取失败失败: {e}")
            full_trace = traceback.format_exc()
            print(f"复权数据拉取失败失败: {full_trace}")
            self.main.BoardCast(f"复权数据拉取失败失败: {e}")





    #拉取价值数据
    async def OnMsgRequestValueData(self):
        try:
            lastDateStr = self.main.recordDataCls.value_list_last_data
            isNeedPull, dateFrom, dateTo = self.CheckIsNeedPull(lastDateStr)
            if isNeedPull:
                await self.RequestValue(dateTo)
                self.main.recordDataCls.value_list_last_data = dateTo


        except Exception as e:
            self.main.SetIsInHandle(False)

            print(f"价值数据拉取失败失败: {e}")
            full_trace = traceback.format_exc()
            print(f"价值数据拉取失败失败: {full_trace}")
            self.main.BoardCast(f"价值数据拉取失败失败: {e}")

    #检查是否需要拉取
    def CheckIsNeedPull(self, dataStr):
        # 获取当前的日期和时间
        now = datetime.datetime.now()
        # 定义时间分割点：19点
        cutoff_hour = 19

        # 判断当前时间是否在19点之前
        if now.hour < cutoff_hour:
            # 19点前，获取前一天的日期
            target_date = now.date() - datetime.timedelta(days=1)
        else:
            # 19点及以后，获取当天的日期
            target_date = now.date()

        today_str = target_date.strftime("%Y%m%d")

        compare_date = datetime.datetime.strptime(dataStr, "%Y%m%d").date()


        date_format = "%Y%m%d"
        original_date = datetime.datetime.strptime(dataStr, date_format)

        # 2. 计算前7天的日期
        seven_days_ago = original_date - datetime.timedelta(days=7)

        # 3. 转换回字符串格式（保持原格式）
        seven_days_ago_str = seven_days_ago.strftime(date_format)


        if compare_date < target_date:
            #print(f"需要拉取:上次日期：{dataStr}，   当日日期{today_str}")
            return True, seven_days_ago_str, today_str
        else:
            #print(f"无需拉取:上次日期：{dataStr}，   当日日期{today_str}")
            return False, seven_days_ago_str, today_str
            
    def get_report_quarter(self, date_str):
        # 1. 校验并解析日期字符串
        try:
            date = datetime.datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            raise ValueError("输入日期格式错误，请使用YYYYMMDD格式，例如20200304")
        
        # 2. 提取年、月
        year = date.year
        month = date.month
        
        # 3. 根据月份判断对应的财报年度和季度
        if 1 <= month <= 4:
            # 1-4月：返回上一年，季度3（对应上一年年报）
            report_year = year - 1
            report_quarter = 3
        elif 5 <= month <= 8:
            # 5-8月：返回当年，季度1（对应当年一季报）
            report_year = year
            report_quarter = 1
        elif 9 <= month <= 10:
            # 9-10月：返回当年，季度2（对应当年半年报）
            report_year = year
            report_quarter = 2
        elif 11 <= month <= 12:
            # 11-12月：返回当年，季度3（对应当年三季报）
            report_quarter = 3
            report_year = year
        else:
            raise ValueError("无效的月份，月份范围应为1-12")
        if  5 <= month <= 8:
            return (report_year, report_quarter, True)
        else:
            return (report_year, report_quarter, False)

    def format_seconds(self, seconds: float) -> str:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    


































    
    #async def RequestTotalValue_Ak(self):
    #    df_value =await self.api.Request_Company_Value_AK()
    #    df_info =await self.api.Request_Company_Info_AK()

    #    df_base = self.normalize_individual_info(df_value)
    #    df_base = self.rename_individual_columns(df_base)

    #    df_business = self.normalize_business_info(df_info)

    #    df_final = self.merge_company_info(df_base, df_business)
    #    df_final["code"] = "000001.SZ"

    #    self.main.fileProcessor.SaveCSV(df_value, "TotalValue_AK", FileProcessor.FileEnum.Basic)
    #    self.main.fileProcessor.SaveCSV(df_info, "TotalInfo_AK", FileProcessor.FileEnum.Basic)
    #    self.main.fileProcessor.SaveCSV(df_final, "Final_AK", FileProcessor.FileEnum.Basic)
        

    #async def RequestTotalValue(self):
    #    codeList = self.main.dbHandler.GetAllStockCodeFromBasicTable()
    #    count_stock = 0
    #    totalCostTime = 0
    #    preCostTime = 0
    #    totalCostTimeStr = ""
    #    preCostTimeStr = ""
    #    sameList = set()
    #    count = 0
    #    df_list = []
    #    for code in codeList:
    #        count = count + 1
    #        #if(count > 30):
    #        #    break
    #        if code in sameList:
    #            continue
    #        df = await self.api.Request_TotalValue(code)
    #        print(f"正在拉取股本数据，当前第{count}个")
    #        df_list.append(df)
    #        sameList.add(code)
    #    big_df = pd.concat(df_list, axis=0, ignore_index=True)
    #    return big_df
        

