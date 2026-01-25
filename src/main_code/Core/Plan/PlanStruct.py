from enum import Enum
from datetime import datetime, date
class PlanEnum(Enum):
    Daily = 1,      #每天更新一次
    Monthly = 2,    #每月更新一次
    Year = 3,       #每年更新一次

    Second = 4,
    Minute = 5,
    Hour = 6,

class PlaneClass:
    def InitPlane(self, callBack, enum:PlanEnum, data):
        self.callBack = callBack
        self.planEnum = enum
        if self.planEnum == PlanEnum.Daily:
            self.data = datetime.strptime(data, "%H:%M:%S").time()
        elif self.planEnum == PlanEnum.Monthly:
            self.data = data

        self.lastExecDate = None


    def Check(self):
        if self.planEnum == PlanEnum.Daily:
            now = datetime.now()
            today = date.today()
            if self.lastExecDate == today:
                return
            if(now.time() >= self.data):
                self.lastExecDate = today
                self.Execute()
        elif self.planEnum == PlanEnum.Monthly:
            if datetime.today().date == self.data:
                self.Execute()


    def Execute(self):
        if self.callBack is not None :
            self.callBack()