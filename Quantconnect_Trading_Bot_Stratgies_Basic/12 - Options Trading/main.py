#region imports
from AlgorithmImports import *
#endregion

class BreakoutCallBuy(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        #想買既期權
        equity = self.AddEquity("MSFT", Resolution.Minute)

        #
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw)

        ##
        self.equity = equity.Symbol
        self.SetBenchmark(self.equity)
        
        #加返D option Data入黎
        option = self.AddOption("MSFT", Resolution.Minute)

        # 期權時間段
        option.SetFilter(-3, 3, timedelta(20), timedelta(40))

        # 21 日高位
        self.high = self.MAX(self.equity, 21, Resolution.Daily, Field.High)
    
    
    def OnData(self,data):

        # 高價個個位做左未?
        if not self.high.IsReady:
            return
        
        # check有無開住options
        option_invested = [x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
        

        #如果有
        if option_invested:

            #如果太近打巴, 就賣左佢
            if self.Time + timedelta(4) > option_invested[0].ID.Date:
                self.Liquidate(option_invested[0], "Too close to expiration")
            return
        
        #如果過左21高點
        if self.Securities[self.equity].Price >= self.high.Current.Value:

            #買多, 但我唔知語快係乜
            for i in data.OptionChains:
                #拎到宜家個數值, 一個一個咁去拎直到拎到最近個個, 就係咁咁過左高點最新個個
                chains = i.Value
                self.BuyCall(chains)

 
    def BuyCall(self,chains):

        #排日期先
        expiry = sorted(chains,key = lambda x: x.Expiry, reverse=True)[0].Expiry

        #唔要Call option 
        calls = [i for i in chains if i.Expiry == expiry and i.Right == OptionRight.Call]

        #拎返我地個underlying price去搵可以買既單 -3 3樓上
        call_contracts = sorted(calls,key = lambda x: abs(x.Strike - x.UnderlyingLastPrice))


        if len(call_contracts) == 0: 
            return
            #買第一張contract
        self.call = call_contracts[0]
        
        #買5%
        quantity = self.Portfolio.TotalPortfolioValue / self.call.AskPrice
        quantity = int( 0.05 * quantity / 100 )
        self.Buy(self.call.Symbol, quantity)


    def OnOrderEvent(self, orderEvent):

        #呢個係一個orderEvent Class
        #
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        if order.Type == OrderType.OptionExercise:
            self.Liquidate()