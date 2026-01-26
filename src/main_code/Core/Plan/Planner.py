from .PlanStruct import PlaneClass
class PlannerClass:
    
    def Init(self):
        self.timer = Timer()
        self.planeList  = []
        

    def AddPlane(self, plane):
        self.planeList.append(plane)

    def UpdatePlane(self):
        #print("更新心跳")
        for v in self.planeList:
            v.Check()



class Timer:
    def Init(self):
        self.counter = 0
        self.CallBackList = {}

    def AddFunc(self, callBack):
        self.CallBackList[self.counter] = callBack
        self.counter = self.counter + 1
        return self.counter - 1

    
    def RemoveFunc(self, id):
        self.CallBackList[id] = None



    def Update(self):
        for _, v in self.CallBackList:
            if v is not None:
                v()