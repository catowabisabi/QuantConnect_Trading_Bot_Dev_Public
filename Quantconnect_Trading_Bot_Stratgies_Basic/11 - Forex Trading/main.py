#region imports
from AlgorithmImports import *
#endregion
from System.Drawing import Color

class ForexBollingerBandBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        #EURUSD / Market
        self.pair = self.AddForex("EURUSD", Resolution.Daily, Market.Oanda).Symbol

        # BB 數值
        self.bb = self.BB(self.pair, 20, 2)
        
        # 畫圖
        stockPlot = Chart('Trade Plot')
        stockPlot.AddSeries(Series('Buy', SeriesType.Scatter, '$', 
                            Color.Green, ScatterMarkerSymbol.Triangle))
        stockPlot.AddSeries(Series('Sell', SeriesType.Scatter, '$', 
                            Color.Red, ScatterMarkerSymbol.TriangleDown))
        stockPlot.AddSeries(Series('Liquidate', SeriesType.Scatter, '$', 
                            Color.Blue, ScatterMarkerSymbol.Diamond))
        self.AddChart(stockPlot)

    def OnData(self, data):

        # BB 可以用就去
        if not self.bb.IsReady:
            return
        
        #宜家既數值
        price = data[self.pair].Price
        
        self.Plot("Trade Plot", "Price", price)
        self.Plot("Trade Plot", "MiddleBand", self.bb.MiddleBand.Current.Value)
        self.Plot("Trade Plot", "UpperBand", self.bb.UpperBand.Current.Value)
        self.Plot("Trade Plot", "LowerBand", self.bb.LowerBand.Current.Value)
        

        #宜家有無野係手
        if not self.Portfolio.Invested:

            #低過BB low就買
            if self.bb.LowerBand.Current.Value > price:
                self.SetHoldings(self.pair, 1)
                self.Plot("Trade Plot", "Buy", price)

            #高過BB high就賣
            elif self.bb.UpperBand.Current.Value < price:
                self.SetHoldings(self.pair, -1)
                self.Plot("Trade Plot", "Sell", price)
        #如果有野係手
        else:

            #如果做緊多, 
            if self.Portfolio[self.pair].IsLong:
                #而過左中線, 就賣晒佢
                if self.bb.MiddleBand.Current.Value < price:
                    self.Liquidate()
                    self.Plot("Trade Plot", "Liquidate", price)


            elif self.bb.MiddleBand.Current.Value > price:
                self.Liquidate()    
                self.Plot("Trade Plot", "Liquidate", price)

