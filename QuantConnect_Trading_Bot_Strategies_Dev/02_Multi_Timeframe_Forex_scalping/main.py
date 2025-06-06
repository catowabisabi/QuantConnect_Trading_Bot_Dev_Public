#region imports
from AlgorithmImports import *
#endregion
from collections import *
import math

class MulitTimeFrameForexScalping(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)    #Set Start Date
        self.SetEndDate(2017, 12, 31)      #Set End Date
        self.SetCash(10000)             #Set Strategy Cash
        
        pairs = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"]
        
        self.forexPair = "EURUSD"
        self.AddForex(self.forexPair, Resolution.Minute, Market.Oanda)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage);
        
    
        self.Consolidate(self.forexPair,timedelta(minutes=5),self.fiveMinutesBarHandler)
        self.Consolidate(self.forexPair, timedelta(minutes=60),self.sixtyMinutesBarHandler)
      
       
        self.BarHistoryWindow = 5 
        #Set up EMA indicators for lookback periods 21, 13 and 8 for both five minutes and 60 minutes time frames
        self.longLookBackPeriod = 21
        self.mediumLookBackPeriod = 13
        self.shortLookBackPeriod = 8
        
        self.percentageOfPortfolioRiskedPerTrade = 0.01
        
        self.emaFiveMinsLong = ExponentialMovingAverage(self.longLookBackPeriod)
        self.RegisterIndicator(self.forexPair, self.emaFiveMinsLong ,timedelta(minutes=5))
        self.emaFiveMinsMedium = ExponentialMovingAverage(self.mediumLookBackPeriod)
        self.RegisterIndicator(self.forexPair, self.emaFiveMinsMedium ,timedelta(minutes=5))
        self.emaFiveMinsShort = ExponentialMovingAverage(self.shortLookBackPeriod)
        self.RegisterIndicator(self.forexPair, self.emaFiveMinsShort ,timedelta(minutes=5))
        
        self.emaSixtyMinsLong = ExponentialMovingAverage(self.longLookBackPeriod)
        self.RegisterIndicator(self.forexPair, self.emaSixtyMinsLong ,timedelta(minutes=60))
        self.emaSixtyMinsShort = ExponentialMovingAverage(self.shortLookBackPeriod)
        self.RegisterIndicator(self.forexPair, self.emaSixtyMinsShort ,timedelta(minutes=60))
        
        self.historyFiveMinuteBars =   deque(maxlen=  self.BarHistoryWindow ) 
        self.historySixtyMinuteBars = deque(maxlen=  self.BarHistoryWindow ) 
        self.historyEmaSixtyMinsLong =  deque(maxlen=  self.BarHistoryWindow)
        self.historyEmaSixtyMinsShort = deque(maxlen=  self.BarHistoryWindow)
        self.historyEmaFiveMinsLong =  deque(maxlen=  self.BarHistoryWindow)
        self.historyEmaFiveMinsMedium = deque(maxlen=  self.BarHistoryWindow)
        self.historyEmaFiveMinsShort = deque(maxlen=  self.BarHistoryWindow)
        
        self.pipsAtRiskPerTrade  = 3
        self.numberOfprofitTarget1Pips = 1
        self.numberOfprofitTarget2Pips = 2
        self.pips = 0.0001
        
        self.stopBuyPrice = 0
        self.stopLossPrice = 0 
        self.profitTarget1 = 0
        self.profitTarget2  = 0
        
        self.orderSize = 100000
        
        self.entryTicket = None
        self.stoplossTicket = None
        self.profit1Ticket = None
        self.profit2Ticket = None
        
    def fiveMinutesBarHandler(self,consolidated):
        self.historyFiveMinuteBars.append(consolidated)
        self.historyEmaFiveMinsLong.append(self.emaFiveMinsLong.Current.Value)
        self.historyEmaFiveMinsMedium.append(self.emaFiveMinsMedium.Current.Value)
        self.historyEmaFiveMinsShort.append(self.emaFiveMinsShort.Current.Value)
        self.Plot("5m","5mEMA21",self.emaFiveMinsLong.Current.Value)
        self.Plot("5m","5mEMA13", self.emaFiveMinsMedium.Current.Value)
        self.Plot("5m","5mEMA8", self.emaFiveMinsShort.Current.Value)
        self.Plot("5m","EURUSD", consolidated.Close)
        if self.entryTicket == None and self.longEntrySetup() and self.longEntryTrigger():
            entryPrice = max([quoteBar.High for quoteBar in  self.historyFiveMinuteBars])
            self.stopBuyPrice = entryPrice + 0.0001*3
            self.stopLossPrice =  consolidated.Low - self.pipsAtRiskPerTrade  * self.pips
            R = self.stopBuyPrice - self.stopLossPrice
            self.profitTarget1 = self.stopBuyPrice + self.numberOfprofitTarget1Pips * R
            self.profitTarget2 = self.stopBuyPrice + self.numberOfprofitTarget2Pips * 2*R
            self.orderSize = self.CalculateOrderSize()
            self.entryTicket = self.StopMarketOrder( self.forexPair, self.orderSize, self.stopBuyPrice)
        elif self.entryTicket is not None and not self.longEntrySetup() and self.entryTicket.Status != OrderStatus.Filled:
            self.Transactions.CancelOrder(self.entryTicket.OrderId)
            self.entryTicket = None
            
    def longEntrySetup(self):
        fiveMinFannedOut =   all([x > y > z for x,y,z in zip(list(self.historyEmaFiveMinsShort),list(self.historyEmaFiveMinsMedium),list(self.historyEmaFiveMinsLong))])
        sixtyMinFannedOut =  all([x > y for x,y in zip(list(self.historyEmaSixtyMinsShort),list(self.historyEmaSixtyMinsLong))])
        prevBarsAboveShortEMA = all([x > y for x,y in zip([bar.Low for bar in list(self.historyFiveMinuteBars)[0:4]],list(self.historyEmaFiveMinsShort)[:4])])
        return fiveMinFannedOut and sixtyMinFannedOut and prevBarsAboveShortEMA
    
    def longEntryTrigger(self):
        return self.historyFiveMinuteBars[-1].Low <= self.historyEmaFiveMinsShort[-1]
    
    def CalculateOrderSize(self):
        #https://www.thebalance.com/how-to-determine-proper-position-size-when-forex-trading-1031023
        totalPortfolioValue = self.Portfolio.TotalPortfolioValue 
        amountAtRisk =  totalPortfolioValue *  self.percentageOfPortfolioRiskedPerTrade
        standardLot = 100000
        pipValueForTrade = 10
        lots =  amountAtRisk/(self.pipsAtRiskPerTrade * pipValueForTrade ) * standardLot
        rounded = math.ceil(lots / 2.) * 2
        return  rounded
    
    
    def OnOrderEvent(self, orderevent):
        if orderevent.Status != OrderStatus.Filled:
            return
        
        if self.entryTicket != None and self.entryTicket.OrderId == orderevent.OrderId:
           # Enter stop loss order
           self.stoplossTicket = self.StopMarketOrder(self.forexPair,-self.orderSize,self.stopLossPrice)
           # Enter limit order 1
           self.profit1Ticket = self.LimitOrder(self.forexPair,-self.orderSize/2,self.profitTarget1)
           # Enter limit order 2
           self.profit2Ticket = self.LimitOrder(self.forexPair,-self.orderSize/2,self.profitTarget2)
        
        if self.profit1Ticket != None and self.profit1Ticket.OrderId == orderevent.OrderId:
            self.stoplossTicket.UpdateQuantity(-self.orderSize/2)
            
        if self.stoplossTicket != None and self.stoplossTicket.OrderId == orderevent.OrderId:
            self.profit1Ticket.Cancel()
            self.profit2Ticket.Cancel()
            self.entryTicket = None
        
        if self.profit2Ticket != None and self.profit2Ticket.OrderId == orderevent.OrderId:
            self.stoplossTicket.Cancel()
            self.entryTicket = None
    
    def sixtyMinutesBarHandler(self,consolidated):
        self.historySixtyMinuteBars.append(consolidated)
        self.historyEmaSixtyMinsLong.append(self.emaSixtyMinsLong.Current.Value)
        self.historyEmaSixtyMinsShort.append(self.emaSixtyMinsShort.Current.Value)
        self.Plot("60m","EMA21",self.emaSixtyMinsLong.Current.Value)
        self.Plot("60m","EMA8", self.emaSixtyMinsShort.Current.Value)
        self.Plot("60m","EURUSD", consolidated.Close)