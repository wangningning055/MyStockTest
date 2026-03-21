class BaseClass:
    id : int
    stockCode : str             #票子代码
    stockPartId : int           #所处的分仓仓位id
    startDate : str             #开仓日期
    endDate : str               #清仓日期
    isEnd : bool                #是否清仓

    #开仓价
    start_oriPrice_avg : float
    start_oriPrice_open : float
    start_oriPrice_close : float
    start_oriPrice_high : float
    start_oriPrice_low : float

    start_adjPrice_avg : float
    start_adjPrice_open : float
    start_adjPrice_close : float
    start_adjPrice_high : float
    start_adjPrice_low : float

    #清仓价
    end_oriPrice_avg : float
    end_oriPrice_open : float
    end_oriPrice_close : float
    end_oriPrice_high : float
    end_oriPrice_low : float

    end_adjPrice_avg : float
    end_adjPrice_open : float
    end_adjPrice_close : float
    end_adjPrice_high : float
    end_adjPrice_low : float



    def __init__(self):
        pass