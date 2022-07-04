#選股

#region imports
from AlgorithmImports import *
#endregion
class WellDressedSkyBlueSardine(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        #
        self.rebalanceTime = datetime.min
        #睇住有咩stocks
        self.activeStocks = set()

        #加股票入黎
        self.AddUniverse(self.CoarseFilter, self.FineFilter)

        #每小時
        self.UniverseSettings.Resolution = Resolution.Hour
        

        self.portfolioTargets = []

    def CoarseFilter(self, coarse):
        # Rebalancing monthly
        #每個月做一次
        if self.Time <= self.rebalanceTime:
            return self.Universe.Unchanged
        self.rebalanceTime = self.Time + timedelta(60)

        #用資金量去選 錢多過10蚊
        
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        return [x.Symbol for x in sortedByDollarVolume if x.Price > 10
                                                and x.HasFundamentalData][:200]

    def FineFilter(self, fine):
                 #要選幾多隻股票
        selectedStocksInUniverse = self.GetParameter("number_of_selected_stock")

        #如果有數就比數, 無數就用10
        selectedStocksInUniverse = 70 if selectedStocksInUniverse is None else int(selectedStocksInUniverse)

        sortedByPE = sorted(fine, key=lambda x: x.MarketCap)
        return [x.Symbol for x in sortedByPE if x.MarketCap > 0][:selectedStocksInUniverse]

    def OnSecuritiesChanged(self, changes):
        #如果股票唔再係list, 就賣左佢
        # close positions in removed securities
        for x in changes.RemovedSecurities:
            self.Liquidate(x.Symbol)
            self.activeStocks.remove(x.Symbol)
        
        # can't open positions here since data might not be added correctly yet
        for x in changes.AddedSecurities:
            self.activeStocks.add(x.Symbol)   

        # adjust targets if universe has changed
        self.portfolioTargets = [PortfolioTarget(symbol, 1/len(self.activeStocks)) 
                            for symbol in self.activeStocks]

    def OnData(self, data):

        if self.portfolioTargets == []:
            return
        
        for symbol in self.activeStocks:
            if symbol not in data:
                return
        
        self.SetHoldings(self.portfolioTargets)
        
        self.portfolioTargets = []