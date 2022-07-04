#region imports
from AlgorithmImports import *
#endregion


class GapReversalAlgo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

#拎分鐘線
        self.symbol = self.AddEquity("SPY", Resolution.Minute).Symbol

#拎兩個數既rolling windows
        self.rollingWindow = RollingWindow[TradeBar](2)
        self.Consolidate(self.symbol, Resolution.Daily, self.CustomBarHandler)
        

        #每一日做
        self.Schedule.On(self.DateRules.EveryDay(self.symbol),
                #每日收巿前15分鐘
                 self.TimeRules.AfterMarketOpen(self.symbol, 30),      
                 #買晒所有野
                 self.ExitPositions)


    def OnData(self, data):
        
        #睇下有無資料先
        if not self.rollingWindow.IsReady:
            return
        
        #9點半既bar
        if not (self.Time.hour == 9 and self.Time.minute == 31):
            return
        

        # Gap Up => Sell
        if data[self.symbol].Open >= 1.01*self.rollingWindow[0].Close:
            self.SetHoldings(self.symbol, -1)

        # Gap Down => Buy
        elif data[self.symbol].Open <= 0.99*self.rollingWindow[0].Close:
            self.SetHoldings(self.symbol, 1)

    #每日既Bar加一加佢
    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar)

    def ExitPositions(self):
        #如果唔set symbol佢會賣晒所有野
        self.Liquidate(self.symbol)