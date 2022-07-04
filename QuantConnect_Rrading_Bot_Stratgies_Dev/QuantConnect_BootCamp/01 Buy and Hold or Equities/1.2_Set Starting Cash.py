class BootCampTask(QCAlgorithm):

    def Initialize(self):
        
        self.AddEquity("SPY", Resolution.Daily)
        
        # 1. Set Starting Cash 
        
    def OnData(self, data):
        pass
